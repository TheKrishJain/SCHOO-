import os
import django
import sys

# Setup Django
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
sys.path.insert(0, backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.schools.models import School
from apps.schools.models_settings import SchoolSettings

def create_default_settings():
    """
    Create default settings for all schools
    """
    
    schools = School.objects.all()
    
    if not schools.exists():
        print("No schools found. Create a school first.")
        return
    
    for school in schools:
        settings, created = SchoolSettings.objects.get_or_create(
            school=school,
            defaults={
                'dark_mode': False,
                'primary_color': '#3B82F6',
                'show_student_stats': True,
                'show_teacher_stats': True,
                'show_attendance_widget': True,
                'show_finance_widget': True,
                'show_health_widget': True,
                'show_gatepass_widget': True,
                'show_achievements_widget': True,
                'show_transfers_widget': True,
                'email_notifications': True,
                'sms_notifications': False,
                'push_notifications': True,
                'academic_year_format': 'YYYY-YYYY',
                'show_student_photos': True,
                'show_parent_contact': True,
                'show_financial_data': True,
                'default_language': 'en',
                'timezone': 'UTC',
                'date_format': 'DD/MM/YYYY',
            }
        )
        
        if created:
            print(f"✅ Created default settings for {school.name}")
        else:
            print(f"ℹ️  Settings already exist for {school.name}")
    
    print(f"\n✅ Settings initialized for {schools.count()} school(s)")

if __name__ == '__main__':
    create_default_settings()
