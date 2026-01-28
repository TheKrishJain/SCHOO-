import uuid
from django.db import models
from apps.students.models import Student
from django.conf import settings

class GatePass(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('ACTIVE', 'Active (Ready to Scan)'),
        ('USED', 'Used (Student Left)'),
        ('EXPIRED', 'Expired (Not Used)'),
    ]

    # A unique generic ID (UUID) that is hard to guess
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='gate_passes')
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='requested_gatepasses',
        help_text="Who requested the gate pass (student/parent/admin)"
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='issued_gatepasses',
        help_text="Who approved and issued the pass"
    )
    
    # Approval flow
    approved_by_class_teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_gatepasses'
    )
    approval_note = models.TextField(blank=True, help_text="Note from approver")
    rejection_reason = models.TextField(blank=True)
    
    reason = models.TextField(help_text="e.g. Medical Emergency, Family Function")
    requested_at = models.DateTimeField(auto_now_add=True)
    issued_at = models.DateTimeField(null=True, blank=True, help_text="When the pass was issued")
    out_time = models.TimeField(null=True, blank=True, help_text="Expected time to leave school")
    valid_until = models.DateTimeField(help_text="Pass expires after this time")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Audit log
    approved_at = models.DateTimeField(null=True, blank=True)
    scanned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='scanned_passes', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    scanned_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"PASS: {self.student.user.full_name} ({self.status})"