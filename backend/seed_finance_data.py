"""
Comprehensive Finance Seed Script
Creates sample data for 10th std students with fee history from LKG till 10th

Run: python manage.py shell < seed_finance_data.py
Or:  python seed_finance_data.py (if Django setup is included)
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date, datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.schools.models import School
from apps.academics.models import Grade, Section
from apps.students.models import Student
from apps.finance.models import (
    FeeCategory, FeeSchedule, FeeStructure, StudentFeeAssignment,
    FeeInstallment, FeeLedger, FeeLedgerEntry, DiscountRecord,
    Invoice, Transaction, LateFeeRule
)

User = get_user_model()

# =============================================================================
# CONFIGURATION
# =============================================================================

# Grade progression from LKG to 10th
GRADE_PROGRESSION = [
    ('LKG', -2),
    ('UKG', -1),
    ('Grade 1', 1),
    ('Grade 2', 2),
    ('Grade 3', 3),
    ('Grade 4', 4),
    ('Grade 5', 5),
    ('Grade 6', 6),
    ('Grade 7', 7),
    ('Grade 8', 8),
    ('Grade 9', 9),
    ('Grade 10', 10),
]

# Fee structure per grade (annual fees in INR)
FEE_BY_GRADE = {
    'LKG': {'tuition': 24000, 'admission': 5000, 'books': 3000, 'activity': 2000},
    'UKG': {'tuition': 26000, 'admission': 0, 'books': 3500, 'activity': 2000},
    'Grade 1': {'tuition': 32000, 'admission': 0, 'books': 4000, 'activity': 2500},
    'Grade 2': {'tuition': 34000, 'admission': 0, 'books': 4200, 'activity': 2500},
    'Grade 3': {'tuition': 36000, 'admission': 0, 'books': 4500, 'activity': 3000},
    'Grade 4': {'tuition': 38000, 'admission': 0, 'books': 4800, 'activity': 3000},
    'Grade 5': {'tuition': 42000, 'admission': 0, 'books': 5000, 'activity': 3500},
    'Grade 6': {'tuition': 48000, 'admission': 0, 'books': 5500, 'activity': 4000},
    'Grade 7': {'tuition': 52000, 'admission': 0, 'books': 6000, 'activity': 4000},
    'Grade 8': {'tuition': 56000, 'admission': 0, 'books': 6500, 'activity': 4500},
    'Grade 9': {'tuition': 62000, 'admission': 0, 'books': 7000, 'activity': 5000},
    'Grade 10': {'tuition': 68000, 'admission': 0, 'books': 8000, 'activity': 6000, 'lab': 4000},
}

# Sample students for 10th std - 3 divisions (A, B, C), 5 students each
SAMPLE_STUDENTS = [
    # Division A
    {'first_name': 'Aarav', 'last_name': 'Sharma', 'gender': 'M', 'section': 'A', 'discount': None},
    {'first_name': 'Ananya', 'last_name': 'Patel', 'gender': 'F', 'section': 'A', 'discount': 'MERIT'},
    {'first_name': 'Vihaan', 'last_name': 'Singh', 'gender': 'M', 'section': 'A', 'discount': 'SIBLING'},
    {'first_name': 'Diya', 'last_name': 'Gupta', 'gender': 'F', 'section': 'A', 'discount': None},
    {'first_name': 'Arjun', 'last_name': 'Kumar', 'gender': 'M', 'section': 'A', 'discount': 'SCHOLARSHIP'},
    # Division B
    {'first_name': 'Ishaan', 'last_name': 'Verma', 'gender': 'M', 'section': 'B', 'discount': None},
    {'first_name': 'Saanvi', 'last_name': 'Reddy', 'gender': 'F', 'section': 'B', 'discount': 'STAFF'},
    {'first_name': 'Reyansh', 'last_name': 'Joshi', 'gender': 'M', 'section': 'B', 'discount': None},
    {'first_name': 'Myra', 'last_name': 'Mehta', 'gender': 'F', 'section': 'B', 'discount': 'FINANCIAL_AID'},
    {'first_name': 'Kabir', 'last_name': 'Shah', 'gender': 'M', 'section': 'B', 'discount': None},
    # Division C
    {'first_name': 'Aadya', 'last_name': 'Nair', 'gender': 'F', 'section': 'C', 'discount': None},
    {'first_name': 'Krishna', 'last_name': 'Iyer', 'gender': 'M', 'section': 'C', 'discount': 'MERIT'},
    {'first_name': 'Avni', 'last_name': 'Rao', 'gender': 'F', 'section': 'C', 'discount': None},
    {'first_name': 'Rudra', 'last_name': 'Desai', 'gender': 'M', 'section': 'C', 'discount': 'SIBLING'},
    {'first_name': 'Prisha', 'last_name': 'Bhat', 'gender': 'F', 'section': 'C', 'discount': None},
]

# Academic years from 2013-2014 (when current 10th graders started LKG)
def get_academic_years():
    """Generate academic years from 2013-2014 to 2025-2026"""
    years = []
    for start_year in range(2013, 2026):
        years.append(f"{start_year}-{start_year + 1}")
    return years

ACADEMIC_YEARS = get_academic_years()

def get_school():
    """Get Premier School (the one user is logged into)"""
    school = School.objects.filter(name__icontains='Premier').first()
    if not school:
        school = School.objects.first()
    if not school:
        print("No school found! Please create a school first.")
        sys.exit(1)
    print(f"Using school: {school.name}")
    return school

def get_admin_user():
    """Get admin user for created_by fields"""
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        admin = User.objects.first()
    return admin

def ensure_grades_exist(school):
    """Ensure all grades from LKG to 10th exist"""
    grades = {}
    for grade_name, grade_num in GRADE_PROGRESSION:
        grade, _ = Grade.objects.get_or_create(
            school=school,
            grade_number=grade_num if grade_num > 0 else 0,
            defaults={'grade_name': grade_name, 'is_active': True}
        )
        # Update grade_name if it exists with different name
        if grade.grade_name != grade_name:
            grade.grade_name = grade_name
            grade.save()
        grades[grade_name] = grade
        print(f"  ✓ Grade: {grade_name}")
    return grades

def ensure_sections_exist(school, grades):
    """Ensure sections A, B, C exist for Grade 10"""
    sections = {}
    grade_10 = grades['Grade 10']
    for section_letter in ['A', 'B', 'C']:
        section, _ = Section.objects.get_or_create(
            school=school,
            grade=grade_10,
            section_letter=section_letter,
            defaults={'capacity': 40, 'is_active': True}
        )
        sections[section_letter] = section
        print(f"  ✓ Section: 10-{section_letter}")
    return sections

def ensure_fee_categories(school):
    """Create fee categories"""
    categories = {}
    category_list = [
        ('Tuition Fee', True),
        ('Admission Fee', False),
        ('Books & Stationery', False),
        ('Activity Fee', True),
        ('Lab Fee', True),
        ('Exam Fee', True),
        ('Transport Fee', True),
        ('Late Fee', False),
    ]
    
    for cat_name, is_recurring in category_list:
        cat, _ = FeeCategory.objects.get_or_create(
            school=school,
            name=cat_name,
            defaults={
                'amount': Decimal('0'),
                'is_recurring': is_recurring,
                'is_active': True
            }
        )
        categories[cat_name] = cat
        print(f"  ✓ Category: {cat_name}")
    return categories

def ensure_fee_schedule(school):
    """Create quarterly fee schedule"""
    schedule, _ = FeeSchedule.objects.get_or_create(
        school=school,
        name='Quarterly Payment',
        defaults={
            'schedule_type': 'QUARTERLY',
            'installments_per_year': 4,
            'is_default': True,
            'is_active': True,
            'grace_period_days': 15,
            'late_fee_per_day': Decimal('50'),
            'max_late_fee': Decimal('1500')
        }
    )
    print(f"  ✓ Schedule: {schedule.name}")
    return schedule

def ensure_late_fee_rule(school, admin):
    """Create late fee rule"""
    rule, _ = LateFeeRule.objects.get_or_create(
        school=school,
        name='Standard Late Fee',
        defaults={
            'calculation_type': 'PER_DAY',
            'per_day_amount': Decimal('50'),
            'grace_period_days': 15,
            'max_late_fee': Decimal('1500'),
            'is_active': True
        }
    )
    print(f"  ✓ Late Fee Rule: {rule.name}")
    return rule

def create_student(school, student_data, grades, sections, admin):
    """Create a student with user account"""
    email = f"{student_data['first_name'].lower()}.{student_data['last_name'].lower()}@student.school.com"
    
    # Check if user exists
    user = User.objects.filter(email=email).first()
    if not user:
        user = User.objects.create_user(
            email=email,
            password='student123',
            first_name=student_data['first_name'],
            last_name=student_data['last_name'],
            user_type='STUDENT',
            is_active=True
        )
    
    # Get grade 10 and section
    grade_10 = grades['Grade 10']
    section = sections[student_data['section']]
    
    # Check if student exists
    student = Student.objects.filter(user=user, school=school).first()
    if not student:
        student = Student.objects.create(
            user=user,
            school=school,
            gender=student_data['gender'],
            date_of_birth=date(2010, random.randint(1, 12), random.randint(1, 28)),
            current_grade=grade_10,
            current_section=section,
            admission_date=date(2013, 6, 1),  # Started in LKG
            status='ACTIVE'
        )
    
    print(f"  ✓ Student: {user.first_name} {user.last_name} ({student.suid}) - 10-{student_data['section']}")
    return student

def create_fee_history_for_student(student, school, grades, categories, schedule, admin, discount_type=None):
    """
    Create complete fee history from LKG to Grade 10
    """
    student_name = f"{student.user.first_name} {student.user.last_name}"
    print(f"\n    Creating fee history for {student_name}...")
    
    # Map grade names to academic years (student started LKG in 2013-2014)
    grade_year_map = {
        'LKG': '2013-2014',
        'UKG': '2014-2015',
        'Grade 1': '2015-2016',
        'Grade 2': '2016-2017',
        'Grade 3': '2017-2018',
        'Grade 4': '2018-2019',
        'Grade 5': '2019-2020',
        'Grade 6': '2020-2021',
        'Grade 7': '2021-2022',
        'Grade 8': '2022-2023',
        'Grade 9': '2023-2024',
        'Grade 10': '2024-2025',
    }
    
    for grade_name, academic_year in grade_year_map.items():
        # Get grade object
        grade = grades.get(grade_name)
        if not grade:
            continue
        
        fees = FEE_BY_GRADE.get(grade_name, {})
        total_annual_fee = sum(fees.values())
        
        # Create or get ledger for this year
        ledger, _ = FeeLedger.objects.get_or_create(
            student=student,
            school=school,
            academic_year=academic_year,
            defaults={
                'opening_balance': Decimal('0'),
                'total_charges': Decimal('0'),
                'total_payments': Decimal('0'),
                'total_discounts': Decimal('0'),
                'total_fines': Decimal('0'),
                'current_balance': Decimal('0'),
                'is_cleared': academic_year != '2024-2025'  # Only current year has balance
            }
        )
        
        if ledger.total_charges > 0:
            # Skip if already has data
            print(f"      Skipping {grade_name} ({academic_year}) - already has data")
            continue
        
        # Add fee charges
        charge_date = date(int(academic_year.split('-')[0]), 4, 1)  # April 1st
        
        running_balance = Decimal('0')
        for fee_type, fee_amount in fees.items():
            if fee_amount <= 0:
                continue
            
            cat_name = fee_type.replace('_', ' ').title()
            running_balance += Decimal(str(fee_amount))
            
            FeeLedgerEntry.objects.create(
                ledger=ledger,
                entry_type='CHARGE',
                date=charge_date,
                description=f'{cat_name} - {grade_name}',
                category=cat_name,
                reference_number=f'FEE-{academic_year}-{student.suid}',
                amount=Decimal(str(fee_amount)),
                balance_after=running_balance,
                created_by=admin
            )
        
        ledger.total_charges = Decimal(str(total_annual_fee))
        ledger.current_balance = running_balance
        
        # Apply discount if applicable
        discount_amount = Decimal('0')
        if discount_type and academic_year in ['2023-2024', '2024-2025']:
            discount_pct = {
                'MERIT': Decimal('15'),
                'SIBLING': Decimal('10'),
                'SCHOLARSHIP': Decimal('25'),
                'STAFF_CHILD': Decimal('50'),
                'FINANCIAL_AID': Decimal('30'),
            }.get(discount_type, Decimal('0'))
            
            if discount_pct > 0:
                discount_amount = (ledger.total_charges * discount_pct / 100).quantize(Decimal('0.01'))
                running_balance -= discount_amount
                
                # Create discount record
                discount_record = DiscountRecord.objects.create(
                    student=student,
                    school=school,
                    academic_year=academic_year,
                    discount_type=discount_type,
                    name=f'{discount_type.replace("_", " ").title()} Discount',
                    is_percentage=True,
                    percentage=discount_pct,
                    calculated_amount=discount_amount,
                    valid_from=charge_date,
                    reason=f'Student eligible for {discount_type.lower()} discount',
                    status='APPROVED',
                    requested_by=admin,
                    approved_by=admin,
                    approved_at=timezone.now()
                )
                
                # Add to ledger
                FeeLedgerEntry.objects.create(
                    ledger=ledger,
                    entry_type='DISCOUNT',
                    date=charge_date,
                    description=f'{discount_type.replace("_", " ").title()} Discount',
                    category='Discount',
                    amount=discount_amount,
                    balance_after=running_balance,
                    discount_record=discount_record,
                    created_by=admin
                )
                
                ledger.total_discounts = discount_amount
        
        # Record payments (for past years, fully paid; current year, partial)
        net_payable = ledger.total_charges - discount_amount
        
        if academic_year == '2024-2025':
            # Current year - partial payment (Q1, Q2, Q3 paid)
            paid_installments = 3
            amount_paid = (net_payable / 4 * paid_installments).quantize(Decimal('0.01'))
            
            for q in range(1, paid_installments + 1):
                q_amount = (net_payable / 4).quantize(Decimal('0.01'))
                payment_date = date(2024, 4 + (q-1)*3, 15)
                running_balance -= q_amount
                
                txn = Transaction.objects.create(
                    student=student,
                    school=school,
                    amount=q_amount,
                    payment_mode='CASH' if q % 2 == 0 else 'UPI',
                    reference_number=f'PAY-{academic_year}-Q{q}-{student.suid}',
                    transaction_date=timezone.make_aware(datetime.combine(payment_date, datetime.min.time())),
                    collected_by=admin,
                    status='COMPLETED'
                )
                
                FeeLedgerEntry.objects.create(
                    ledger=ledger,
                    entry_type='PAYMENT',
                    date=payment_date,
                    description=f'Q{q} Payment - {grade_name}',
                    category='Payment',
                    reference_number=txn.receipt_number,
                    amount=q_amount,
                    balance_after=running_balance,
                    transaction=txn,
                    created_by=admin
                )
            
            ledger.total_payments = amount_paid
        else:
            # Past years - fully paid
            payment_date = date(int(academic_year.split('-')[0]), 6, 15)
            running_balance -= net_payable
            
            txn = Transaction.objects.create(
                student=student,
                school=school,
                amount=net_payable,
                payment_mode='BANK_TRANSFER',
                reference_number=f'PAY-{academic_year}-{student.suid}',
                transaction_date=timezone.make_aware(datetime.combine(payment_date, datetime.min.time())),
                collected_by=admin,
                status='COMPLETED'
            )
            
            FeeLedgerEntry.objects.create(
                ledger=ledger,
                entry_type='PAYMENT',
                date=payment_date,
                description=f'Full Payment - {grade_name}',
                category='Payment',
                reference_number=txn.receipt_number,
                amount=net_payable,
                balance_after=running_balance,
                transaction=txn,
                created_by=admin
            )
            
            ledger.total_payments = net_payable
        
        # Update ledger with final values
        ledger.current_balance = running_balance
        ledger.is_cleared = running_balance <= 0
        ledger.save()
        
        status = "CLEARED" if running_balance <= 0 else "BALANCE DUE"
        balance = ledger.current_balance
        print(f"      ✓ {grade_name} ({academic_year}): ₹{ledger.total_charges} charged, "
              f"₹{ledger.total_payments} paid, Balance: ₹{balance} [{status}]")


def main():
    print("\n" + "="*60)
    print("FINANCE SEED DATA GENERATOR")
    print("="*60)
    
    # Get school
    print("\n1. Getting school...")
    school = get_school()
    print(f"   School: {school.name}")
    
    # Get admin
    admin = get_admin_user()
    print(f"   Admin: {admin.email if admin else 'None'}")
    
    # Ensure grades exist
    print("\n2. Creating grades (LKG to 10th)...")
    grades = ensure_grades_exist(school)
    
    # Ensure sections exist
    print("\n3. Creating sections for Grade 10...")
    sections = ensure_sections_exist(school, grades)
    
    # Ensure fee categories
    print("\n4. Creating fee categories...")
    categories = ensure_fee_categories(school)
    
    # Ensure fee schedule
    print("\n5. Creating fee schedule...")
    schedule = ensure_fee_schedule(school)
    
    # Create late fee rule
    print("\n6. Creating late fee rule...")
    late_fee_rule = ensure_late_fee_rule(school, admin)
    
    # Create students
    print("\n7. Creating students...")
    students = []
    for student_data in SAMPLE_STUDENTS:
        student = create_student(school, student_data, grades, sections, admin)
        students.append((student, student_data.get('discount')))
    
    # Create fee history for each student
    print("\n8. Creating fee history (LKG to Grade 10)...")
    for student, discount_type in students:
        create_fee_history_for_student(
            student, school, grades, categories, 
            schedule, admin, discount_type
        )
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  Total Students: {len(students)}")
    print(f"  Total Ledgers: {FeeLedger.objects.filter(school=school).count()}")
    print(f"  Total Ledger Entries: {FeeLedgerEntry.objects.count()}")
    print(f"  Total Transactions: {Transaction.objects.filter(school=school).count()}")
    print(f"  Total Discounts: {DiscountRecord.objects.filter(school=school).count()}")
    
    # Current year summary
    current_year = '2024-2025'
    current_ledgers = FeeLedger.objects.filter(school=school, academic_year=current_year)
    total_charges = sum(l.total_charges for l in current_ledgers)
    total_payments = sum(l.total_payments for l in current_ledgers)
    total_outstanding = sum(l.current_balance for l in current_ledgers)
    
    print(f"\n  Current Year ({current_year}):")
    print(f"    Total Fees: ₹{total_charges:,.2f}")
    print(f"    Total Collected: ₹{total_payments:,.2f}")
    print(f"    Total Outstanding: ₹{total_outstanding:,.2f}")
    if total_charges > 0:
        print(f"    Collection Rate: {(total_payments/total_charges*100):.1f}%")
    
    print("\n✅ Seed data created successfully!")
    print("="*60)


if __name__ == '__main__':
    main()