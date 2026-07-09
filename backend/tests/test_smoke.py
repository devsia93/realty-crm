import pytest

from company.models import Worker


@pytest.mark.django_db
def test_worker_model_saves():
    w = Worker.objects.create(username="tw", password="x", first_name="Test", last_name="Worker")
    assert Worker.objects.get(pk=w.pk).username == "tw"
