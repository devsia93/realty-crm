"""Characterization tests for Deal.save() -- Phase 1, step 2. FILE-EDIT-ONLY.

Pinned save() contract (backend/realty/models/deal.py):

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        worker = self.realty.owner.worker   # 3-hop reach: Deal.realty -> Realty.owner -> Client.worker
        if worker:                          # truthy Worker instance -> assign; None/falsy -> skip
            self.main_worker = worker
        super().save()                      # called with NO args, so force_insert/force_update/
                                            # using/update_fields are ALL ignored (full save always)

Reach chain nullability:
    Deal.realty      FK -> Realty   null=True  (on_delete=SET_NULL)
    Realty.owner     FK -> Client   null=True  (on_delete=CASCADE)
    Client.worker    FK -> Worker   null=True  (on_delete=SET_NULL)
    Deal.main_worker FK -> Worker   null=True, editable=False  (auto-set by save())

Net behavior pinned here:
  - On every save() (insert AND update) main_worker is (re)assigned to
    realty.owner.worker when that worker is truthy, OVERWRITING any value the
    caller put on deal.main_worker.
  - When realty.owner.worker is None, save() SKIPS assignment (main_worker is
    left as-is) and still persists the row -- no crash.
  - When realty is None        -> None.owner   -> AttributeError.
    When realty.owner is None   -> None.worker  -> AttributeError.  (FIXME(behavior))
  - amount / amount_commission / type_payment are NOT touched by save() (no
    derivation/defaulting there); commission decimal fields default to 0 at
    the CustomDecimalField level, not in save().

Factories come from tests/factories.py (task 046). Deal.save() forces the
realty -> owner -> worker chain, so DealFactory wires it by default. The two
crash cases use DealFactory.build() to obtain an UNSAVED Deal (build() never
persists the main instance, so save() crashes on the call rather than at
factory-creation time). The other pre-save-control cases re-save an existing
Deal, because save() has no adding-guard and behaves identically on insert
and update -- this also avoids depending on factory_boy's SubFactory strategy.
"""
from decimal import Decimal

import pytest
from django.db import models

import tests.factories as f
from realty.models import Deal


@pytest.mark.django_db
def test_main_worker_auto_assigned_from_realty_owner_worker_on_create():
    # Happy path (case 1): a Deal whose realty -> owner -> worker chain is
    # complete gets main_worker auto-assigned from exactly that worker, and the
    # assigned value is what is persisted to the DB.
    deal = f.DealFactory()
    expected_worker = deal.realty.owner.worker_id

    deal.refresh_from_db()

    assert deal.main_worker_id is not None
    assert deal.main_worker_id == expected_worker
    assert deal.main_worker_id == deal.realty.owner.worker_id


@pytest.mark.django_db
def test_save_overwrites_explicitly_set_main_worker():
    # Explicit main_worker (case 2): save() runs `if worker: self.main_worker =
    # worker` whenever realty.owner.worker is truthy, so a caller-supplied
    # main_worker is OVERWRITTEN, not kept. Shown on a re-save: a value stamped
    # onto an existing Deal is clobbered back to realty.owner.worker. (save() has
    # no adding-guard, so this overwrite is identical on first insert.)
    deal = f.DealFactory()                       # saved; main_worker = realty.owner.worker
    chain_worker = deal.realty.owner.worker_id
    explicit = f.WorkerFactory()
    assert explicit.pk != chain_worker

    deal.main_worker = explicit                  # caller sets an explicit different worker
    deal.save()                                  # save() re-runs -> overwrites with chain worker
    deal.refresh_from_db()

    assert deal.main_worker_id == chain_worker
    assert deal.main_worker_id != explicit.pk    # caller's value was clobbered


@pytest.mark.django_db
def test_save_raises_attribute_error_when_realty_owner_is_none():
    # Broken chain, owner missing (case 3): Realty.owner is None ->
    # `None.worker` -> AttributeError. Deal is never persisted.
    # FIXME(behavior): unhandled None owner -- Phase 2 turns this into ValidationError (owner-approved)
    realty = f.RealtyFactory(owner=None)
    deal = f.DealFactory.build(realty=realty)
    assert realty.owner is None

    with pytest.raises(AttributeError):
        deal.save()

    assert deal.pk is None


@pytest.mark.django_db
def test_main_worker_reassigned_on_update():
    # Deal update (case 4): save() has no `self._state.adding` / `if not self.pk`
    # guard, so the auto-assignment re-runs on every save -- including updates
    # of an already-persisted row.
    deal = f.DealFactory()
    old_main_worker = deal.main_worker_id
    realty2 = f.RealtyFactory()  # new owner (Client) -> new worker
    new_worker = realty2.owner.worker_id
    assert new_worker != old_main_worker

    deal.realty = realty2
    deal.save()
    deal.refresh_from_db()

    assert deal.main_worker_id == new_worker  # re-assigned on update
    assert deal.main_worker_id != old_main_worker


@pytest.mark.django_db
def test_main_worker_kept_when_owner_worker_is_none():
    # Falsy-worker branch of `if worker:`: owner is present but owner.worker is
    # None, so save() SKIPS assignment (no crash) and a caller-supplied
    # main_worker is RETAINED rather than cleared or overwritten. The insert
    # itself also succeeds with main_worker=None (same skip), proving owner=None
    # (crash) vs owner.worker=None (silent None) are genuinely different paths.
    owner = f.ClientFactory(worker=None)
    realty = f.RealtyFactory(owner=owner)
    assert realty.owner.worker is None

    deal = f.DealFactory(realty=realty)          # insert: owner.worker None -> skip -> main_worker None
    assert deal.main_worker_id is None

    explicit = f.WorkerFactory()
    deal.main_worker = explicit
    deal.save()                                  # update: still skipped -> main_worker retained
    deal.refresh_from_db()

    assert deal.main_worker_id == explicit.pk    # retained, not cleared/overwritten


@pytest.mark.django_db
def test_save_does_not_derive_or_default_commission_or_payment_fields():
    # Commission / payment-type fields (case 5): save() touches ONLY
    # main_worker. amount, amount_commission and type_payment are neither
    # defaulted nor derived inside save(); their persisted values equal the
    # in-memory values passed in. The commission default=0 is a field-level
    # CustomDecimalField trait, not a save() side effect.
    tp = f.TypePaymentFactory(title="Cash")
    deal = f.DealFactory(
        amount=Decimal("123456.78"),
        amount_commission=Decimal("987.65"),
        type_payment=tp,
    )
    deal.refresh_from_db()

    assert deal.amount == Decimal("123456.78")
    assert deal.amount_commission == Decimal("987.65")
    assert deal.type_payment_id == tp.pk

    # Field-level traits (not save() behavior), pinned alongside for context.
    assert Deal._meta.get_field("amount").default == 0
    assert Deal._meta.get_field("amount_commission").default == 0
    assert Deal._meta.get_field("type_payment").remote_field.on_delete is models.PROTECT


@pytest.mark.django_db
def test_save_ignores_update_fields_kwarg():
    # save()'s `update_fields` (and force_insert/force_update/using) are
    # dropped: it calls `super().save()` with NO args, so a partial update
    # requested via update_fields still performs a FULL save. Proven by
    # main_worker being rewritten even though only ["amount"] was requested.
    deal = f.DealFactory()
    realty2 = f.RealtyFactory()
    new_worker = realty2.owner.worker_id
    assert new_worker != deal.main_worker_id

    deal.realty = realty2
    deal.amount = Decimal("123456.00")
    deal.save(update_fields=["amount"])  # update_fields should exclude main_worker...
    deal.refresh_from_db()

    assert deal.amount == Decimal("123456.00")
    assert deal.main_worker_id == new_worker  # ...yet main_worker was still written -> kwarg ignored


@pytest.mark.django_db
def test_main_worker_field_is_non_editable():
    # main_worker is editable=False, which is why the auto-assignment in save()
    # is the only way it gets populated -- forms/admin cannot set it. Pin that
    # metadata so a Phase 2 move of the logic cannot silently drop the guard.
    assert Deal._meta.get_field("main_worker").editable is False
    assert Deal._meta.get_field("main_worker").null is True


@pytest.mark.django_db
def test_save_raises_attribute_error_when_realty_is_none():
    # The other crash path: Deal.realty is None -> `None.owner` ->
    # AttributeError (the reach blows up one hop earlier than the owner=None
    # case). Deal.realty is nullable, so this state is reachable.
    # FIXME(behavior): unhandled None realty -- Phase 2 turns this into ValidationError
    deal = f.DealFactory.build(realty=None)
    assert deal.realty is None

    with pytest.raises(AttributeError):
        deal.save()

    assert deal.pk is None
