import pytest
import tests.factories as f
import inspect
import factory as fb

factories = [c for _, c in inspect.getmembers(f, inspect.isclass)
             if issubclass(c, fb.django.DjangoModelFactory) and c is not fb.django.DjangoModelFactory]

@pytest.mark.django_db
@pytest.mark.parametrize("factory_cls", factories, ids=lambda c: c.__name__)
def test_factory_creates(factory_cls):
    obj = factory_cls()
    assert obj.pk is not None
