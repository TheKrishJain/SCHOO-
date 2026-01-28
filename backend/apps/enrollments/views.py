from rest_framework import viewsets, permissions, status as http_status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from .models import StudentEnrollment
from .serializers import StudentEnrollmentSerializer
from apps.accounts.permission_utils import RBACPermission

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = StudentEnrollment.objects.all()
    serializer_class = StudentEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated, RBACPermission]
    
    # RBAC Configuration
    rbac_module = 'enrollments'
    rbac_resource = 'enrollment'
    rbac_action_permissions = {
        'class_strength': 'enrollments.view_enrollment',
        'assign_roll_numbers': 'enrollments.edit_enrollment',
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        
        school_id = self.request.query_params.get('school')
        if school_id:
            queryset = queryset.filter(school_id=school_id)
        
        student_id = self.request.query_params.get('student')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        grade = self.request.query_params.get('grade')
        if grade:
            queryset = queryset.filter(grade=grade)
        
        section = self.request.query_params.get('section')
        if section:
            queryset = queryset.filter(section=section)
        
        enrollment_status = self.request.query_params.get('status')
        if enrollment_status:
            queryset = queryset.filter(status=enrollment_status)
        
        academic_year = self.request.query_params.get('academic_year')
        if academic_year:
            queryset = queryset.filter(academic_year=academic_year)
            
        return queryset.order_by('grade', 'section', 'roll_number')
    
    @action(detail=False, methods=['get'])
    def class_strength(self, request):
        """Get student count by grade and section"""
        school_id = request.query_params.get('school')
        queryset = self.get_queryset().filter(status='ACTIVE')
        
        if school_id:
            queryset = queryset.filter(school_id=school_id)
        
        strength = queryset.values('grade', 'section').annotate(
            student_count=Count('id')
        ).order_by('grade', 'section')
        
        return Response(list(strength))
    
    @action(detail=True, methods=['post'])
    def promote(self, request, pk=None):
        """Promote student to next grade"""
        enrollment = self.get_object()
        new_grade = request.data.get('new_grade')
        new_section = request.data.get('new_section')
        
        if not new_grade or not new_section:
            return Response(
                {'error': 'new_grade and new_section required'}, 
                status=http_status.HTTP_400_BAD_REQUEST
            )
        
        enrollment.status = 'INACTIVE'
        enrollment.save()
        
        new_enrollment = StudentEnrollment.objects.create(
            student=enrollment.student,
            school=enrollment.school,
            grade=new_grade,
            section=new_section,
            academic_year=request.data.get('academic_year', '2026-2027'),
            status='ACTIVE'
        )
        
        return Response(StudentEnrollmentSerializer(new_enrollment).data)