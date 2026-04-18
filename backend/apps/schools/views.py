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

    @action(detail=False, methods=['get'])
    def features(self, request):
        """
        Get enabled features for current user's school
        """
        # Logic to get school (same as my_settings)
        school = None
        if hasattr(request.user, 'school') and request.user.school:
            school = request.user.school
        else:
            school = School.objects.first()
            
        if not school:
            return Response({'error': 'No school found'}, status=status.HTTP_404_NOT_FOUND)
            
        # Import dynamically to avoid circular imports if any
        from apps.owner.models import FeatureToggle
        
        # Fetch ALL toggles (enabled and disabled) to respect explicit disablement
        toggles = FeatureToggle.objects.filter(school=school)
        
        # Build a dictionary map
        features_map = {}
        for toggle in toggles:
            # If explicit record exists, use its state
            if toggle.is_enabled:
                features_map[toggle.feature] = {
                    "enabled": True,
                    "sub_features": toggle.sub_features or {}
                }
            # If disabled, we don't add it to map (or add with enabled: False if frontend needs it)
            # The previous logic seemed to rely on presence = enabled.
            # But the 'default core' logic below re-enables it if missing.
            
            # Let's verify how frontend uses it. 
            # Frontend Sidebar: if (!isFeatureEnabled('STUDENTS')) return false;
            # FeatureContext: isFeatureEnabled checks `features[feature]?.enabled`.
            # So if it's missing, it returns false (disabled).
            
            # So, if explicitly disabled in DB, we should NOT add it to map, 
            # AND we must prevent the Core logic below from re-adding it.
            
            # Solution: Add it to a "known_features" set to track existence.
            pass
            
        # Re-implementing correctly:
        known_features = set()
        for toggle in toggles:
            known_features.add(toggle.feature)
            if toggle.is_enabled:
                 features_map[toggle.feature] = {
                    "enabled": True,
                    "sub_features": toggle.sub_features or {}
                }
        
        CORE_FEATURES = ['STUDENTS', 'TEACHERS', 'ATTENDANCE', 'ANNOUNCEMENTS']
        for core in CORE_FEATURES:
            # Only add default if NO RECORD exists at all in the DB
            if core not in known_features:
                features_map[core] = {"enabled": True, "sub_features": {}}
                
        return Response(features_map)
