# realty-crm

A real-estate agency CRM backend: properties (sale/rent, layouts, materials,
types), clients and their deals, agency staff and tasks. REST API built with
Django + DRF; token-authenticated staff model based on Django's auth.

**Stack:** Django 5.1 · DRF 3.15 · PostgreSQL 16 · Python 3.12 · Docker

## Quick start

```bash
cp example.env .env
docker compose up        # API on :8000 under /api/v1/
./test.sh                # 63-test suite in Docker
./test.sh -k deal        # pytest filter
```

## Domain & API

Two apps behind versioned routers:

| Prefix | App | Resources |
| --- | --- | --- |
| `/api/v1/realty/` | realty | realties, deals, clients, type dictionaries (layout / material / payment / realty) |
| `/api/v1/company/` | company | workers, tasks, kids |

Key business rule: creating or updating a **Deal** auto-assigns the responsible
`main_worker` from the property owner's chain — implemented in
`realty/services.py` (a broken owner chain is a `ValidationError`, not a crash).

## Architecture notes

- **Services layer**: deal mutations live in `realty/services.py`; models hold data
  and simple invariants only.
- **Worker security**: `Worker` extends `AbstractUser` properly — passwords are
  hashed by Django's auth machinery (a legacy plaintext override was removed with
  a data migration wrapping existing values).
- **Integrations seam**: `backend/integrations/calendar.py` defines a
  `CalendarGateway` (with a no-op default); the Google Calendar quickstart lives in
  `scripts/` with its own requirements file, out of the app's dependency tree.
- **Tests**: 63 characterization-first tests — factory_boy factories for all 10
  models, `Deal.save()` behavior pins, serializer field-key snapshots for every
  route, auth surface, bogus-FK handling.

## History

The committed repo never ran from a clean clone (broken Dockerfile base image,
missing app migrations). It was restored test-first: environment fixed, missing
migrations generated, 63 tests written against actual behavior, business logic
extracted to services, passwords secured, then Django 3.1 → 4.2 → 5.1.
