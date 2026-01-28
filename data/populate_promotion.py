import os
import django
import sys
from datetime import date, timedelta

# Setup Django - point to backend directory
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
sys.path.insert(0, backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.enrollments.models_promotion import AcademicYear, PromotionRule
from apps.schools.models import School

def populate_promotion_data():
    """
    Create sample academic years and promotion rules
    """
    
    # Get first school
    school = School.objects.first()
    if not school:
        print("No school found. Create a school first.")
        return
    
    print(f"Using school: {school.name}")
    
    # Create Academic Years
    current_year = AcademicYear.objects.create(
        school=school,
        year_code="2025-2026",
        start_date=date(2025, 4, 1),
        end_date=date(2026, 3, 31),
        status='ACTIVE'
    )
    print(f"Created Academic Year: {current_year.year_code}")
    
    next_year = AcademicYear.objects.create(
        school=school,
        year_code="2026-2027",
        start_date=date(2026, 4, 1),
        end_date=date(2027, 3, 31),
        status='UPCOMING'
    )
    print(f"Created Academic Year: {next_year.year_code}")
    
    # Create Promotion Rules (LKG to 10th)
    grade_progression = [
        ('LKG', 'UKG'),
        ('UKG', '1'),
        ('1', '2'),
        ('2', '3'),
        ('3', '4'),
        ('4', '5'),
        ('5', '6'),
        ('6', '7'),
        ('7', '8'),
        ('8', '9'),
        ('9', '10'),
        ('10', 'ALUMNI'),
    ]
    
    for from_grade, to_grade in grade_progression:
        rule = PromotionRule.objects.create(
            school=school,
            from_grade=from_grade,
            to_grade=to_grade,
            promotion_type='AUTO' if from_grade in ['LKG', 'UKG'] else 'MARKS_BASED',
            min_percentage=None if from_grade in ['LKG', 'UKG'] else 35,
            is_active=True
        )
        print(f"Created Rule: {from_grade} → {to_grade} ({rule.promotion_type})")
    
    print("\n✅ Promotion system data populated successfully!")
    print(f"   - 2 Academic Years")
    print(f"   - {len(grade_progression)} Promotion Rules")

if __name__ == '__main__':
    populate_promotion_data()
