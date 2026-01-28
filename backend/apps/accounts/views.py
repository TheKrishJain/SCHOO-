from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count, Avg
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, UserSerializer
from .password_reset import (
    PasswordResetToken, 
    send_password_reset_email, 
    get_client_ip
)
from .uid_validation import validate_uid, UIDGenerator

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """
    Aggregated dashboard metrics for school principal/admin.
    School admins see only their school's data.
    Platform admins see all data.
    """
    from apps.students.models import Student
    from apps.enrollments.models import StudentEnrollment
    from apps.discipline.models import DisciplineRecord, KarmaActivity
    from apps.gatepass.models import GatePass
    from apps.attendance.models import AttendanceSession, StudentAttendance
    from apps.core.school_isolation import get_user_school, is_platform_admin
    from django.db.models import Q, Count
    from datetime import datetime, timedelta
    
    # Get user's school for filtering
    user = request.user
    user_school = get_user_school(user)
    platform_admin = is_platform_admin(user)
    
    # Build school filter - use school_id for FK comparisons
    def apply_school_filter(queryset, school_field='school'):
        if platform_admin:
            return queryset
        if user_school:
            return queryset.filter(**{school_field: user_school.id})
        return queryset.none()
    
    # Basic counts - Student model (Student -> User -> School)
    if platform_admin:
        students_qs = Student.objects.all()
    elif user_school:
        students_qs = Student.objects.filter(user__school_id=user_school.id)
    else:
        students_qs = Student.objects.none()
    total_students = students_qs.count()
    
    # Active enrollments count
    enrollments_qs = apply_school_filter(StudentEnrollment.objects.filter(status='ACTIVE'), 'school_id')
    active_enrollments = enrollments_qs.count()
    
    # Calculate average attendance from actual data (StudentAttendance -> Student -> User -> School)
    if platform_admin:
        attendance_qs = StudentAttendance.objects.all()
    elif user_school:
        attendance_qs = StudentAttendance.objects.filter(student__user__school_id=user_school.id)
    else:
        attendance_qs = StudentAttendance.objects.none()
    
    total_attendance_records = attendance_qs.count()
    if total_attendance_records > 0:
        present_count = attendance_qs.filter(status='PRESENT').count()
        avg_attendance = round((present_count / total_attendance_records) * 100, 1)
    else:
        avg_attendance = 0
    
    # Behavior incidents (DisciplineRecord -> Student -> User -> School)
    if platform_admin:
        incidents_qs = DisciplineRecord.objects.all()
    elif user_school:
        incidents_qs = DisciplineRecord.objects.filter(student__user__school_id=user_school.id)
    else:
        incidents_qs = DisciplineRecord.objects.none()
    total_incidents = incidents_qs.count()
    
    # Active gate passes (GatePass -> Student -> User -> School)
    if platform_admin:
        passes_qs = GatePass.objects.filter(status='ACTIVE')
    elif user_school:
        passes_qs = GatePass.objects.filter(status='ACTIVE', student__user__school_id=user_school.id)
    else:
        passes_qs = GatePass.objects.none()
    active_passes = passes_qs.count()
    
    # Monthly enrollment data
    from django.db.models.functions import TruncMonth
    
    six_months_ago = datetime.now() - timedelta(days=180)
    if platform_admin:
        monthly_qs = StudentEnrollment.objects.filter(enrollment_date__gte=six_months_ago)
    elif user_school:
        monthly_qs = StudentEnrollment.objects.filter(enrollment_date__gte=six_months_ago, school_id=user_school.id)
    else:
        monthly_qs = StudentEnrollment.objects.none()
    monthly_data = monthly_qs.annotate(
        month=TruncMonth('enrollment_date')
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    # Format for frontend
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_enrollment = []
    cumulative = 0
    for entry in monthly_data:
        month_num = entry['month'].month - 1
        cumulative += entry['count']
        monthly_enrollment.append({
            'month': month_names[month_num],
            'students': cumulative
        })
    
    if not monthly_enrollment:
        monthly_enrollment = [{'month': 'Jan', 'students': total_students}]
    
    # Recent karma awards
    if platform_admin:
        karma_qs = KarmaActivity.objects.select_related('student', 'student__user')
    elif user_school:
        karma_qs = KarmaActivity.objects.select_related('student', 'student__user').filter(student__user__school_id=user_school.id)
    else:
        karma_qs = KarmaActivity.objects.none()
    
    recent_karma_records = karma_qs.order_by('-date')[:5]
    recent_karma = [
        {
            'student_name': f"{record.student.user.first_name} {record.student.user.last_name}",
            'reason': record.title,
            'points': record.points
        }
        for record in recent_karma_records
    ]
    
    if not recent_karma:
        recent_karma = [{'student_name': 'No recent karma', 'reason': 'No activities yet', 'points': 0}]
    
    # Add school info to response
    response_data = {
        'total_students': total_students,
        'avg_attendance': avg_attendance,
        'total_incidents': total_incidents,
        'active_passes': active_passes,
        'monthly_enrollment': monthly_enrollment,
        'recent_karma': recent_karma,
    }
    
    # Add user context
    if user_school:
        response_data['school_name'] = user_school.name
        response_data['school_id'] = str(user_school.id)
    elif platform_admin:
        response_data['school_name'] = 'All Schools (Platform Admin)'
        response_data['is_platform_admin'] = True
    
    return Response(response_data)


# ============================================
# PASSWORD RESET VIEWS
# ============================================

class RequestPasswordResetView(APIView):
    """
    Request a password reset link via email.
    
    POST /auth/password-reset/request/
    {
        "email": "admin@school.com"
    }
    
    Security:
    - Only for SCHOOL_ADMIN and ADMIN users initially
    - Rate limited (3 requests per hour)
    - Doesn't reveal if email exists (returns same message)
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Always return success message to prevent email enumeration
        success_message = {
            'message': 'If an account exists with this email, you will receive a password reset link shortly.',
            'email_sent': True
        }
        
        try:
            user = User.objects.get(email=email)
            
            # Only allow school admins for now
            if user.user_type not in ['SCHOOL_ADMIN', 'ADMIN', 'PLATFORM_ADMIN']:
                # Silently ignore non-admin users (security)
                return Response(success_message)
            
            # Check rate limiting
            if not PasswordResetToken.can_request_reset(user):
                return Response(
                    {'error': 'Too many reset requests. Please try again later.'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # Get request metadata
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Create token
            token_instance, plain_token = PasswordResetToken.create_for_user(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Send email
            email_sent = send_password_reset_email(user, plain_token, request)
            
            if not email_sent:
                # Log error but don't expose to user
                print(f"Failed to send reset email to {email}")
            
        except User.DoesNotExist:
            # Don't reveal that user doesn't exist
            pass
        
        return Response(success_message)


class VerifyResetTokenView(APIView):
    """
    Verify if a password reset token is valid.
    
    POST /auth/password-reset/verify/
    {
        "token": "abcdef123456..."
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        token = request.data.get('token', '')
        
        if not token:
            return Response(
                {'valid': False, 'error': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user, token_instance = PasswordResetToken.verify_token(token)
        
        if user:
            return Response({
                'valid': True,
                'email': user.email,
                'user_name': user.first_name or user.email.split('@')[0]
            })
        else:
            return Response({
                'valid': False,
                'error': 'Invalid or expired token'
            }, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    """
    Reset password using a valid token.
    
    POST /auth/password-reset/confirm/
    {
        "token": "abcdef123456...",
        "new_password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!"
    }
    
    Password Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        token = request.data.get('token', '')
        new_password = request.data.get('new_password', '')
        confirm_password = request.data.get('confirm_password', '')
        
        # Validate input
        if not token:
            return Response(
                {'error': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not new_password or not confirm_password:
            return Response(
                {'error': 'Password fields are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != confirm_password:
            return Response(
                {'error': 'Passwords do not match'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate password strength
        password_errors = self._validate_password(new_password)
        if password_errors:
            return Response(
                {'error': password_errors[0], 'errors': password_errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify token
        user, token_instance = PasswordResetToken.verify_token(token)
        
        if not user:
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        # Mark token as used
        token_instance.mark_used()
        
        return Response({
            'success': True,
            'message': 'Password has been reset successfully. You can now login with your new password.'
        })
    
    def _validate_password(self, password):
        """Validate password strength."""
        errors = []
        
        if len(password) < 8:
            errors.append('Password must be at least 8 characters long')
        
        if not any(c.isupper() for c in password):
            errors.append('Password must contain at least one uppercase letter')
        
        if not any(c.islower() for c in password):
            errors.append('Password must contain at least one lowercase letter')
        
        if not any(c.isdigit() for c in password):
            errors.append('Password must contain at least one digit')
        
        special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        if not any(c in special_chars for c in password):
            errors.append('Password must contain at least one special character (!@#$%^&*...)')
        
        return errors


# ============================================
# UID VALIDATION VIEWS
# ============================================

class ValidateUIDView(APIView):
    """
    Validate a SUID or TUID.
    
    POST /auth/validate-uid/
    {
        "uid": "S-DPS-2026-A3F9B2-7"
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        uid = request.data.get('uid', '').strip().upper()
        
        if not uid:
            return Response(
                {'valid': False, 'error': 'UID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_valid, uid_type, message = validate_uid(uid)
        
        return Response({
            'valid': is_valid,
            'uid_type': uid_type,
            'message': message,
            'uid': uid
        })