from rest_framework import routers

from realty.viewsets import ClientViewSet, DealViewSet, RealtyViewSet, TypeLayoutViewSet, TypeMaterialViewSet, \
    TypePaymentViewSet, TypeRealtyViewSet

router = routers.DefaultRouter()

router.register(r'clients', ClientViewSet)
router.register(r'deals', DealViewSet)
router.register(r'realties', RealtyViewSet)
router.register(r'type_layouts', TypeLayoutViewSet)
router.register(r'type_materials', TypeMaterialViewSet)
router.register(r'type_payments', TypePaymentViewSet)
router.register(r'type_realties', TypeRealtyViewSet)

urlpatterns = [
    *router.urls,
]
