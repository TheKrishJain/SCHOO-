from rest_framework import serializers
from .models_promotion import (
    AcademicYear, PromotionRule, PromotionBatch, 
    PromotionRecord, DataCarryForward
)
from .models import StudentEnrollment


class AcademicYearSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    can_close = serializers.SerializerMethodField()
    
    class Meta:
        model = AcademicYear
        fields = '__all__'
        read_only_fields = ['closed_by', 'closed_at']
    
    def get_can_close(self, obj):
        # Can only close if ACTIVE and has enrollments
        return obj.status == 'ACTIVE' and StudentEnrollment.objects.filter(
            school=obj.school, 
            academic_year=obj.year_code, 
            status='ACTIVE'
        ).exists()


class PromotionRuleSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    
    class Meta:
        model = PromotionRule
        fields = '__all__'


class PromotionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionRecord
        fields = '__all__'
        read_only_fields = ['is_locked']


class PromotionBatchSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    academic_year_code = serializers.CharField(source='academic_year.year_code', read_only=True)
    initiated_by_name = serializers.CharField(source='initiated_by.first_name', read_only=True)
    records = PromotionRecordSerializer(many=True, read_only=True)
    
    class Meta:
        model = PromotionBatch
        fields = '__all__'
        read_only_fields = ['initiated_by', 'completed_at']


class DataCarryForwardSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True)
    
    class Meta:
        model = DataCarryForward
        fields = '__all__'


class PromotionPreviewSerializer(serializers.Serializer):
    """
    Preview data before executing promotion
    """
    enrollment_id = serializers.UUIDField()
    student_name = serializers.CharField()
    student_suid = serializers.CharField()
    current_grade = serializers.CharField()
    current_section = serializers.CharField()
    target_grade = serializers.CharField()
    target_section = serializers.CharField(allow_blank=True)
    action = serializers.CharField()
    reason = serializers.CharField(allow_blank=True)
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
