from rest_framework import serializers
from .models_calendar import Holiday, SchoolEvent


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = ['id', 'school', 'name', 'date', 'description', 'is_recurring', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and hasattr(request.user, 'school'):
            validated_data['school'] = request.user.school
        return super().create(validated_data)


class SchoolEventSerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)

    class Meta:
        model = SchoolEvent
        fields = [
            'id', 'school', 'title', 'event_date', 'start_time', 'end_time',
            'event_type', 'event_type_display', 'description', 'location',
            'is_all_day', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and hasattr(request.user, 'school'):
            validated_data['school'] = request.user.school
        return super().create(validated_data)
