# 💰 Fee Management System Documentation

## Overview

The Fee Management System allows school administrators to:
1. **Configure Fee Schedules** - Set up payment frequencies (Quarterly, Half-Yearly, Monthly, etc.)
2. **Define Fee Structures** - Set grade-wise fee amounts for each academic year
3. **Assign Fees to Students** - Bulk assign or individual assignment with discounts
4. **Manage Fee Hikes** - Configure yearly fee increases
5. **Generate Invoices** - Create and track payment invoices
6. **Track Payments** - Record and reconcile payments

---

## 📅 Fee Schedules

Fee schedules define **how often** students pay their fees.

### Available Schedule Types:
| Type | Installments/Year | Description |
|------|-------------------|-------------|
| **MONTHLY** | 12 | Pay every month |
| **QUARTERLY** | 4 | Pay every 3 months (Q1: Apr-Jun, Q2: Jul-Sep, Q3: Oct-Dec, Q4: Jan-Mar) |
| **HALF_YEARLY** | 2 | Pay every 6 months (H1: Apr-Sep, H2: Oct-Mar) |
| **YEARLY** | 1 | Pay once annually |
| **PER_EXAM** | 3 | Pay before each exam (Term 1, Term 2, Final) |

### Features:
- **Discount Percentage** - Reward for choosing longer payment terms (e.g., 5% for annual payment)
- **Late Fee Configuration** - Per-day late fee, grace period, maximum cap
- **Default Schedule** - Auto-assigned to new students

### API Example:
```json
POST /api/v1/finance/schedules/
{
  "school": "school-uuid",
  "name": "Quarterly Payment",
  "schedule_type": "QUARTERLY",
  "installments_per_year": 4,
  "discount_percentage": 0,
  "late_fee_per_day": 50,
  "grace_period_days": 7,
  "max_late_fee": 1000,
  "is_default": true
}
```

---

## 💵 Fee Structures

Fee structures define **how much** each grade pays.

### Fee Components:
- **Tuition Fee** - Main academic fee
- **Admission Fee** - One-time fee for new students
- **Exam Fee** - Examination charges
- **Lab Fee** - Laboratory usage
- **Library Fee** - Library services
- **Sports Fee** - Sports & PE activities
- **Computer Fee** - Computer lab usage
- **Transport Fee** - School bus service
- **Development Fee** - Infrastructure development
- **Misc Fee** - Other charges

### Sample Fee Structure (Grade 10):
```json
{
  "name": "Grade 10 Fee Structure 2025-26",
  "grade": "grade-uuid",
  "academic_year": "2025-2026",
  "tuition_fee": 55000,
  "admission_fee": 5000,
  "exam_fee": 4000,
  "lab_fee": 4000,
  "library_fee": 2000,
  "sports_fee": 3000,
  "computer_fee": 4000,
  "transport_fee": 12000,
  "misc_fee": 2500,
  "development_fee": 7000,
  "total_annual_fee": 98500  // Auto-calculated
}
```

---

## 👨‍🎓 Student Fee Assignment

Assigns a fee structure and schedule to students.

### Assignment Methods:

#### 1. Bulk Assignment (Recommended)
Assign fees to all students in a grade or section at once:

```json
POST /api/v1/finance/assignments/bulk_assign/
{
  "fee_structure_id": "structure-uuid",
  "fee_schedule_id": "schedule-uuid",
  "academic_year": "2025-2026",
  "grade_id": "grade-uuid",           // Optional: specific grade only
  "section_id": "section-uuid",        // Optional: specific section only
  "override_existing": false           // Skip students with existing assignments
}
```

Response:
```json
{
  "message": "Bulk assignment completed",
  "total_students": 150,
  "successful": 145,
  "failed": 0,
  "skipped": 5,
  "bulk_assignment_id": "uuid"
}
```

#### 2. Individual Assignment
For special cases with discounts/scholarships:

```json
POST /api/v1/finance/assignments/
{
  "student": "student-uuid",
  "school": "school-uuid",
  "fee_structure": "structure-uuid",
  "fee_schedule": "schedule-uuid",
  "academic_year": "2025-2026",
  "scholarship_percentage": 25,        // 25% scholarship
  "sibling_discount": 5000,            // ₹5000 sibling discount
  "special_discount": 2000,            // Other discount
  "discount_reason": "Merit scholarship + sibling discount",
  "requires_approval": true            // Needs admin approval
}
```

### Automatic Calculations:
- **Total Annual Fee** - From fee structure
- **Per Installment Fee** - Total ÷ installments
- **Net Payable** - After all discounts
- **Balance Due** - Net payable - paid amount

### Installments Auto-Generated:
When you create an assignment, installments are automatically created based on the schedule.

---

## 📈 Fee Hike Management

Configure and apply annual fee increases.

### Create Hike Config:
```json
POST /api/v1/finance/hike-configs/
{
  "school": "school-uuid",
  "name": "2026-27 Fee Revision",
  "from_academic_year": "2025-2026",
  "to_academic_year": "2026-2027",
  "hike_percentage": 8,
  "tuition_hike": 10,        // Optional: different hike for tuition
  "transport_hike": 5,       // Optional: different hike for transport
  "effective_date": "2026-04-01",
  "notes": "Annual fee revision as per school policy"
}
```

### Apply Hike:
```json
POST /api/v1/finance/hike-configs/{id}/apply_hike/
```

This will:
1. Copy all fee structures to the new academic year
2. Apply the hike percentage to each component
3. Mark the hike config as applied

### Copy Structures to Next Year:
```json
POST /api/v1/finance/structures/copy_to_next_year/
{
  "from_year": "2025-2026",
  "to_year": "2026-2027",
  "hike_percentage": 8,
  "school_id": "school-uuid"
}
```

---

## 🧾 Invoices & Payments

### Generate Invoice from Installment:
```json
POST /api/v1/finance/assignments/{id}/generate_invoice/
{
  "installment_id": "installment-uuid"  // Optional: auto-picks next pending
}
```

### Record Payment:
```json
POST /api/v1/finance/invoices/{id}/record_payment/
{
  "amount": 25000,
  "mode": "UPI",              // CASH, UPI, CHEQUE, BANK_TRANSFER, CARD
  "reference": "UPI12345678"  // Transaction reference
}
```

### Payment Tracking:
- Each payment creates a Transaction with receipt number
- Invoice status auto-updates (UNPAID → PARTIAL → PAID)
- Fee assignment balance auto-updates
- Installment status auto-updates

---

## 📊 Dashboard Statistics

```json
GET /api/v1/finance/invoices/dashboard_stats/?school={id}&academic_year=2025-2026
```

Response:
```json
{
  "total_invoiced": 15000000,
  "total_collected": 12000000,
  "total_pending": 3000000,
  "by_status": {
    "PAID": 450,
    "PARTIAL": 75,
    "UNPAID": 100,
    "OVERDUE": 25
  }
}
```

---

## 🔄 Typical Workflow

### Beginning of Academic Year:
1. **Create Fee Schedules** (if not exists)
2. **Copy Fee Structures** from previous year with hike
3. **Bulk Assign Fees** to all students by grade
4. **Handle Special Cases** - Individual discounts, scholarships

### During Academic Year:
1. **Generate Invoices** as installments come due
2. **Record Payments** as received
3. **Track Overdue** - Run check_overdue periodically
4. **Handle Late Fees** if applicable

### End of Year:
1. **Review Outstanding** balances
2. **Plan Fee Hike** for next year
3. **Copy Structures** with new fees

---

## 🛠️ Admin Panel

All models are registered in Django Admin with:
- Colored status indicators
- Inline installments on assignments
- Filter by school, year, status
- Search by student name/SUID
- Read-only calculated fields

Access at: `/admin/finance/`

---

## 📝 Sample Data

Run the seed script to create sample data:
```bash
cd backend
python seed_fee_data.py
```

This creates:
- 5 Fee Schedules (Quarterly, Half-Yearly, Annual, Monthly, Per-Exam)
- 12 Fee Structures (one per grade)
- 20 Student Assignments with installments
- 10 Sample Invoices with payments
- 1 Fee Hike Config for next year
