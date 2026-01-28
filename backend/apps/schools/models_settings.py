from django.db import models
from apps.schools.models import School
from django.contrib.auth import get_user_model

User = get_user_model()


class SchoolSettings(models.Model):
    """
    School-level settings and preferences
    """
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name='settings')
    
    # Appearance
    dark_mode = models.BooleanField(default=False)
    primary_color = models.CharField(max_length=7, default='#3B82F6', help_text="Hex color code")
    
    # Dashboard Widget Visibility
    show_student_stats = models.BooleanField(default=True)
    show_teacher_stats = models.BooleanField(default=True)
    show_attendance_widget = models.BooleanField(default=True)
    show_finance_widget = models.BooleanField(default=True)
    show_health_widget = models.BooleanField(default=True)
    show_gatepass_widget = models.BooleanField(default=True)
    show_achievements_widget = models.BooleanField(default=True)
    show_transfers_widget = models.BooleanField(default=True)
    show_alumni_stats = models.BooleanField(default=True, help_text="Show alumni statistics on dashboard")
    
    # Notifications
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    
    # Academic Settings
    academic_year_format = models.CharField(
        max_length=20, 
        choices=[
            ('YYYY-YYYY', '2025-2026'),
            ('YYYY/YYYY', '2025/2026'),
            ('YY-YY', '25-26'),
        ],
        default='YYYY-YYYY'
    )
    
    graduation_point = models.CharField(
        max_length=10,
        choices=[
            ('10', 'After Grade 10'),
            ('12', 'After Grade 12'),
        ],
        default='12',
        help_text="Grade level at which students graduate"
    )
    
    allow_continuation_after_10 = models.BooleanField(
        default=True,
        help_text="Allow students to continue to 11-12 after Grade 10"
    )
    
    # Class Teacher Features
    enable_class_teacher_attendance_edit = models.BooleanField(
        default=True,
        help_text="Allow class teachers to edit full-day attendance"
    )
    
    enable_class_teacher_gatepass_approval = models.BooleanField(
        default=True,
        help_text="Allow class teachers to approve gate passes for their class"
    )
    
    karma_system_enabled = models.BooleanField(
        default=True,
        help_text="Enable behavior/discipline tracking system"
    )
    
    karma_label = models.CharField(
        max_length=50,
        default='Karma',
        help_text="Custom name for behavior system (Karma, Conduct Points, Behavior Score, etc.)"
    )

    # Gatepass / Digital Pass Settings
    enable_gatepass_print = models.BooleanField(
        default=False,
        help_text="Show a print icon on the digital pass QR so staff can print the pass"
    )
    
    # Data Privacy
    show_student_photos = models.BooleanField(default=True)
    show_parent_contact = models.BooleanField(default=True)
    show_financial_data = models.BooleanField(default=True)
    
    # System Preferences
    default_language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    date_format = models.CharField(
        max_length=20,
        choices=[
            ('DD/MM/YYYY', 'DD/MM/YYYY'),
            ('MM/DD/YYYY', 'MM/DD/YYYY'),
            ('YYYY-MM-DD', 'YYYY-MM-DD'),
        ],
        default='DD/MM/YYYY'
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # ============================================================
    # FINANCE SETTINGS
    # ============================================================
    
    # Duplicate Billing Protection
    prevent_duplicate_billing = models.BooleanField(
        default=True,
        help_text="Prevent generating duplicate invoices for same student & installment"
    )
    
    require_billing_confirmation = models.BooleanField(
        default=True,
        help_text="Show confirmation dialog before generating invoice"
    )
    
    show_student_fee_history_on_invoice = models.BooleanField(
        default=True,
        help_text="Show student's fee history when creating invoice"
    )
    
    # Auto Invoice Generation
    auto_generate_installment_invoices = models.BooleanField(
        default=False,
        help_text="Automatically generate invoices when installments are due"
    )
    
    days_before_due_to_generate = models.PositiveIntegerField(
        default=7,
        help_text="Days before due date to auto-generate invoice"
    )
    
    # Late Fee Settings
    auto_apply_late_fee = models.BooleanField(
        default=True,
        help_text="Automatically apply late fees to overdue invoices"
    )
    
    # Fee Display
    show_fee_breakdown_on_invoice = models.BooleanField(
        default=True,
        help_text="Show detailed fee breakdown on invoices"
    )
    
    # Payment Reminders
    send_payment_reminders = models.BooleanField(
        default=True,
        help_text="Send automated payment reminders"
    )
    
    reminder_days_before_due = models.PositiveIntegerField(
        default=3,
        help_text="Days before due date to send reminder"
    )
    
    class Meta:
        verbose_name = 'School Settings'
        verbose_name_plural = 'School Settings'
    
    def __str__(self):
        return f"Settings for {self.school.name}"
