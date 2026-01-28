from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AchievementViewSet, ArtifactViewSet, StudentYearlyAwardViewSet

router = DefaultRouter()
router.register(r'awards', AchievementViewSet)  # Legacy - Achievement model
router.register(r'yearly-awards', StudentYearlyAwardViewSet)  # New - StudentYearlyAward model
router.register(r'artifacts', ArtifactViewSet)

urlpatterns = [
    path('', include(router.urls)),
]