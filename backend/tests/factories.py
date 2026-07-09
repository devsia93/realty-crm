"""factory_boy factories for every realty-crm model.

Task 046 (Phase 1, step 1). FILE-EDIT-ONLY.
Sources: backend/company/models/{worker,task,child}.py
         backend/realty/models/{client,realty,deal,type_*}.py

FK dependency graph (as discovered in the model files):

    Worker (company.Worker; AbstractUser subclass)          -- root, no FK
    TypeLayout / TypeMaterial / TypeRealty / TypePayment    -- roots, title-only

    Client  --worker (FK, nullable)-->  Worker
    Realty  --owner   (FK, nullable)-->  Client --worker--> Worker
            |--type_layout  (nullable)--> TypeLayout
            |--type_material(nullable)--> TypeMaterial
            `--type_realty  (nullable)--> TypeRealty
    Deal    --realty (FK, null=True but Deal.save() walks realty.owner.worker)--> Realty --> Client --> Worker
            |--client (FK, nullable)--> Client
            |--type_payment (FK, on_delete=PROTECT, NOT NULL)--> TypePayment
            |--main_worker (FK, editable=False)--> Auto-set in save() from realty.owner.worker
            `--sub_worker (FK, nullable)--> Worker
            (agreement = FileField, required: no null/blank)
    Task    --worker (FK, nullable)--> Worker
            --deal   (FK, nullable)--> Deal  (left None by default; pass TaskFactory(deal=DealFactory()))
    Child   --worker (FK, nullable)--> Worker

Caveat: Deal.save() executes `worker = self.realty.owner.worker`, so a *creatable* Deal
requires realty -> owner -> worker to be populated. DealFactory wires that full chain
by default. (The owner-missing crash path is intentional legacy behavior to be pinned
by tests in a later task; it is deliberately not reproduced here.)
"""
from datetime import date
from decimal import Decimal

import factory
from factory.django import DjangoModelFactory, FileField

from company.models import Child, Task, Worker
from realty.models import (
    Client,
    Deal,
    Realty,
    TypeLayout,
    TypeMaterial,
    TypePayment,
    TypeRealty,
)


class WorkerFactory(DjangoModelFactory):
    class Meta:
        model = Worker

    username = factory.Sequence(lambda n: f"worker{n}")
    password = "pass-12345"
    email = factory.Sequence(lambda n: f"worker{n}@example.com")
    first_name = "Firstname"
    last_name = "Lastname"
    is_active = True


class TypeLayoutFactory(DjangoModelFactory):
    class Meta:
        model = TypeLayout

    title = factory.Sequence(lambda n: f"Layout {n}")


class TypeMaterialFactory(DjangoModelFactory):
    class Meta:
        model = TypeMaterial

    title = factory.Sequence(lambda n: f"Material {n}")


class TypeRealtyFactory(DjangoModelFactory):
    class Meta:
        model = TypeRealty

    title = factory.Sequence(lambda n: f"Realty type {n}")


class TypePaymentFactory(DjangoModelFactory):
    class Meta:
        model = TypePayment

    title = factory.Sequence(lambda n: f"Payment {n}")


class ClientFactory(DjangoModelFactory):
    class Meta:
        model = Client

    fio = factory.Sequence(lambda n: f"Client {n}")
    worker = factory.SubFactory(WorkerFactory)


class RealtyFactory(DjangoModelFactory):
    class Meta:
        model = Realty

    address = factory.Sequence(lambda n: f"Address {n}")
    price = Decimal("1000000.00")
    count_rooms = 2
    floor = 1
    floors = 1
    type_deal = Realty.DEAL.SALE
    status = True
    owner = factory.SubFactory(ClientFactory)
    type_layout = factory.SubFactory(TypeLayoutFactory)
    type_material = factory.SubFactory(TypeMaterialFactory)
    type_realty = factory.SubFactory(TypeRealtyFactory)


class DealFactory(DjangoModelFactory):
    class Meta:
        model = Deal

    realty = factory.SubFactory(RealtyFactory)
    client = factory.SubFactory(ClientFactory)
    type_payment = factory.SubFactory(TypePaymentFactory)
    amount = Decimal("500000.00")
    amount_commission = Decimal("50000.00")
    agreement = FileField(data=b"agreement content", filename="agreement.txt")
    # main_worker is editable=False and auto-assigned by Deal.save() from
    # realty.owner.worker; never set it here.


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task

    text = factory.Sequence(lambda n: f"Task {n}")
    date_start = factory.LazyFunction(date.today)
    date_end = factory.LazyFunction(date.today)
    worker = factory.SubFactory(WorkerFactory)
    # deal is nullable; left None by default. Provide with TaskFactory(deal=DealFactory()).


class ChildFactory(DjangoModelFactory):
    class Meta:
        model = Child

    name = factory.Sequence(lambda n: f"Child {n}")
    worker = factory.SubFactory(WorkerFactory)
