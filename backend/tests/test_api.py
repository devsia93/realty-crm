"""Characterization tests for every registered realty-crm API route.

Phase 1, step 3 (task 048). FILE-EDIT-ONLY: writes ONLY this file. No src
changes. No commits.

# Route inventory (enumerated -- do NOT assume; smarthouse taught urls can be
# empty -- here they are NOT)
Source: backend/app/urls.py + included urlconfs.

    admin/                 -> django.contrib.admin (out of scope: not a DRF route)

    api/v1/company/        company/urls.py  -- routers.DefaultRouter()
        kids/    -> company.viewsets.ChildViewSet   (ModelViewSet)
        tasks/   -> company.viewsets.TaskViewSet
        workers/ -> company.viewsets.WorkerViewSet

    api/v1/realty/         realty/urls.py   -- routers.DefaultRouter()
        clients/        -> realty.viewsets.ClientViewSet
        deals/          -> realty.viewsets.DealViewSet
        realties/       -> realty.viewsets.RealtyViewSet
        type_layouts/   -> realty.viewsets.TypeLayoutViewSet
        type_materials/ -> realty.viewsets.TypeMaterialViewSet
        type_payments/  -> realty.viewsets.TypePaymentViewSet
        type_realties/  -> realty.viewsets.TypeRealtyViewSet

DefaultRouter also exposes a root view at each prefix (/api/v1/company/ ,
/api/v1/realty/) listing registered basenames -> 200.

Could write CRUD for all 10 -> NOT the smarthouse-empty branch; step 3
instructs full CRUD characterization here.

# Auth surface (DRF settings audit)
app/settings.py defines NO `REST_FRAMEWORK` dict -> no DEFAULT_PERMISSION_CLASSES
/ DEFAULT_AUTHENTICATION_CLASSES overrides. Every viewset sets
authentication_classes = (TokenAuthentication,) and NO permission_classes ->
DRF falls back to the APView default permission_classes = [AllowAny].
=> ANONYMOUS requests PASS (200 on read, 201 on write). Pinned below; Phase 3
security work is expected to break these pins intentionally.

# Serializer field-key snapshot (the API contract pin)
Every serializer is `Meta.fields = '__all__'`, so each response object's
top-level key set == the model's concrete field names (+ forward M2M names for
Worker's groups/user_permissions), with FKs serialized as PKs EXCEPT
ClientSerializer.worker which is a NESTED WorkerSerializer (still keyed `worker`
-- only its VALUE shape differs, not the key set).
We pin each response's key set against `model._meta.concrete_fields | .many_to_many`
so that ANY Phase 2/3 change to the serializer's field scope (e.g. dropping
`password`, listing explicit fields, adding a SerializerMethodField) fails this
test -- the contract pin. Source-derived (not execution-captured); host confirms
on first run.

# Deal-specific API create (Phase 2: routed through services)
DealViewSet.create -> DealSerializer.create -> realty.services.create_deal ports
the old Deal.save() main_worker reach-through (realty.owner.worker). Deal.realty
is null=True at model & serializer level, so DRF ACCEPTS a create payload without
realty -- but create_deal now raises django ValidationError on the incomplete
owner chain, which the serializer converts to a DRF ValidationError -> HTTP 400
(was an uncaught AttributeError / 500). The bogus-FK 400s below are unaffected:
those fail at serializer.is_valid() (PrimaryKeyRelatedField), before the service.

Factories from tests/factories.py (task 046). The realty->owner->worker chain is
wired by DealFactory by default.
"""
import uuid

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.test import APIClient

import tests.factories as f
from company.models import Child, Task, Worker
from company.viewsets import ChildViewSet, TaskViewSet, WorkerViewSet
from realty.models import (
    Client,
    Deal,
    Realty,
    TypeLayout,
    TypeMaterial,
    TypePayment,
    TypeRealty,
)
from realty.viewsets import (
    ClientViewSet,
    DealViewSet,
    RealtyViewSet,
    TypeLayoutViewSet,
    TypeMaterialViewSet,
    TypePaymentViewSet,
    TypeRealtyViewSet,
)


def _url(suffix: str) -> str:
    return f"/api/v1/{suffix}"


def _model_keyset(model) -> set:
    # Exact set of keys a plain `Meta.fields='__all__'` ModelSerializer emits.
    # concrete_fields covers id + every real column (FKs included, named by attr);
    # many_to_many covers forward M2M (Worker.groups / Worker.user_permissions).
    return {fld.name for fld in model._meta.concrete_fields} | {
        fld.name for fld in model._meta.many_to_many
    }


# (url suffix, model, factory attr on tests.factories) -- 10 registered routes.
ROUTES = [
    ("company/kids/", Child, "ChildFactory"),
    ("company/tasks/", Task, "TaskFactory"),
    ("company/workers/", Worker, "WorkerFactory"),
    ("realty/clients/", Client, "ClientFactory"),
    ("realty/deals/", Deal, "DealFactory"),
    ("realty/realties/", Realty, "RealtyFactory"),
    ("realty/type_layouts/", TypeLayout, "TypeLayoutFactory"),
    ("realty/type_materials/", TypeMaterial, "TypeMaterialFactory"),
    ("realty/type_payments/", TypePayment, "TypePaymentFactory"),
    ("realty/type_realties/", TypeRealty, "TypeRealtyFactory"),
]


# Minimal-valid create payloads for the 9 non-Deal routes (Deal is handled
# separately because of the FileField + Deal.save() reach-through). Each FK
# given as a PK to an existing factory object; nullable FKs omitted -> null.
# Client intentionally omits `worker` (ClientSerializer.worker is a NESTED
# writable WorkerSerializer, so it must NOT be sent as a PK; the FK is nullable
# so omitting is the valid minimal path -> worker=None).
def _u() -> str:
    return uuid.uuid4().hex[:8]


CREATE_CASES = [
    ("company/kids/", Child, lambda: {"name": f"k{_u()}", "sex": 1, "worker": f.WorkerFactory().pk}),
    ("company/tasks/", Task, lambda: {"text": f"t{_u()}", "date_start": "2026-01-01", "date_end": "2026-01-02", "worker": f.WorkerFactory().pk}),
    ("company/workers/", Worker, lambda: {"username": f"u{_u()}", "password": "p", "last_name": "L"}),
    ("realty/clients/", Client, lambda: {"fio": f"c{_u()}"}),
    ("realty/realties/", Realty, lambda: {"address": f"a{_u()}", "count_rooms": 3, "price": "100.00", "type_deal": 1}),
    ("realty/type_layouts/", TypeLayout, lambda: {"title": f"l{_u()}"}),
    ("realty/type_materials/", TypeMaterial, lambda: {"title": f"m{_u()}"}),
    ("realty/type_payments/", TypePayment, lambda: {"title": f"p{_u()}"}),
    ("realty/type_realties/", TypeRealty, lambda: {"title": f"r{_u()}"}),
]


VIEWSETS = (
    ChildViewSet, TaskViewSet, WorkerViewSet,
    ClientViewSet, DealViewSet, RealtyViewSet,
    TypeLayoutViewSet, TypeMaterialViewSet, TypePaymentViewSet, TypeRealtyViewSet,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "suffix,model,factory_name",
    ROUTES,
    ids=[s for s, _, _ in ROUTES],
)
def test_list_returns_200_and_field_key_snapshot(suffix, model, factory_name):
    obj = getattr(f, factory_name)()
    resp = APIClient().get(_url(suffix))
    assert resp.status_code == 200, (suffix, resp.status_code)
    data = resp.json()
    assert isinstance(data, list) and len(data) >= 1
    expected = _model_keyset(model)
    assert set(data[0].keys()) == expected, (
        f"{suffix} list keys {sorted(data[0].keys())} != expected {sorted(expected)}"
    )
    assert obj.pk in {item["id"] for item in data}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "suffix,model,factory_name",
    ROUTES,
    ids=[s for s, _, _ in ROUTES],
)
def test_retrieve_returns_200_and_field_key_snapshot(suffix, model, factory_name):
    obj = getattr(f, factory_name)()
    resp = APIClient().get(f"{_url(suffix)}{obj.pk}/")
    assert resp.status_code == 200, (suffix, resp.status_code)
    body = resp.json()
    expected = _model_keyset(model)
    assert set(body.keys()) == expected, (
        f"{suffix} retrieve keys {sorted(body.keys())} != expected {sorted(expected)}"
    )
    assert body["id"] == obj.pk


@pytest.mark.django_db
@pytest.mark.parametrize(
    "suffix,model,payload_fn",
    CREATE_CASES,
    ids=[c[0] for c in CREATE_CASES],
)
def test_create_minimal_valid_payload_status_and_db_effect(suffix, model, payload_fn):
    payload = payload_fn()
    before = model.objects.count()
    resp = APIClient().post(_url(suffix), payload, format="json")
    assert resp.status_code == 201, (suffix, resp.status_code, resp.content[:300])
    assert model.objects.count() == before + 1


@pytest.mark.django_db
def test_deal_create_runs_save_auto_assign_through_api():
    # The Deal create API routes through services.create_deal, which ports the
    # old Deal.save() main_worker reach-through (realty.owner.worker): a valid
    # POST with a realty whose owner.worker chain is set yields 201 AND the
    # persisted Deal.main_worker == realty.owner.worker.
    realty = f.RealtyFactory()
    tp = f.TypePaymentFactory()
    before = Deal.objects.count()
    resp = APIClient().post(
        _url("realty/deals/"),
        {
            "realty": realty.pk,
            "type_payment": tp.pk,
            "amount": "100.00",
            "amount_commission": "10.00",
            "agreement": SimpleUploadedFile("ag.txt", b"deal bytes"),
        },
        format="multipart",
    )
    assert resp.status_code == 201, (resp.status_code, resp.content[:300])
    assert Deal.objects.count() == before + 1
    new_deal = Deal.objects.order_by("-pk").first()
    assert new_deal.main_worker_id == realty.owner.worker_id


@pytest.mark.django_db
def test_deal_create_without_realty_returns_400():
    # Phase 2: Deal.realty is nullable, so DRF still ACCEPTS a no-realty payload,
    # but the create now routes through services.create_deal, which raises
    # ValidationError on the incomplete owner chain -> DRF answers 400 (was an
    # uncaught AttributeError / HTTP 500). Nothing is persisted.
    tp = f.TypePaymentFactory()
    before = Deal.objects.count()
    resp = APIClient().post(
        _url("realty/deals/"),
        {"type_payment": tp.pk, "amount": "1.00", "agreement": SimpleUploadedFile("a.txt", b"x")},
        format="multipart",
    )
    assert resp.status_code == 400, (resp.status_code, resp.content[:300])
    assert Deal.objects.count() == before


@pytest.mark.django_db
def test_bogus_fk_create_realty_app_returns_400():
    # one bogus-FK create per app (realty): Realty.owner -> non-existent PK.
    # DRF PrimaryKeyRelatedField validation rejects it before save -> 400.
    resp = APIClient().post(
        _url("realty/realties/"),
        {"address": "x", "count_rooms": 1, "price": "1.00", "owner": 999_999},
        format="json",
    )
    assert resp.status_code == 400, (resp.status_code, resp.content[:200])


@pytest.mark.django_db
def test_bogus_fk_create_company_app_returns_400():
    # one bogus-FK create per app (company): Task.worker -> non-existent PK.
    resp = APIClient().post(
        _url("company/tasks/"),
        {"text": "x", "date_start": "2026-01-01", "date_end": "2026-01-02", "worker": 999_999},
        format="json",
    )
    assert resp.status_code == 400, (resp.status_code, resp.content[:200])


@pytest.mark.django_db
def test_anonymous_list_passes_open_api():
    # No Authorization header -> still 200 (AllowAny default, nothing requires
    # the Token). Phase 3 is expected to flip this to 401/403 intentionally.
    f.RealtyFactory()
    resp = APIClient().get(_url("realty/realties/"))
    assert resp.status_code == 200


@pytest.mark.django_db
def test_anonymous_create_passes_open_api():
    before = TypeLayout.objects.count()
    resp = APIClient().post(_url("realty/type_layouts/"), {"title": f"anon{_u()}"}, format="json")
    assert resp.status_code == 201
    assert TypeLayout.objects.count() == before + 1


def test_viewsets_use_token_auth_and_allowany_permissions():
    # Config pin: every viewset sets authentication_classes=(TokenAuthentication,)
    # and none sets permission_classes -> inherited [AllowAny]. This is WHY the
    # anonymous tests above pass. Phase 3 adding permissions will fail this pin
    # on purpose -- update it intentionally then.
    for viewset in VIEWSETS:
        assert any(issubclass(a, TokenAuthentication) for a in viewset.authentication_classes), viewset
        assert any(issubclass(p, AllowAny) for p in viewset.permission_classes), viewset


@pytest.mark.django_db
def test_default_router_root_view_realty():
    resp = APIClient().get("/api/v1/realty/")
    assert resp.status_code == 200
    assert "deals" in resp.json()  # DefaultRouter root maps basename -> url


@pytest.mark.django_db
def test_default_router_root_view_company():
    resp = APIClient().get("/api/v1/company/")
    assert resp.status_code == 200
    assert "workers" in resp.json()
