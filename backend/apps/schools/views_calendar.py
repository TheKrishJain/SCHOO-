from rest_framework import viewsets, permissions
from .models_calendar import Holiday, SchoolEvent
from .serializers_calendar import HolidaySerializer, SchoolEventSerializer


class HolidayViewSet(viewsets.ModelViewSet):
    """ViewSet for school holidays"""
    serializer_class = HolidaySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'school') and user.school:
            return Holiday.objects.filter(school=user.school)
        return Holiday.objects.none()

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'school') and self.request.user.school:
            serializer.save(school=self.request.user.school)


class SchoolEventViewSet(viewsets.ModelViewSet):
    """ViewSet for school events"""
    serializer_class = SchoolEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'school') and user.school:
            return SchoolEvent.objects.filter(school=user.school)
        return SchoolEvent.objects.none()

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'school') and self.request.user.school:
            serializer.save(school=self.request.user.school)
