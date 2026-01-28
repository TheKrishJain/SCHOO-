"""
Seed script for Fee Management System
Creates sample fee schedules, structures, and assigns fees to students

Run: python manage.py shell < seed_fee_data.py
Or:  python seed_fee_data.py (if Django settings configured)
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone

from apps.finance.models import (
    FeeSchedule, FeeStructure, StudentFeeAssignment, 
    FeeInstallment, FeeCategory, FeeHikeConfig, Invoice
)
from apps.schools.models import School
from apps.students.models import Student
from apps.academics.models import Grade
from apps.accounts.models import User


def create_fee_schedules(school):
    """Create different fee payment schedules"""
    print("\n📅 Creating Fee Schedules...")
    
    schedules_data = [
        {
            'name': 'Quarterly Payment',
            'schedule_type': 'QUARTERLY',
            'description': 'Pay fees every 3 months (4 installments per year)',
            'installments_per_year': 4,
            'discount_percentage': Decimal('0'),
            'late_fee_per_day': Decimal('50'),
            'grace_period_days': 7,
            'max_late_fee': Decimal('1000'),
            'is_default': True,
        },
        {
            'name': 'Half-Yearly Payment',
            'schedule_type': 'HALF_YEARLY',
            'description': 'Pay fees every 6 months (2 installments per year). Get 2% discount!',
            'installments_per_year': 2,
            'discount_percentage': Decimal('2'),
            'late_fee_per_day': Decimal('100'),
            'grace_period_days': 10,
            'max_late_fee': Decimal('2000'),
            'is_default': False,
        },
        {
            'name': 'Annual Payment',
            'schedule_type': 'YEARLY',
            'description': 'Pay full fees at once. Get 5% discount!',
            'installments_per_year': 1,
            'discount_percentage': Decimal('5'),
            'late_fee_per_day': Decimal('200'),
            'grace_period_days': 15,
            'max_late_fee': Decimal('5000'),
            'is_default': False,
        },
        {
            'name': 'Monthly Payment',
            'schedule_type': 'MONTHLY',
            'description': 'Pay fees every month (12 installments per year)',
            'installments_per_year': 12,
            'discount_percentage': Decimal('0'),
            'late_fee_per_day': Decimal('25'),
            'grace_period_days': 5,
            'max_late_fee': Decimal('500'),
            'is_default': False,
        },
        {
            'name': 'Per Exam Payment',
            'schedule_type': 'PER_EXAM',
            'description': 'Pay before each exam (Term 1, Term 2, Final)',
            'installments_per_year': 3,
            'discount_percentage': Decimal('0'),
            'late_fee_per_day': Decimal('75'),
            'grace_period_days': 7,
            'max_late_fee': Decimal('1500'),
            'is_default': False,
        },
    ]
    
    created_schedules = []
    for data in schedules_data:
        schedule, created = FeeSchedule.objects.get_or_create(
            school=school,
            name=data['name'],
            defaults={**data, 'school': school}
        )
        created_schedules.append(schedule)
        status = "✅ Created" if created else "⏩ Exists"
        print(f"  {status}: {schedule.name} ({schedule.get_schedule_type_display()})")
    
    return created_schedules


def create_fee_structures(school, academic_year="2025-2026"):
    """Create grade-wise fee structures"""
    print(f"\n💰 Creating Fee Structures for {academic_year}...")
    
    # Get all grades for the school
    grades = Grade.objects.filter(school=school).order_by('grade_number')
    
    if not grades.exists():
        print("  ⚠️ No grades found. Creating sample grades...")
        for i in range(1, 13):
            Grade.objects.get_or_create(
                school=school,
                grade_number=i,
                defaults={'grade_name': f'Grade {i}'}
            )
        grades = Grade.objects.filter(school=school).order_by('grade_number')
    
    # Fee structure varies by grade level
    # Lower grades: Less fees
    # Higher grades: More fees (labs, computers, etc.)
    
    base_fees = {
        # Grade range: (tuition, exam, lab, library, sports, computer, transport, misc, development)
        (1, 5): (35000, 2000, 0, 1000, 2000, 1500, 12000, 1500, 5000),       # Primary
        (6, 8): (45000, 3000, 2000, 1500, 2500, 3000, 12000, 2000, 6000),    # Middle
        (9, 10): (55000, 4000, 4000, 2000, 3000, 4000, 12000, 2500, 7000),   # Secondary
        (11, 12): (65000, 5000, 6000, 2500, 3500, 5000, 12000, 3000, 8000),  # Senior Secondary
    }
    
    created_structures = []
    
    for grade in grades:
        # Find the right fee tier
        fees = None
        for (min_g, max_g), fee_tuple in base_fees.items():
            if min_g <= grade.grade_number <= max_g:
                fees = fee_tuple
                break
        
        if not fees:
            fees = base_fees[(1, 5)]  # Default to primary fees
        
        structure, created = FeeStructure.objects.get_or_create(
            school=school,
            grade=grade,
            academic_year=academic_year,
            defaults={
                'name': f'{grade.grade_name} Fee Structure {academic_year}',
                'tuition_fee': Decimal(fees[0]),
                'admission_fee': Decimal('5000'),  # One-time, same for all
                'exam_fee': Decimal(fees[1]),
                'lab_fee': Decimal(fees[2]),
                'library_fee': Decimal(fees[3]),
                'sports_fee': Decimal(fees[4]),
                'computer_fee': Decimal(fees[5]),
                'transport_fee': Decimal(fees[6]),
                'misc_fee': Decimal(fees[7]),
                'development_fee': Decimal(fees[8]),
            }
        )
        created_structures.append(structure)
        status = "✅ Created" if created else "⏩ Exists"
        print(f"  {status}: {grade.grade_name} - Total: ₹{structure.total_annual_fee:,.2f}")
    
    return created_structures


def create_fee_categories(school):
    """Create fee categories for invoicing"""
    print("\n🏷️ Creating Fee Categories...")
    
    categories_data = [
        ('Tuition Fee', 0, 'Monthly/Term tuition fee', True),
        ('Admission Fee', 5000, 'One-time admission fee', False),
        ('Exam Fee', 0, 'Examination charges', True),
        ('Lab Fee', 0, 'Laboratory usage charges', True),
        ('Library Fee', 0, 'Library membership and maintenance', True),
        ('Sports Fee', 0, 'Sports and PE activities', True),
        ('Computer Fee', 0, 'Computer lab usage', True),
        ('Transport Fee', 0, 'School bus service', True),
        ('Development Fee', 0, 'Infrastructure development', True),
        ('Late Fee', 0, 'Late payment penalty', False),
        ('Re-admission Fee', 2000, 'Re-admission after gap', False),
        ('Transfer Certificate Fee', 500, 'TC issuance charges', False),
    ]
    
    created_categories = []
    for name, amount, desc, recurring in categories_data:
        # First check if it exists by name and school
        existing = FeeCategory.objects.filter(school=school, name=name).first()
        if existing:
            print(f"  ⏩ Exists: {name}")
            created_categories.append(existing)
            continue
        
        # Also check if exists by name without school (old data)
        existing_no_school = FeeCategory.objects.filter(name=name, school__isnull=True).first()
        if existing_no_school:
            # Update existing to add school
            existing_no_school.school = school
            existing_no_school.description = desc
            existing_no_school.is_recurring = recurring
            existing_no_school.save()
            print(f"  🔄 Updated: {name} (added school)")
            created_categories.append(existing_no_school)
            continue
        
        # Create new
        try:
            category = FeeCategory.objects.create(
                school=school,
                name=name,
                amount=Decimal(amount),
                description=desc,
                is_recurring=recurring,
            )
            created_categories.append(category)
            print(f"  ✅ Created: {name}")
        except Exception as e:
            print(f"  ⚠️ Error creating {name}: {e}")
    
    return created_categories


def assign_fees_to_students(school, academic_year="2025-2026"):
    """Assign fees to existing students"""
    print(f"\n👨‍🎓 Assigning Fees to Students for {academic_year}...")
    
    students = Student.objects.filter(school=school, status='ACTIVE')
    
    if not students.exists():
        print("  ⚠️ No active students found. Skipping fee assignment.")
        return []
    
    # Get default schedule
    default_schedule = FeeSchedule.objects.filter(school=school, is_default=True).first()
    if not default_schedule:
        default_schedule = FeeSchedule.objects.filter(school=school).first()
    
    if not default_schedule:
        print("  ⚠️ No fee schedule found. Please create schedules first.")
        return []
    
    created_assignments = []
    
    for student in students[:20]:  # Limit to first 20 for demo
        # Get fee structure for student's grade
        structure = FeeStructure.objects.filter(
            school=school,
            grade=student.current_grade,
            academic_year=academic_year
        ).first()
        
        if not structure:
            print(f"  ⚠️ No fee structure for {student.current_grade}. Skipping {student.suid}")
            continue
        
        # Check if already assigned
        existing = StudentFeeAssignment.objects.filter(
            student=student,
            academic_year=academic_year
        ).first()
        
        if existing:
            print(f"  ⏩ Already assigned: {student.user.full_name} ({student.suid})")
            continue
        
        # Assign fees with some random variations
        import random
        
        # Some students get scholarships
        scholarship = Decimal('0')
        if random.random() < 0.1:  # 10% students get scholarship
            scholarship = Decimal(random.choice([10, 15, 20, 25, 50]))
        
        # Some siblings get discount
        sibling_discount = Decimal('0')
        if random.random() < 0.05:  # 5% get sibling discount
            sibling_discount = Decimal(random.randint(2000, 5000))
        
        assignment = StudentFeeAssignment.objects.create(
            student=student,
            school=school,
            fee_structure=structure,
            fee_schedule=default_schedule,
            academic_year=academic_year,
            scholarship_percentage=scholarship,
            sibling_discount=sibling_discount,
            discount_reason="Merit scholarship" if scholarship > 0 else "",
        )
        
        # Generate installments
        generate_installments(assignment)
        
        created_assignments.append(assignment)
        discount_info = f" (Scholarship: {scholarship}%)" if scholarship > 0 else ""
        print(f"  ✅ Assigned: {student.user.full_name} - ₹{assignment.net_payable:,.2f}{discount_info}")
    
    return created_assignments


def generate_installments(assignment):
    """Generate fee installments for an assignment"""
    schedule = assignment.fee_schedule
    if not schedule:
        return
    
    # Installment names based on schedule type
    names = {
        'MONTHLY': [f'Month {i} ({["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"][i-1]})' for i in range(1, 13)],
        'QUARTERLY': ['Q1 (Apr-Jun)', 'Q2 (Jul-Sep)', 'Q3 (Oct-Dec)', 'Q4 (Jan-Mar)'],
        'HALF_YEARLY': ['H1 (Apr-Sep)', 'H2 (Oct-Mar)'],
        'YEARLY': ['Annual Fee'],
        'PER_EXAM': ['Term 1 Exam', 'Term 2 Exam', 'Final Exam'],
    }
    
    installment_names = names.get(schedule.schedule_type, [f'Installment {i}' for i in range(1, schedule.installments_per_year + 1)])
    
    # Due dates based on schedule type
    start_year = int(assignment.academic_year.split('-')[0])
    
    due_dates = {
        'MONTHLY': [date(start_year if m <= 12 else start_year + 1, m if m <= 12 else m - 12, 15) 
                    for m in range(4, 16)],  # Apr to Mar
        'QUARTERLY': [date(start_year, 4, 15), date(start_year, 7, 15), 
                      date(start_year, 10, 15), date(start_year + 1, 1, 15)],
        'HALF_YEARLY': [date(start_year, 4, 15), date(start_year, 10, 15)],
        'YEARLY': [date(start_year, 4, 15)],
        'PER_EXAM': [date(start_year, 7, 1), date(start_year, 11, 1), date(start_year + 1, 2, 1)],
    }
    
    dates = due_dates.get(schedule.schedule_type, [])
    amount_per_installment = assignment.per_installment_fee
    
    for i, (name, due_date) in enumerate(zip(installment_names, dates), 1):
        FeeInstallment.objects.get_or_create(
            fee_assignment=assignment,
            installment_number=i,
            defaults={
                'installment_name': name,
                'amount_due': amount_per_installment,
                'due_date': due_date,
            }
        )


def create_sample_invoices(school, academic_year="2025-2026"):
    """Create some sample invoices with payments"""
    print("\n📄 Creating Sample Invoices...")
    
    assignments = StudentFeeAssignment.objects.filter(
        school=school,
        academic_year=academic_year
    ).select_related('student')[:10]  # First 10 students
    
    from apps.finance.models import Transaction
    import random
    
    for assignment in assignments:
        # Get first pending installment
        installment = assignment.installments.filter(status='PENDING').first()
        if not installment:
            continue
        
        # Create invoice
        invoice, created = Invoice.objects.get_or_create(
            student=assignment.student,
            fee_assignment=assignment,
            installment=installment,
            defaults={
                'school': school,
                'academic_year': academic_year,
                'total_amount': installment.amount_due,
                'due_date': installment.due_date,
            }
        )
        
        if created:
            # Randomly add some payments
            if random.random() < 0.6:  # 60% chance of payment
                payment_amount = installment.amount_due if random.random() < 0.7 else installment.amount_due / 2
                
                Transaction.objects.create(
                    invoice=invoice,
                    amount=payment_amount,
                    payment_mode=random.choice(['CASH', 'UPI', 'BANK_TRANSFER']),
                    reference_id=f'REF{random.randint(100000, 999999)}',
                )
                
                # Update installment status
                if payment_amount >= installment.amount_due:
                    installment.status = 'PAID'
                    installment.paid_date = timezone.now().date()
                else:
                    installment.status = 'PARTIAL'
                installment.amount_paid = payment_amount
                installment.save()
                
                print(f"  ✅ Invoice {invoice.invoice_number}: ₹{payment_amount:,.2f} paid")
            else:
                print(f"  📋 Invoice {invoice.invoice_number}: Pending (₹{invoice.total_amount:,.2f})")


def create_fee_hike_config(school):
    """Create a sample fee hike configuration"""
    print("\n📈 Creating Fee Hike Configuration...")
    
    hike, created = FeeHikeConfig.objects.get_or_create(
        school=school,
        from_academic_year="2025-2026",
        to_academic_year="2026-2027",
        defaults={
            'name': '2026-27 Annual Fee Revision',
            'hike_percentage': Decimal('8'),
            'tuition_hike': Decimal('10'),
            'transport_hike': Decimal('5'),
            'effective_date': date(2026, 4, 1),
            'notes': 'Annual fee revision as per school policy. Tuition increased by 10%, transport by 5%.',
        }
    )
    
    status = "✅ Created" if created else "⏩ Exists"
    print(f"  {status}: {hike.name} ({hike.hike_percentage}% overall hike)")


def main():
    print("=" * 60)
    print("🏫 FEE MANAGEMENT SYSTEM - SEED DATA")
    print("=" * 60)
    
    # Get first school
    school = School.objects.first()
    
    if not school:
        print("\n⚠️ No school found! Creating a sample school...")
        school = School.objects.create(
            name="Demo School",
            code="DEMO",
            email="demo@school.com",
            phone="9876543210",
            address="123 Education Street"
        )
        print(f"  ✅ Created: {school.name}")
    
    print(f"\n📍 Using School: {school.name}")
    
    # Create all fee data
    create_fee_schedules(school)
    create_fee_structures(school, "2025-2026")
    create_fee_categories(school)
    assign_fees_to_students(school, "2025-2026")
    create_sample_invoices(school, "2025-2026")
    create_fee_hike_config(school)
    
    print("\n" + "=" * 60)
    print("✅ FEE MANAGEMENT SEED DATA COMPLETE!")
    print("=" * 60)
    
    # Summary
    print("\n📊 Summary:")
    print(f"  • Fee Schedules: {FeeSchedule.objects.filter(school=school).count()}")
    print(f"  • Fee Structures: {FeeStructure.objects.filter(school=school).count()}")
    print(f"  • Fee Categories: {FeeCategory.objects.filter(school=school).count()}")
    print(f"  • Student Assignments: {StudentFeeAssignment.objects.filter(school=school).count()}")
    print(f"  • Invoices: {Invoice.objects.filter(school=school).count()}")
    
    print("\n🔗 API Endpoints:")
    print("  • GET  /api/v1/finance/schedules/        - List fee schedules")
    print("  • GET  /api/v1/finance/structures/       - List fee structures")
    print("  • GET  /api/v1/finance/assignments/      - List student fee assignments")
    print("  • POST /api/v1/finance/assignments/bulk_assign/  - Bulk assign fees")
    print("  • GET  /api/v1/finance/installments/     - List installments")
    print("  • GET  /api/v1/finance/invoices/         - List invoices")
    print("  • POST /api/v1/finance/invoices/{id}/record_payment/  - Record payment")


if __name__ == '__main__':
    main()
