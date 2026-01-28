"""
Seed Default Notification Templates
Run: python manage.py shell < seed_notification_templates.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.notifications.models import NotificationTemplate

DEFAULT_TEMPLATES = [
    {
        'category': 'ATTENDANCE',
        'title': 'Attendance Alert',
        'body': '''Dear Parent/Guardian,

This is to inform you that {{student_name}}'s attendance has dropped to {{attendance_percentage}}%.

Regular attendance is crucial for academic success. Please ensure your child attends school regularly.

If there are any circumstances affecting attendance, please contact the school office.

Best regards,
{{school_name}}''',
        'channels': {'sms': True, 'email': True, 'whatsapp': False},
    },
    {
        'category': 'MARKS',
        'title': 'Exam Results Notification',
        'body': '''Dear Parent/Guardian,

We are pleased to share {{student_name}}'s exam results:

Subject: {{subject_name}}
Exam: {{exam_name}}
Marks Obtained: {{marks}}/{{max_marks}}
Percentage: {{percentage}}%
Grade: {{grade}}

{{#if remarks}}
Teacher's Remarks: {{remarks}}
{{/if}}

For detailed report card, please visit the school portal or contact the class teacher.

Best regards,
{{school_name}}''',
        'channels': {'sms': True, 'email': True, 'whatsapp': True},
    },
    {
        'category': 'DISCIPLINE',
        'title': 'Discipline Incident Notice',
        'body': '''Dear Parent/Guardian,

This is to inform you about a discipline matter concerning {{student_name}}:

Date: {{incident_date}}
Incident: {{incident_description}}
Action Taken: {{action_taken}}

We request your cooperation in addressing this matter. Please contact the school office if you have any questions.

Best regards,
{{school_name}}''',
        'channels': {'sms': True, 'email': True, 'whatsapp': False},
    },
    {
        'category': 'PROMOTION',
        'title': 'Promotion Decision Notification',
        'body': '''Dear Parent/Guardian,

We are pleased to inform you about {{student_name}}'s academic progress:

Academic Year: {{academic_year}}
Current Grade: {{from_grade}}
Decision: {{decision}}
{{#if to_grade}}
Promoted To: {{to_grade}}
{{/if}}

{{#if remarks}}
Remarks: {{remarks}}
{{/if}}

Please collect the report card from the school office. For any queries, contact the class teacher.

Best regards,
{{school_name}}''',
        'channels': {'sms': True, 'email': True, 'whatsapp': True},
    },
    {
        'category': 'CERTIFICATE',
        'title': 'Certificate Ready for Collection',
        'body': '''Dear Parent/Guardian,

This is to inform you that {{student_name}}'s {{certificate_type}} is ready for collection.

Please visit the school administrative office during working hours with a valid ID to collect the certificate.

Office Hours: Monday to Friday, 9:00 AM - 4:00 PM

Best regards,
{{school_name}}''',
        'channels': {'sms': True, 'email': True, 'whatsapp': False},
    },
    {
        'category': 'GENERAL',
        'title': 'School Notification',
        'body': '''Dear Parent/Guardian,

{{message}}

For any queries, please contact the school office.

Best regards,
{{school_name}}''',
        'channels': {'sms': True, 'email': True, 'whatsapp': False},
    },
]


def seed_templates():
    """Create default notification templates for all schools."""
    from apps.schools.models import School
    
    schools = School.objects.all()
    if not schools.exists():
        print("No schools found. Please create at least one school first.")
        return 0, 0
    
    created_count = 0
    updated_count = 0
    
    for school in schools:
        print(f"\nSeeding templates for: {school.name}")
        for template_data in DEFAULT_TEMPLATES:
            template, created = NotificationTemplate.objects.update_or_create(
                school=school,
                category=template_data['category'],
                defaults={
                    'title': template_data['title'],
                    'body': template_data['body'],
                    'channels': template_data['channels'],
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                print(f"  ✓ Created template: {template_data['category']}")
            else:
                updated_count += 1
                print(f"  ↻ Updated template: {template_data['category']}")
    
    print(f"\nDone! Created: {created_count}, Updated: {updated_count}")
    return created_count, updated_count


if __name__ == '__main__':
    seed_templates()
