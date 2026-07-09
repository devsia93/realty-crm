"""Google Calendar gateway seam (Phase 2, step 2 / task 050).

Why this exists
---------------
The repository's ONLY Google Calendar code was the standalone `quickstart.py`
diagnostic at the repo root. It is now relocated to
`scripts/google_calendar_quickstart.py` with a docstring. A grep of the backend
(`grep -rn google backend/`) returns NO matches, i.e. NO application code
imports or calls Google. So nothing is wired through this gateway yet.

This module provides the *seam* so that when a service eventually needs calendar
data it depends on `CalendarGateway`, never on `googleapiclient`, and tests can
inject a fake / null object instead of calling Google (the REFACTOR_PROMPT
forbids hitting Google from tests). A concrete `GoogleCalendarGateway` is
intentionally NOT implemented here: with no call site, it would be untested dead
code. Add it (and a settings-driven factory) when the first consumer appears.

Patterns: Gateway (interface) + Null Object (NullCalendarGateway, the safe
application default that never touches the network and never raises).
"""
from __future__ import annotations

from typing import List, Protocol, runtime_checkable


@runtime_checkable
class CalendarGateway(Protocol):
    """Read access to a user's calendar events.

    Implementations talk to an external provider (Google Calendar). Call sites
    depend on THIS interface, so the provider can be swapped or faked in tests
    without touching service code.
    """

    def list_upcoming_events(self, max_results: int = 10) -> List[dict]:
        """Return up to ``max_results`` upcoming events as plain dicts.

        Each dict minimally carries ``start`` (ISO 8601 string) and ``summary``
        (string), matching the shape historically printed by
        ``scripts/google_calendar_quickstart.py``.
        """
        ...


class NullCalendarGateway:
    """No-op gateway. The application default until a provider is wired.

    Returns an empty result set, so services that depend on a ``CalendarGateway``
    keep working with no external dependency configured. Never raises, never
    contacts the network. This is the Null Object pattern.
    """

    def list_upcoming_events(self, max_results: int = 10) -> List[dict]:
        return []


def get_calendar_gateway() -> CalendarGateway:
    """Return the gateway the app should use.

    Returns :class:`NullCalendarGateway` until a real provider is wired in
    (guarded by a future setting/secret). Call sites should resolve this through
    dependency injection so tests can substitute a fake.
    """
    return NullCalendarGateway()
