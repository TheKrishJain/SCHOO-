from rest_framework import serializers
from .models import GatePass

class GatePassSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    student_suid = serializers.CharField(source='student.suid', read_only=True)
    issued_by_name = serializers.CharField(source='issued_by.full_name', read_only=True)
    scanned_by_name = serializers.CharField(source='scanned_by.full_name', read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = GatePass
        fields = '__all__'
        read_only_fields = [
            'id', 'issued_by', 'issued_at', 'valid_until', 
            'status', 'scanned_by', 'scanned_at'
        ]
    
    def get_is_expired(self, obj):
        from django.utils import timezone
        return timezone.now() > obj.valid_until and obj.status == 'ACTIVE'