#!/usr/bin/env python
"""
Seed promotion rules and sample exam marks for Year-End testing.
Run: python seed_promotion_data.py
"""
import os
import django
from datetime import date
from random import randint, choice

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.schools.models import School
from apps.enrollments.models_promotion import AcademicYear, PromotionRule
from apps.students.models import Student

def seed_promotion_rules():
    print("🎓 Seeding Promotion Rules and Exam Data...")
    
    school = School.objects.first()
    if not school:
        print("❌ No school found!")
        return
    
    print(f"✅ Using school: {school.name}")
    
    # Create promotion rules
    rules_data = [
        ('9', '10', 'Grade 9 → 10'),
        ('10', '11', 'Grade 10 → 11'),
        ('11', '12', 'Grade 11 → 12'),
        ('12', 'ALUMNI', 'Grade 12 → Graduation'),
    ]
    
    rules_created = 0
    for from_grade, to_grade, description in rules_data:
        rule, created = PromotionRule.objects.get_or_create(
            school=school,
            from_grade=from_grade,
            defaults={
                'to_grade': to_grade,
                'promotion_type': 'AUTO',
                'action': 'GRADUATE' if to_grade == 'ALUMNI' else 'PROMOTE',
                'min_percentage': 35.0,
                'auto_assign_section': True,
                'is_active': True
            }
        )
        if created:
            print(f"✅ Created rule: {description}")
            rules_created += 1
        else:
            print(f"ℹ️  Rule exists: {description}")
    
    print(f"\n✅ Created {rules_created} new promotion rules")
    print(f"📊 Total rules: {PromotionRule.objects.filter(school=school).count()}")
    
    print("\n🎉 Promotion rules are ready!")
    print("\nNext steps:")
    print("1. Go to Year-End page")
    print("2. Select 2025-2026 academic year")
    print("3. Click 'Generate Promotion Preview'")
    print("4. Review the 120 students and their promotions")
    print("5. Execute the batch promotion!")

if __name__ == '__main__':
    seed_promotion_rules()
