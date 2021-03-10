from rest_framework import routers

from company.viewsets import ChildViewSet, TaskViewSet, WorkerViewSet

router = routers.DefaultRouter()

router.register(r'kids', ChildViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'workers', WorkerViewSet)

urlpatterns = [
    *router.urls,
]
