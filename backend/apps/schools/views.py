from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import School
from .models_settings import SchoolSettings
from .serializers import SchoolSerializer
from .serializers_settings import SchoolSettingsSerializer

class SchoolViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Schools to be viewed or edited.
    """
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [permissions.IsAuthenticated]


class SchoolSettingsViewSet(viewsets.ModelViewSet):
    """
    API endpoint for school settings
    """
    queryset = SchoolSettings.objects.all()
    serializer_class = SchoolSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Filter by user's school (assuming user has school relationship)
        user = self.request.user
        if hasattr(user, 'school'):
            return SchoolSettings.objects.filter(school=user.school)
        # For now, return all (will add proper school filtering later)
        return SchoolSettings.objects.all()
    
    @action(detail=False, methods=['get'])
    def my_settings(self, request):
        """
        Get settings for current user's school
        """
        # For now, get first school's settings
        # TODO: Add proper user->school relationship
        school = School.objects.first()
        if not school:
            return Response({'error': 'No school found'}, status=status.HTTP_404_NOT_FOUND)
        
        settings, created = SchoolSettings.objects.get_or_create(school=school)
        serializer = self.get_serializer(settings)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'])
    def update_my_settings(self, request):
        """
        Update settings for current user's school
        """
        # For now, get first school's settings
        school = School.objects.first()
        if not school:
            return Response({'error': 'No school found'}, status=status.HTTP_404_NOT_FOUND)
        
        settings, created = SchoolSettings.objects.get_or_create(school=school)
        serializer = self.get_serializer(settings, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
