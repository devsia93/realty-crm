"""Characterization tests for the Deal write service -- Phase 2, step 1.

Phase 1 (task 047) pinned Deal.save()'s buried main_worker auto-assignment:

    def save(self, ...):
        worker = self.realty.owner.worker   # Deal.realty -> Realty.owner -> Client.worker
        if worker:                          # truthy -> assign; falsy -> skip
            self.main_worker = worker
        super().save()                      # called with NO args (update_fields dropped)

Phase 2 moves that logic OUT of the model into realty/services.create_deal /
update_deal, and turns the two unhandled AttributeError crash paths into
django.core.exceptions.ValidationError (owner-sanctioned fix, REFACTOR_PROMPT
section 5/93). Deal.save() is now Django's plain default model save.

Reach chain nullability (unchanged):
    Deal.realty      FK -> Realty   null=True  (on_delete=SET_NULL)
    Realty.owner     FK -> Client   null=True  (on_delete=CASCADE)
    Client.worker    FK -> Worker   null=True  (on_delete=SET_NULL)
    Deal.main_worker FK -> Worker   null=True, editable=False  (now set only by the service)

Net behavior pinned here (service contract):
  - create_deal/update_deal (re)assign main_worker to realty.owner.worker when
    that worker is truthy, OVERWRITING any caller-supplied value -- the
    assignment is unconditional and re-runs on every update (no adding-guard),
    exactly as the old save() did.
  - When owner.worker is None, assignment is SKIPPED (no raise, no crash): the
    row persists and a caller-supplied main_worker is RETAINED. This falsy-worker
    branch is preserved verbatim (NOT part of the sanctioned fix).
  - When realty is None or realty.owner is None (the old AttributeError crashes)
    the service raises ValidationError("realty owner has no assigned worker")
    BEFORE save(), so nothing is persisted.
  - amount / amount_commission / type_payment are NOT touched by the service.
  - Plain Deal.objects.create() / Deal.save() NO LONGER auto-assign main_worker
    (the logic moved) -- pinned explicitly below.

Factories from tests/factories.py (task 046). DealFactory still wires the full
realty -> owner -> worker chain (harmless now that save() no longer needs it).
ValidationError cases call create_deal directly; the assignment runs before
save(), so no Deal row is written.
"""
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models

import tests.factories as f
from realty import services
from realty.models import Deal


def _deal_fields(**overrides):
    """Minimal valid Deal field set for services.create_deal / Deal.objects.create.

    realty -> owner -> worker is complete by default (RealtyFactory wires it).
    """
    base = {
        "realty": f.RealtyFactory(),
        "type_payment": f.TypePaymentFactory(),
        "amount": Decimal("500000.00"),
        "amount_commission": Decimal("50000.00"),
        "agreement": SimpleUploadedFile("agreement.txt", b"agreement content"),
    }
    base.update(overrides)
    return base


@pytest.mark.django_db
def test_main_worker_auto_assigned_from_realty_owner_worker_on_create():
    # Case 1 (happy path), now via the service: create_deal ports save()'s
    # `if worker: main_worker = worker` and assigns BEFORE persisting, so the
    # chained worker is what is stored.
    realty = f.RealtyFactory()
    deal = services.create_deal(**_deal_fields(realty=realty))

    deal.refresh_from_db()

    assert deal.main_worker_id is not None
    assert deal.main_worker_id == realty.owner.worker_id


@pytest.mark.django_db
def test_create_deal_overwrites_explicitly_set_main_worker():
    # Case 2: the assignment runs unconditionally whenever the chain worker is
    # truthy, so a caller-supplied main_worker is CLOBBERED, not kept. The
    # service has no adding-guard, so this is identical on create and update.
    realty = f.RealtyFactory()
    explicit = f.WorkerFactory()
    assert explicit.pk != realty.owner.worker_id

    deal = services.create_deal(**_deal_fields(realty=realty, main_worker=explicit))
    deal.refresh_from_db()

    assert deal.main_worker_id == realty.owner.worker_id
    assert deal.main_worker_id != explicit.pk


@pytest.mark.django_db
def test_create_deal_raises_validation_error_when_realty_owner_is_none():
    # Case 3 (was the AttributeError pin): Realty.owner is None -> the owner
    # chain is incomplete. The service raises ValidationError (owner-approved
    # Phase 2 fix) INSTEAD of the old ``None.worker`` AttributeError, and before
    # save(), so nothing is persisted.
    realty = f.RealtyFactory(owner=None)
    assert realty.owner is None

    with pytest.raises(ValidationError, match="realty owner has no assigned worker"):
        services.create_deal(realty=realty)

    assert not Deal.objects.exists()


@pytest.mark.django_db
def test_main_worker_reassigned_on_update():
    # Case 4: update_deal re-runs the assignment on every call (no adding-guard),
    # so moving a Deal to a new realty re-points main_worker to the new chain.
    realty1 = f.RealtyFactory()
    deal = services.create_deal(**_deal_fields(realty=realty1))
    old_main_worker = deal.main_worker_id

    realty2 = f.RealtyFactory()
    new_worker = realty2.owner.worker_id
    assert new_worker != old_main_worker

    deal = services.update_deal(deal, realty=realty2)
    deal.refresh_from_db()

    assert deal.main_worker_id == new_worker
    assert deal.main_worker_id != old_main_worker


@pytest.mark.django_db
def test_main_worker_kept_when_owner_worker_is_none():
    # Case 5a (falsy-worker branch, preserved verbatim): owner is present but
    # owner.worker is None, so ``if worker:`` is False -> assignment SKIPPED, no
    # ValidationError, row persists, and a caller-supplied main_worker is
    # RETAINED rather than cleared or overwritten. This is the distinct
    # silent-None path vs. the owner=None ValidationError path.
    owner = f.ClientFactory(worker=None)
    realty = f.RealtyFactory(owner=owner)
    assert realty.owner.worker is None

    deal = services.create_deal(**_deal_fields(realty=realty))
    assert deal.main_worker_id is None

    explicit = f.WorkerFactory()
    deal = services.update_deal(deal, main_worker=explicit)
    deal.refresh_from_db()

    assert deal.main_worker_id == explicit.pk


@pytest.mark.django_db
def test_create_deal_does_not_derive_or_default_commission_or_payment_fields():
    # Case 5: the service touches ONLY main_worker. amount, amount_commission
    # and type_payment are neither defaulted nor derived; their persisted values
    # equal what was passed. The commission default=0 is a field-level
    # CustomDecimalField trait, not a service side effect.
    tp = f.TypePaymentFactory(title="Cash")
    deal = services.create_deal(**_deal_fields(
        type_payment=tp,
        amount=Decimal("123456.78"),
        amount_commission=Decimal("987.65"),
    ))
    deal.refresh_from_db()

    assert deal.amount == Decimal("123456.78")
    assert deal.amount_commission == Decimal("987.65")
    assert deal.type_payment_id == tp.pk

    # Field-level traits (not service behavior), pinned alongside for context.
    assert Deal._meta.get_field("amount").default == 0
    assert Deal._meta.get_field("amount_commission").default == 0
    assert Deal._meta.get_field("type_payment").remote_field.on_delete is models.PROTECT


@pytest.mark.django_db
def test_save_respects_update_fields_kwarg():
    # Case 7 RE-PINNED for Phase 2: the save() override that called
    # ``super().save()`` with NO args (dropping update_fields) is GONE -- the
    # auto-assignment moved to the service, and Deal.save() is now Django's plain
    # default, which HONORS update_fields. A partial save touching only
    # ["amount"] therefore leaves realty / main_worker at their prior values
    # (main_worker is also no longer touched by save() at all).
    deal = services.create_deal(**_deal_fields())
    old_realty = deal.realty_id
    old_main_worker = deal.main_worker_id
    assert old_main_worker is not None

    realty2 = f.RealtyFactory()
    deal.realty = realty2
    deal.amount = Decimal("123456.00")
    deal.save(update_fields=["amount"])  # plain default save -> partial
    deal.refresh_from_db()

    assert deal.amount == Decimal("123456.00")
    assert deal.realty_id == old_realty              # not in update_fields -> not written
    assert deal.main_worker_id == old_main_worker    # not in update_fields + logic moved


@pytest.mark.django_db
def test_main_worker_field_is_non_editable():
    # main_worker is editable=False, so forms/admin/serializer cannot set it;
    # only the service (create_deal/update_deal) populates it now. Pin the
    # metadata so the logic cannot silently drift back into the model.
    assert Deal._meta.get_field("main_worker").editable is False
    assert Deal._meta.get_field("main_worker").null is True


@pytest.mark.django_db
def test_create_deal_raises_validation_error_when_realty_is_none():
    # Case 9 (was the other AttributeError pin): Deal.realty is None -> the owner
    # chain is incomplete one hop earlier. The service raises ValidationError
    # (owner-approved Phase 2 fix) instead of the old ``None.owner``
    # AttributeError, before save(), so nothing is persisted.
    with pytest.raises(ValidationError, match="realty owner has no assigned worker"):
        services.create_deal(realty=None)

    assert not Deal.objects.exists()


@pytest.mark.django_db
def test_plain_orm_create_no_longer_auto_assigns_main_worker():
    # NEW Phase 2 pin: the auto-assignment moved OUT of Deal.save() into
    # services.create_deal. Plain Deal.objects.create() therefore no longer
    # auto-sets main_worker even when the realty -> owner -> worker chain is
    # complete -- pin the new reality so the logic cannot drift back into the
    # model.
    realty = f.RealtyFactory()  # complete owner -> worker chain
    deal = Deal.objects.create(
        realty=realty,
        type_payment=f.TypePaymentFactory(),
        amount=Decimal("500000.00"),
        amount_commission=Decimal("50000.00"),
        agreement=SimpleUploadedFile("a.txt", b"x"),
    )
    deal.refresh_from_db()

    assert deal.main_worker_id is None
