"""
Proper Finance Seed Data Generator
===================================
This script creates finance data using the proper system flow:
1. Fee Structures (grade-wise fee definitions)
2. Fee Schedules (payment plans)
3. Students
4. Fee Assignments (link student to structure + schedule)
5. Invoices (generated from fee assignments)
6. Payments (recorded against invoices)
7. Ledger entries are auto-created via signals

This ensures data integrity and proper relationships.
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta
import random
import uuid

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.schools.models import School
from apps.academics.models import Grade, Section
from apps.enrollments.models_promotion import AcademicYear
from apps.students.models import Student
from apps.finance.models import (
    FeeCategory, FeeSchedule, FeeStructure, 
    StudentFeeAssignment, FeeInstallment,
    Invoice, Transaction, FeeLedger, FeeLedgerEntry
)

User = get_user_model()

print("\n" + "=" * 60)
print("PROPER FINANCE SEED DATA GENERATOR")
print("=" * 60)

# ============================================================
# 1. GET SCHOOL
# ============================================================
print("\n1. Getting Premier School...")

# Use Premier School (the one user is logged into)
school = School.objects.filter(name__icontains='Premier').first()
if not school:
    print("ERROR: Premier School not found!")
    sys.exit(1)

print(f"   ✓ School: {school.name}")

# Get admin user
admin_user = User.objects.filter(user_type='SCHOOL_ADMIN', school=school).first()
if not admin_user:
    admin_user = User.objects.filter(is_superuser=True).first()
print(f"   ✓ Admin: {admin_user.email if admin_user else 'None'}")

# ============================================================
# 2. CREATE ACADEMIC YEARS (if not exist)
# ============================================================
print("\n2. Setting up academic years...")

current_year = "2024-2025"
academic_years = [
    "2013-2014", "2014-2015", "2015-2016", "2016-2017",
    "2017-2018", "2018-2019", "2019-2020", "2020-2021",
    "2021-2022", "2022-2023", "2023-2024", "2024-2025"
]

for year in academic_years:
    start_year = int(year.split('-')[0])
    AcademicYear.objects.get_or_create(
        school=school,
        year_code=year,
        defaults={
            'start_date': date(start_year, 4, 1),
            'end_date': date(start_year + 1, 3, 31),
            'status': 'ACTIVE' if year == current_year else 'CLOSED'
        }
    )
print(f"   ✓ Academic years set up")

# ============================================================
# 3. CREATE GRADES (LKG to Grade 10)
# ============================================================
print("\n3. Creating grades...")

grade_data = [
    (0, "LKG", "Lower Kindergarten"),
    (1, "UKG", "Upper Kindergarten"),
    (2, "Grade 1", "Class 1"),
    (3, "Grade 2", "Class 2"),
    (4, "Grade 3", "Class 3"),
    (5, "Grade 4", "Class 4"),
    (6, "Grade 5", "Class 5"),
    (7, "Grade 6", "Class 6"),
    (8, "Grade 7", "Class 7"),
    (9, "Grade 8", "Class 8"),
    (10, "Grade 9", "Class 9"),
    (11, "Grade 10", "Class 10"),
]

grades = {}
for grade_num, name, desc in grade_data:
    # Try to find by school + grade_number first
    grade = Grade.objects.filter(school=school, grade_number=grade_num).first()
    if not grade:
        grade = Grade.objects.create(
            school=school,
            grade_name=name,
            grade_number=grade_num,
            is_active=True
        )
    grades[name] = grade
    print(f"   ✓ Grade: {name}")

# ============================================================
# 4. CREATE SECTIONS FOR GRADE 10
# ============================================================
print("\n4. Creating sections for Grade 10...")

grade_10 = grades["Grade 10"]
sections = []
for sec_name in ['A', 'B', 'C']:
    section, _ = Section.objects.get_or_create(
        school=school,
        grade=grade_10,
        section_letter=sec_name,
        defaults={'room_number': f'10{sec_name}', 'capacity': 50}
    )
    sections.append(section)
    print(f"   ✓ Section: 10-{sec_name}")

# ============================================================
# 5. CREATE FEE SCHEDULE (Quarterly Payment)
# ============================================================
print("\n5. Creating fee schedule...")

fee_schedule, _ = FeeSchedule.objects.get_or_create(
    school=school,
    name="Quarterly Payment Plan",
    defaults={
        'schedule_type': 'QUARTERLY',
        'description': 'Pay fees quarterly (every 3 months)',
        'installments_per_year': 4,
        'discount_percentage': Decimal('0'),
        'late_fee_per_day': Decimal('50'),
        'grace_period_days': 7,
        'max_late_fee': Decimal('500'),
        'is_default': True,
        'is_active': True
    }
)
print(f"   ✓ Fee Schedule: {fee_schedule.name}")

# ============================================================
# 6. CREATE FEE STRUCTURES (for each grade/year)
# ============================================================
print("\n6. Creating fee structures...")

# Base fees that increase each year
base_fees = {
    "LKG": 30000, "UKG": 28000, "Grade 1": 35000, "Grade 2": 37000,
    "Grade 3": 40000, "Grade 4": 42000, "Grade 5": 46000, "Grade 6": 52000,
    "Grade 7": 56000, "Grade 8": 60000, "Grade 9": 66000, "Grade 10": 75000
}

fee_structures = {}  # {grade_name: {year: structure}}
for grade_name, grade in grades.items():
    fee_structures[grade_name] = {}
    base = base_fees[grade_name]
    
    for i, year in enumerate(academic_years):
        # 5% hike each year
        annual_fee = int(base * (1.05 ** i))
        
        structure, _ = FeeStructure.objects.get_or_create(
            school=school,
            grade=grade,
            academic_year=year,
            defaults={
                'name': f'{grade_name} Fee Structure {year}',
                'tuition_fee': Decimal(str(int(annual_fee * 0.6))),
                'exam_fee': Decimal(str(int(annual_fee * 0.1))),
                'lab_fee': Decimal(str(int(annual_fee * 0.05))),
                'library_fee': Decimal(str(int(annual_fee * 0.05))),
                'sports_fee': Decimal(str(int(annual_fee * 0.05))),
                'computer_fee': Decimal(str(int(annual_fee * 0.05))),
                'misc_fee': Decimal(str(int(annual_fee * 0.1))),
                'total_annual_fee': Decimal(str(annual_fee)),
                'is_active': True
            }
        )
        fee_structures[grade_name][year] = structure

print(f"   ✓ Created fee structures for all grades and years")

# ============================================================
# 7. CREATE FEE CATEGORIES
# ============================================================
print("\n7. Creating fee categories...")

categories_data = [
    ("Tuition Fee", 45000, True),
    ("Exam Fee", 7500, True),
    ("Lab Fee", 3750, True),
    ("Library Fee", 3750, True),
    ("Sports Fee", 3750, True),
    ("Computer Fee", 3750, True),
    ("Miscellaneous", 7500, True),
]

fee_categories = {}
for name, amount, recurring in categories_data:
    cat, _ = FeeCategory.objects.get_or_create(
        school=school,
        name=name,
        defaults={
            'amount': Decimal(str(amount)),
            'description': f'{name} for the academic year',
            'is_recurring': recurring,
            'is_active': True
        }
    )
    fee_categories[name] = cat
    print(f"   ✓ Category: {name}")

# ============================================================
# 8. CREATE STUDENTS
# ============================================================
print("\n8. Creating students...")

student_names = [
    ("Aarav", "Sharma"), ("Ananya", "Patel"), ("Vihaan", "Singh"),
    ("Diya", "Gupta"), ("Arjun", "Kumar"), ("Ishaan", "Verma"),
    ("Saanvi", "Reddy"), ("Reyansh", "Joshi"), ("Myra", "Mehta"),
    ("Kabir", "Shah"), ("Aadya", "Nair"), ("Krishna", "Iyer"),
    ("Avni", "Rao"), ("Rudra", "Desai"), ("Prisha", "Bhat"),
]

students = []
for i, (first_name, last_name) in enumerate(student_names):
    section = sections[i % 3]  # Distribute across sections
    
    # Create user
    email = f"{first_name.lower()}.{last_name.lower()}@student.premier.edu"
    
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'user_type': 'STUDENT',
            'school': school,
            'is_active': True
        }
    )
    
    if created:
        user.set_password('student123')
        user.save()
    
    # Create student - their journey started in LKG (2013)
    student, _ = Student.objects.get_or_create(
        user=user,
        defaults={
            'school': school,
            'current_grade': grade_10,
            'current_section': section,
            'date_of_birth': date(2009, random.randint(1, 12), random.randint(1, 28)),
            'admission_date': date(2013, 6, 15),
            'status': 'ACTIVE',
            'gender': 'M' if i % 2 == 0 else 'F'
        }
    )
    
    students.append(student)
    print(f"   ✓ Student: {first_name} {last_name} ({student.suid}) - Section {section.section_letter}")

# ============================================================
# 9. CREATE FEE HISTORY WITH PROPER INVOICE FLOW
# ============================================================
print("\n9. Creating fee history with proper invoice flow...")

# Grade progression for each year
grade_progression = [
    ("2013-2014", "LKG"),
    ("2014-2015", "UKG"),
    ("2015-2016", "Grade 1"),
    ("2016-2017", "Grade 2"),
    ("2017-2018", "Grade 3"),
    ("2018-2019", "Grade 4"),
    ("2019-2020", "Grade 5"),
    ("2020-2021", "Grade 6"),
    ("2021-2022", "Grade 7"),
    ("2022-2023", "Grade 8"),
    ("2023-2024", "Grade 9"),
    ("2024-2025", "Grade 10"),
]

total_invoices = 0
total_payments = 0
total_ledgers = 0

for student in students:
    print(f"\n   Creating fee history for {student.user.first_name} {student.user.last_name}...")
    
    for year, grade_name in grade_progression:
        grade = grades[grade_name]
        structure = fee_structures[grade_name][year]
        annual_fee = structure.total_annual_fee
        is_current_year = (year == "2024-2025")
        
        start_year = int(year.split('-')[0])
        
        # ─────────────────────────────────────────────────────────
        # Step 1: Create Fee Ledger for this year
        # ─────────────────────────────────────────────────────────
        ledger, _ = FeeLedger.objects.get_or_create(
            student=student,
            school=school,
            academic_year=year,
            defaults={
                'opening_balance': Decimal('0'),
                'total_charges': Decimal('0'),
                'total_payments': Decimal('0'),
                'total_discounts': Decimal('0'),
                'total_fines': Decimal('0'),
                'current_balance': Decimal('0'),
                'is_cleared': False
            }
        )
        total_ledgers += 1
        
        # ─────────────────────────────────────────────────────────
        # Step 2: Create Fee Assignment
        # ─────────────────────────────────────────────────────────
        assignment, _ = StudentFeeAssignment.objects.get_or_create(
            student=student,
            academic_year=year,
            defaults={
                'school': school,
                'fee_structure': structure,
                'fee_schedule': fee_schedule,
                'total_annual_fee': annual_fee,
                'net_payable': annual_fee,
                'per_installment_fee': annual_fee / 4,
                'status': 'ACTIVE'
            }
        )
        
        # ─────────────────────────────────────────────────────────
        # Step 3: Create Quarterly Invoices
        # ─────────────────────────────────────────────────────────
        quarters = [
            (1, "Q1 - Apr-Jun", date(start_year, 4, 15), date(start_year, 4, 30)),
            (2, "Q2 - Jul-Sep", date(start_year, 7, 15), date(start_year, 7, 31)),
            (3, "Q3 - Oct-Dec", date(start_year, 10, 15), date(start_year, 10, 31)),
            (4, "Q4 - Jan-Mar", date(start_year + 1, 1, 15), date(start_year + 1, 1, 31)),
        ]
        
        quarterly_amount = annual_fee / 4
        
        for q_num, q_name, inv_date, due_date in quarters:
            # For current year, only Q1-Q3 have been invoiced (Q4 not yet due)
            if is_current_year and q_num == 4:
                continue
            
            # Create Invoice
            invoice = Invoice.objects.create(
                student=student,
                school=school,
                fee_assignment=assignment,
                ledger=ledger,
                academic_year=year,
                subtotal=quarterly_amount,
                total_amount=quarterly_amount,
                invoice_date=inv_date,
                due_date=due_date,
                status='UNPAID',
                description=f"{grade_name} - {q_name}",
                created_by=admin_user
            )
            total_invoices += 1
            
            # Add fee categories to invoice
            for cat in fee_categories.values():
                invoice.categories.add(cat)
            
            # Create CHARGE entry in ledger
            FeeLedgerEntry.objects.create(
                ledger=ledger,
                entry_type='CHARGE',
                date=inv_date,
                description=f"{grade_name} Fee - {q_name}",
                category="Tuition Fee",
                amount=quarterly_amount,
                invoice=invoice,
                balance_after=Decimal('0'),  # Will be recalculated
                created_by=admin_user
            )
            
            # ─────────────────────────────────────────────────────────
            # Step 4: Record Payment
            # ─────────────────────────────────────────────────────────
            if is_current_year:
                # Current year: only Q1 and Q2 paid, Q3 partially/unpaid
                if q_num == 1:
                    paid = quarterly_amount  # Fully paid
                elif q_num == 2:
                    paid = quarterly_amount  # Fully paid
                elif q_num == 3:
                    # Random: some fully paid, some partial, some unpaid
                    payment_scenario = random.choice(['full', 'partial', 'unpaid'])
                    if payment_scenario == 'full':
                        paid = quarterly_amount
                    elif payment_scenario == 'partial':
                        paid = quarterly_amount * Decimal(str(random.uniform(0.3, 0.7)))
                    else:
                        paid = Decimal('0')
                else:
                    paid = Decimal('0')
            else:
                # Past years: fully paid
                paid = quarterly_amount
            
            if paid > 0:
                # Determine payment date (a few days after invoice)
                payment_date = inv_date + timedelta(days=random.randint(5, 20))
                payment_mode = random.choice(['CASH', 'UPI', 'BANK_TRANSFER', 'CHEQUE'])
                
                # Create Transaction
                transaction = Transaction.objects.create(
                    invoice=invoice,
                    student=student,
                    school=school,
                    amount=paid,
                    payment_mode=payment_mode,
                    status='SUCCESS',
                    transaction_date=payment_date,
                    collected_by=admin_user,
                    notes=f"Payment for {q_name}"
                )
                total_payments += 1
                
                # Update invoice status
                invoice.paid_amount = paid
                if paid >= quarterly_amount:
                    invoice.status = 'PAID'
                    invoice.paid_date = payment_date
                else:
                    invoice.status = 'PARTIAL'
                invoice.save()
                
                # Create PAYMENT entry in ledger
                FeeLedgerEntry.objects.create(
                    ledger=ledger,
                    entry_type='PAYMENT',
                    date=payment_date,
                    description=f"Payment - {payment_mode} - {q_name}",
                    category="Payment",
                    amount=paid,
                    invoice=invoice,
                    transaction=transaction,
                    reference_number=transaction.receipt_number,
                    balance_after=Decimal('0'),  # Will be recalculated
                    created_by=admin_user
                )
        
        # Recalculate ledger
        ledger.recalculate()
        
        status = "CLEARED" if ledger.is_cleared else f"₹{ledger.current_balance} DUE"
        print(f"      ✓ {year} ({grade_name}): ₹{ledger.total_charges} charged, ₹{ledger.total_payments} paid [{status}]")

# ============================================================
# 10. SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

# Calculate current year stats
current_ledgers = FeeLedger.objects.filter(school=school, academic_year="2024-2025")
total_fees = sum(l.total_charges for l in current_ledgers)
total_collected = sum(l.total_payments for l in current_ledgers)
total_outstanding = sum(l.current_balance for l in current_ledgers)

current_invoices = Invoice.objects.filter(school=school, academic_year="2024-2025")
paid_invoices = current_invoices.filter(status='PAID').count()
partial_invoices = current_invoices.filter(status='PARTIAL').count()
unpaid_invoices = current_invoices.filter(status='UNPAID').count()

print(f"  Total Students: {len(students)}")
print(f"  Total Ledgers Created: {total_ledgers}")
print(f"  Total Invoices Created: {total_invoices}")
print(f"  Total Payments Recorded: {total_payments}")
print(f"\n  Current Year (2024-2025):")
print(f"    Total Fees: ₹{total_fees:,.2f}")
print(f"    Total Collected: ₹{total_collected:,.2f}")
print(f"    Total Outstanding: ₹{total_outstanding:,.2f}")
print(f"    Collection Rate: {(total_collected / total_fees * 100):.1f}%")
print(f"\n  Invoice Status:")
print(f"    Paid: {paid_invoices}")
print(f"    Partial: {partial_invoices}")
print(f"    Unpaid: {unpaid_invoices}")

print(f"\n✅ Seed data created successfully using proper invoice flow!")
print("=" * 60 + "\n")
