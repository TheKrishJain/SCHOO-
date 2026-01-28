#!/usr/bin/env python
"""
Quick script to seed academic years for testing Year-End promotion.
Run: python seed_academic_years.py
"""
import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.schools.models import School
from apps.enrollments.models_promotion import AcademicYear

def seed_academic_years():
    print("🎓 Seeding Academic Years...")
    
    # Get the first school (or create one if none exists)
    try:
        school = School.objects.first()
        if not school:
            print("❌ No school found! Please create a school first.")
            return
            
        print(f"✅ Using school: {school.name} (ID: {school.id})")
    except Exception as e:
        print(f"❌ Error getting school: {e}")
        return
    
    # Create 2025-2026 (Current Year - ACTIVE)
    year_2025, created1 = AcademicYear.objects.get_or_create(
        school=school,
        year_code='2025-2026',
        defaults={
            'start_date': date(2025, 4, 1),
            'end_date': date(2026, 3, 31),
            'status': 'ACTIVE'
        }
    )
    
    if created1:
        print(f"✅ Created: 2025-2026 (ACTIVE)")
    else:
        print(f"ℹ️  Already exists: 2025-2026")
    
    # Create 2026-2027 (Next Year - UPCOMING)
    year_2026, created2 = AcademicYear.objects.get_or_create(
        school=school,
        year_code='2026-2027',
        defaults={
            'start_date': date(2026, 4, 1),
            'end_date': date(2027, 3, 31),
            'status': 'UPCOMING'
        }
    )
    
    if created2:
        print(f"✅ Created: 2026-2027 (UPCOMING)")
    else:
        print(f"ℹ️  Already exists: 2026-2027")
    
    print("\n📊 Summary:")
    print(f"   School: {school.name}")
    print(f"   Current Year: 2025-2026 (ID: {year_2025.id})")
    print(f"   Next Year: 2026-2027 (ID: {year_2026.id})")
    print("\n🎉 Academic years are ready for Year-End promotion testing!")

if __name__ == '__main__':
    seed_academic_years()
