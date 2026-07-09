"""Service layer for Deal writes (Phase 2, step 1).

Extracts the main_worker auto-assignment that used to live in Deal.save()
(realty/models/deal.py) into explicit use-case functions, and turns the
previously unhandled AttributeError on an incomplete owner chain into a
django.core.exceptions.ValidationError -- the owner-sanctioned fix per
REFACTOR_PROMPT section 5 ("explicit handling of missing owner (ValidationError,
not AttributeError)") and section 93 (pre-authorized fixes ONLY: Deal owner
ValidationError).

Original Deal.save() logic, ported verbatim:

    worker = self.realty.owner.worker   # Deal.realty -> Realty.owner -> Client.worker
    if worker:                          # truthy -> assign; falsy -> skip (preserved)
        self.main_worker = worker

The two hops that used to crash with AttributeError -- `realty is None`
(``None.owner``) and `realty.owner is None` (``None.worker``) -- now raise
ValidationError("realty owner has no assigned worker") instead. The falsy-worker
branch (owner present but owner.worker is None) is preserved as-is: assignment is
silently skipped and main_worker is left untouched, matching the prior behavior
exactly. Turning that silent-None path into a ValidationError is NOT part of
this sanctioned fix and would need its own owner decision.
"""
from django.core.exceptions import ValidationError

from realty.models import Deal


_OWNER_CHAIN_INCOMPLETE = "realty owner has no assigned worker"


def _assign_main_worker(deal: Deal) -> None:
    """Port of Deal.save()'s auto-assignment, with crash paths -> ValidationError.

    Assigns deal.main_worker from deal.realty.owner.worker whenever that worker
    is truthy (overwriting any caller-supplied value, exactly as the old save()
    did, since the assignment is unconditional). Raises ValidationError when the
    owner chain is incomplete (realty or owner is None) instead of the former
    AttributeError, and does so BEFORE the row is written. The falsy-worker
    branch (owner present, owner.worker is None) is preserved: no raise, no
    assignment, main_worker left as-is.
    """
    realty = deal.realty
    if realty is None:
        raise ValidationError(_OWNER_CHAIN_INCOMPLETE)
    owner = realty.owner
    if owner is None:
        raise ValidationError(_OWNER_CHAIN_INCOMPLETE)
    worker = owner.worker
    if worker:
        deal.main_worker = worker


def create_deal(**fields) -> Deal:
    """Create and persist a Deal, auto-assigning main_worker from the owner chain.

    Mirrors the old Deal.save() ordering: resolve/assign main_worker BEFORE the
    row is written. Raises ValidationError on an incomplete owner chain; no row
    is persisted in that case (assignment runs before save()).
    """
    deal = Deal(**fields)
    _assign_main_worker(deal)
    deal.save()
    return deal


def update_deal(deal: Deal, **fields) -> Deal:
    """Apply field updates to an existing Deal and re-run the auto-assignment.

    The assignment re-runs on every update (the old save() had no
    ``self._state.adding`` / ``if not self.pk`` guard), so changing deal.realty
    re-points main_worker to the new owner chain. Raises ValidationError if the
    resulting owner chain is incomplete.
    """
    for attr, value in fields.items():
        setattr(deal, attr, value)
    _assign_main_worker(deal)
    deal.save()
    return deal
