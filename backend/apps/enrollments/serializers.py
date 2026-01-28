from rest_framework import serializers
from .models import StudentEnrollment

class StudentEnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    student_suid = serializers.CharField(source='student.suid', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    current_class = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentEnrollment
        fields = '__all__'
        read_only_fields = ['enrollment_date']
    
    def get_current_class(self, obj):
        return f"{obj.grade}-{obj.section}"