"""Worker password-hashing characterization (Phase 2, step 2 / task 050).

``Worker`` used to override ``AbstractUser.password`` with a plaintext
``CharField``. Task 050 deletes that override, so AbstractUser's hashed-password
machinery (``set_password`` / ``check_password`` / ``make_password``) owns the
column. These tests pin the resulting contract:

* the manager's ``create_user`` hashes (raw string NOT stored, ``check_password``
  works, the stored value is a recognized Django hash format);
* ``WorkerFactory`` no longer stores the default raw password — it routes
  through ``set_password`` — and both the default and an overridden password
  authenticate correctly;
* ``set_password`` round-trips on a ``Worker`` instance (AbstractBaseUser
  machinery is active on the model).

No Google / no network. No commits (FILE-EDIT-ONLY).
"""
import pytest
from django.contrib.auth.hashers import identify_hasher

from company.models import Worker
from tests.factories import WorkerFactory


def _is_hashed(value: str) -> bool:
    try:
        identify_hasher(value)
        return True
    except ValueError:
        return False


@pytest.mark.django_db
def test_create_user_hashes_password():
    # last_name is NOT NULL on Worker (CharField without blank=True), and email
    # is passed explicitly to avoid any None-vs-empty coercion ambiguity; both
    # are forwarded via create_user's **extra_fields.
    w = Worker.objects.create_user(
        username="alice",
        email="alice@example.com",
        password="s3cret-pw",
        last_name="A",
    )
    stored = Worker.objects.get(pk=w.pk).password

    assert stored != "s3cret-pw"              # raw string is NOT stored
    assert _is_hashed(stored)                  # stored value is a real hash format
    assert w.check_password("s3cret-pw")      # hashing round-trips
    assert not w.check_password("wrong-pw")   # wrong password rejected


@pytest.mark.django_db
def test_set_password_roundtrips_on_worker():
    w = WorkerFactory()
    w.set_password("rotated-pw")
    w.save(update_fields=["password"])

    assert Worker.objects.get(pk=w.pk).password != "rotated-pw"
    assert w.check_password("rotated-pw")
    assert not w.check_password("pass-12345")


@pytest.mark.django_db
def test_factory_default_password_is_hashed_and_authenticates():
    w = WorkerFactory()
    stored = Worker.objects.get(pk=w.pk).password

    assert stored != "pass-12345"             # factory no longer stores the raw default
    assert _is_hashed(stored)
    assert w.check_password("pass-12345")     # default still authenticates


@pytest.mark.django_db
def test_factory_custom_password_is_hashed():
    w = WorkerFactory(password="custom-pw")
    stored = Worker.objects.get(pk=w.pk).password

    assert stored != "custom-pw"
    assert _is_hashed(stored)
    assert w.check_password("custom-pw")
    assert not w.check_password("pass-12345")
