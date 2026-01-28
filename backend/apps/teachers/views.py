from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Teacher, TeacherSchoolAssociation, TeacherAssignment, Remark
from .serializers import TeacherSerializer, TeacherSchoolAssociationSerializer, TeacherAssignmentSerializer, RemarkSerializer
from apps.students.models import Student
from apps.students.serializers import StudentSerializer
from apps.accounts.permission_utils import RBACPermission


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def teacher_profile(request):
    """Get or update current teacher's profile"""
    try:
        teacher = Teacher.objects.get(user=request.user)
        
        if request.method == 'GET':
            serializer = TeacherSerializer(teacher)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = TeacherSerializer(teacher, data=request.data, partial=partial)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Teacher.DoesNotExist:
        return Response(
            {'error': 'Teacher profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_detail(request, student_id):
    """Get student details - for teachers to view their students"""
    try:
        from apps.attendance.models import StudentAttendance
        from apps.discipline.models import StudentKarma
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        
        teacher = Teacher.objects.get(user=request.user)
        student = Student.objects.get(id=student_id)
        
        # Verify teacher has access to this student
        # (student is in one of teacher's classes)
        teacher_assignments = TeacherAssignment.objects.filter(
            teacher=teacher,
            is_active=True
        )
        
        has_access = False
        student_enrollment = None
        for assignment in teacher_assignments:
            enrollment = student.enrollments.filter(
                grade=assignment.grade,
                section=assignment.section,
                status='ACTIVE'
            ).first()
            if enrollment:
                has_access = True
                student_enrollment = enrollment
                break
        
        if not has_access:
            return Response(
                {'error': 'You do not have access to this student'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get student data
        student_data = {
            'id': str(student.id),
            'full_name': student.user.full_name,
            'suid': student.suid,
            'email': student.user.email,
            'grade': student_enrollment.grade if student_enrollment else '',
            'section': student_enrollment.section if student_enrollment else '',
            'roll_number': student_enrollment.roll_number if student_enrollment else '',
            'photo': student.profile_photo.url if student.profile_photo else None,
        }
        
        # Get attendance stats (last 30 days)
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        attendance_records = StudentAttendance.objects.filter(
            student=student,
            session__date__gte=thirty_days_ago  # Access date through session relationship
        )
        
        total_days = attendance_records.count()
        present_count = attendance_records.filter(status='PRESENT').count()
        late_count = attendance_records.filter(status='LATE').count()
        absent_count = attendance_records.filter(status='ABSENT').count()
        
        attendance_data = {
            'total_days': total_days,
            'present': present_count,
            'late': late_count,
            'absent': absent_count,
            'percentage': round((present_count + late_count) / total_days * 100, 1) if total_days > 0 else 0
        }
        
        # Get karma/discipline data
        try:
            karma_records = StudentKarma.objects.filter(student=student)
            positive_total = sum(k.points for k in karma_records if k.type == 'POSITIVE')
            negative_total = sum(abs(k.points) for k in karma_records if k.type == 'NEGATIVE')
            
            karma_data = {
                'positive_total': positive_total,
                'negative_total': negative_total,
                'net_score': positive_total - negative_total,
                'recent_records': []
            }
        except Exception:
            # Karma system might not be set up yet
            karma_data = {
                'positive_total': 0,
                'negative_total': 0,
                'net_score': 0,
                'recent_records': []
            }
        
        # Get academic performance from ReportCard
        from apps.academics.models import ReportCard
        
        academic_data = {
            'rank': None,
            'percentage': 0.0,
            'total_marks': None,
        }
        
        try:
            # Get the latest report card for this student
            report_card = ReportCard.objects.filter(
                student=student,
                academic_year='2026-2027'
            ).order_by('-generated_date').first()
            
            if report_card:
                academic_data['rank'] = report_card.rank
                academic_data['percentage'] = float(report_card.percentage)
                academic_data['total_marks'] = float(report_card.total_marks_obtained)
        except Exception as e:
            print(f"Error fetching report card: {e}")
            pass  # Use defaults if error occurs
        
        # Response
        return Response({
            'student': student_data,
            'attendance': attendance_data,
            'karma': karma_data,
            'academic': academic_data
        })
    
    except Teacher.DoesNotExist:
        return Response(
            {'error': 'Teacher profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Student.DoesNotExist:
        return Response(
            {'error': 'Student not found'},
            status=status.HTTP_404_NOT_FOUND
        )

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticated, RBACPermission]
    
    # RBAC Configuration
    rbac_module = 'teachers'
    rbac_resource = 'teacher'
    rbac_action_permissions = {
        'history': 'teachers.view_teacher',
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        school_id = self.request.query_params.get('school')
        if school_id:
            queryset = queryset.filter(school_associations__school_id=school_id, 
                                      school_associations__status='ACTIVE').distinct()
        return queryset
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get complete employment history for a teacher"""
        teacher = self.get_object()
        associations = TeacherSchoolAssociation.objects.filter(teacher=teacher)
        serializer = TeacherSchoolAssociationSerializer(associations, many=True)
        return Response(serializer.data)


class TeacherSchoolAssociationViewSet(viewsets.ModelViewSet):
    queryset = TeacherSchoolAssociation.objects.all()
    serializer_class = TeacherSchoolAssociationSerializer
    permission_classes = [permissions.IsAuthenticated, RBACPermission]
    
    # RBAC Configuration
    rbac_module = 'teachers'
    rbac_resource = 'teacher'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        school_id = self.request.query_params.get('school')
        if school_id:
            queryset = queryset.filter(school_id=school_id)
        
        teacher_id = self.request.query_params.get('teacher')
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset


class TeacherAssignmentViewSet(viewsets.ModelViewSet):
    queryset = TeacherAssignment.objects.all()
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, RBACPermission]
    
    # RBAC Configuration
    rbac_module = 'teachers'
    rbac_resource = 'assignment'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by logged-in teacher if they are a teacher
        # This ensures teachers only see their own assignments
        if hasattr(self.request.user, 'teacher_profile'):
            queryset = queryset.filter(teacher=self.request.user.teacher_profile)
        
        school_id = self.request.query_params.get('school')
        if school_id:
            queryset = queryset.filter(school_id=school_id)
        
        teacher_id = self.request.query_params.get('teacher')
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
        
        grade = self.request.query_params.get('grade')
        if grade:
            queryset = queryset.filter(grade=grade)
        
        section = self.request.query_params.get('section')
        if section:
            queryset = queryset.filter(section=section)
        
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset


class RemarkViewSet(viewsets.ModelViewSet):
    queryset = Remark.objects.all()
    serializer_class = RemarkSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Remark.objects.all()
        
        # Filter by class if provided
        class_param = self.request.query_params.get('class')
        if class_param:
            # Parse class (e.g., "9-B" -> grade=9, section=B)
            try:
                grade_name, section_name = class_param.split('-')
                queryset = queryset.filter(
                    student__enrollments__grade=grade_name,
                    student__enrollments__section=section_name,
                    student__enrollments__status='ACTIVE'
                )
            except ValueError:
                pass
        
        # Filter by category if provided
        category = self.request.query_params.get('category')
        if category and category != 'ALL':
            queryset = queryset.filter(category=category)
        
        return queryset.distinct()
    
    def perform_create(self, serializer):
        # Get teacher from the current user
        try:
            teacher = Teacher.objects.get(user=self.request.user)
            serializer.save(teacher=teacher)
        except Teacher.DoesNotExist:
            from rest_framework import serializers as drf_serializers
            raise drf_serializers.ValidationError('Teacher profile not found')
