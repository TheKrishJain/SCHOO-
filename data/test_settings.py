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
from apps.schools.serializers_settings import SchoolSettingsSerializer

def test_settings():
    """
    Test that settings are properly configured and serialized
    """
    
    school = School.objects.first()
    if not school:
        print("❌ No school found")
        return
    
    print(f"✅ Found school: {school.name} ({school.code})")
    
    settings, created = SchoolSettings.objects.get_or_create(school=school)
    
    if created:
        print("✅ Created new settings")
    else:
        print("✅ Settings already exist")
    
    # Serialize
    serializer = SchoolSettingsSerializer(settings)
    data = serializer.data
    
    print("\n📋 Serialized Data:")
    print(f"   School Name: {data.get('school_name', 'MISSING')}")
    print(f"   School Code: {data.get('school_code', 'MISSING')}")
    print(f"   Dark Mode: {data.get('dark_mode', 'MISSING')}")
    print(f"   Primary Color: {data.get('primary_color', 'MISSING')}")
    print(f"   Show Student Stats: {data.get('show_student_stats', 'MISSING')}")
    
    print(f"\n✅ Settings test complete!")

if __name__ == '__main__':
    test_settings()
