from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.http import HttpResponse
import csv

from .models import Student, Guardian, StudentDocument, StudentHistory
from .serializers import StudentSerializer, StudentDetailSerializer, GuardianSerializer, StudentHistorySerializer
from apps.features.permissions import can
from apps.core.school_isolation import SchoolIsolationMixin, get_user_school, is_platform_admin
from apps.accounts.permission_utils import RBACPermission


class StudentViewSet(SchoolIsolationMixin, viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    school_field = 'school'
    
    # RBAC Configuration
    rbac_module = 'students'
    rbac_resource = 'student'
    rbac_action_permissions = {
        'profile': 'students.view_student',
        'history': 'students.view_student',
        'guardians': 'students.view_student',
        'export': 'students.export_student',
        'import_students': 'students.import_student',
    }
    
    def get_queryset(self):
        """Filter students by user's school."""
        queryset = Student.objects.select_related('user')
        
        # Apply school isolation
        user = self.request.user
        if is_platform_admin(user):
            return queryset
        
        user_school = get_user_school(user)
        if user_school:
            queryset = queryset.filter(user__school_id=user_school.id)
        else:
            # No school - empty queryset
            queryset = queryset.none()
        
        return queryset

    # --- SECURITY: VIEWING SINGLE PROFILE ---
    def retrieve(self, request, *args, **kwargs):
        # Permission: School isolation mixin handles access control
        # School admins can view any student in their school
        # Platform admins can view any student
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # --- SECURITY: VIEWING DIRECTORY ---
    def list(self, request, *args, **kwargs):
        # Permission: School isolation mixin filters by school
        # School admins see their school's students
        # Platform admins see all students
        return super().list(request, *args, **kwargs)

    # --- LOGIC: UPDATING PROFILE (Your Original Code) ---
    def update(self, request, *args, **kwargs):
        # 1. Get the student instance
        instance = self.get_object()
        
        # 2. Extract user-related data
        user_data = {
            'full_name': request.data.get('full_name'),
            'email': request.data.get('email'),
            'phone_number': request.data.get('phone_number')
        }
        
        # 3. Update the User Model manually
        if instance.user:
            user = instance.user
            for key, value in user_data.items():
                if value is not None: 
                    setattr(user, key, value)
            user.save()

        # 4. Update the Student Model via standard Serializer
        return super().update(request, *args, **kwargs)
    
    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """Get complete student profile with all details"""
        student = self.get_object()
        serializer = StudentDetailSerializer(student)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get student's academic history across years"""
        student = self.get_object()
        history = StudentHistory.objects.filter(student=student).order_by('-academic_year_name')
        serializer = StudentHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def guardians(self, request, pk=None):
        """Get student's guardians/parents"""
        student = self.get_object()
        guardians = Guardian.objects.filter(student=student)
        serializer = GuardianSerializer(guardians, many=True)
        return Response(serializer.data)


# View for teachers to see their remarks
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.teachers.models import Teacher

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_remarks(request):
    """
    Get all remarks made by the logged-in teacher across years.
    This allows teachers to see their feedback history.
    """
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        return Response({'error': 'Not a teacher'}, status=403)
    
    # Get all history records where this teacher gave remarks
    remarks = StudentHistory.objects.filter(
        class_teacher=teacher,
        teacher_remarks__isnull=False
    ).exclude(teacher_remarks='').select_related('student', 'student__user').order_by('-academic_year_name')
    
    data = [{
        'id': str(r.id),
        'student_id': r.student.id,
        'student_name': r.student.full_name_display,
        'student_photo': r.student.profile_photo.url if r.student.profile_photo else None,
        'grade_name': r.grade_name,
        'section_name': r.section_name,
        'academic_year': r.academic_year_name,
        'remarks': r.teacher_remarks,
        'remarks_date': r.remarks_date.isoformat() if r.remarks_date else None,
        'overall_grade': r.overall_grade,
        'class_rank': r.class_rank,
        'percentage': str(r.percentage) if r.percentage else None,
    } for r in remarks]
    
    return Response({
        'count': len(data),
        'remarks': data
    })