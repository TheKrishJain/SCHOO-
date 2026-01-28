from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GatePassViewSet
from .views_approval import approve_gatepass, reject_gatepass, pending_gatepasses

router = DefaultRouter()
router.register(r'passes', GatePassViewSet)

urlpatterns = [
    path('pending/', pending_gatepasses, name='pending_gatepasses'),
    path('<uuid:gatepass_id>/approve/', approve_gatepass, name='approve_gatepass'),
    path('<uuid:gatepass_id>/reject/', reject_gatepass, name='reject_gatepass'),
    path('', include(router.urls)),
]