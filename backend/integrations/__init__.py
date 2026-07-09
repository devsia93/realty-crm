"""External-integration seams for realty-crm.

Each provider lives behind a Gateway interface defined here so application code
depends on the interface, never on a concrete client, and tests inject fakes.
See `calendar.py` (task 050, Phase 2 step 2).
"""
