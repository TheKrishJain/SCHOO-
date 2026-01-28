# 🚀 PostgreSQL Quick Setup - School-OS

## Option 1: Automated Setup (Recommended)

### Run PowerShell Script
```powershell
cd backend
.\setup_postgresql.ps1
```

**This script will:**
- ✅ Create database `school_os`
- ✅ Create user `school_os_user`
- ✅ Update `.env` file
- ✅ Install `psycopg2-binary`
- ✅ Backup SQLite data
- ✅ Migrate to PostgreSQL
- ✅ Load data

---

## Option 2: Interactive Setup

### Run Python Helper
```powershell
cd backend
python setup_postgres_helper.py
```

Follow the prompts to configure.

---

## Option 3: Manual Setup (5 minutes)

### 1. Install PostgreSQL Driver
```powershell
pip install psycopg2-binary
```

### 2. Open SQL Shell (psql)
Search "SQL Shell (psql)" in Windows Start

### 3. Run SQL Commands
```sql
CREATE DATABASE school_os;
CREATE USER school_os_user WITH PASSWORD 'SchoolOS2026!Secure';
GRANT ALL PRIVILEGES ON DATABASE school_os TO school_os_user;
ALTER DATABASE school_os OWNER TO school_os_user;
\q
```

### 4. Update .env File
Create/edit `backend\.env`:
```env
DATABASE_URL=postgresql://school_os_user:SchoolOS2026!Secure@localhost:5432/school_os
```

### 5. Migrate
```powershell
python manage.py migrate
```

### 6. Test
```powershell
python manage.py runserver
```

---

## Migrate Existing Data from SQLite

### Backup SQLite
```powershell
python manage.py dumpdata --natural-foreign --natural-primary --exclude=contenttypes > backup.json
```

### Switch to PostgreSQL
Update `.env` with PostgreSQL URL

### Migrate & Load
```powershell
python manage.py migrate
python manage.py loaddata backup.json
```

### Verify
```powershell
python manage.py shell
```
```python
from apps.students.models import Student
print(Student.objects.count())  # Should be 739
```

---

## Quick Check Commands

### Test Connection
```powershell
psql -U school_os_user -d school_os -h localhost
# Enter password: SchoolOS2026!Secure
```

### Check Database Size
```sql
SELECT pg_size_pretty(pg_database_size('school_os'));
```

### List Tables
```sql
\dt
```

### Active Connections
```sql
SELECT count(*) FROM pg_stat_activity WHERE datname = 'school_os';
```

---

## Troubleshooting

### "psql not recognized"
Add to PATH: `C:\Program Files\PostgreSQL\16\bin`

### "Connection refused"
Start PostgreSQL:
```powershell
net start postgresql-x64-16
```

### "Authentication failed"
Check password in `.env` matches database user password

### Migration errors
Run with verbose:
```powershell
python manage.py migrate --verbosity 3
```

---

## Switching Between SQLite and PostgreSQL

### Use SQLite (Development)
In `.env`:
```env
DATABASE_URL=sqlite:///db.sqlite3
```

### Use PostgreSQL (Production)
In `.env`:
```env
DATABASE_URL=postgresql://school_os_user:password@localhost:5432/school_os
```

No code changes needed! Just update `.env` and restart server.

---

## Default Credentials

| Setting | Value |
|---------|-------|
| Database | school_os |
| Username | school_os_user |
| Password | SchoolOS2026!Secure |
| Host | localhost |
| Port | 5432 |

⚠️ **Change password in production!**

---

## Performance Check

After setup:
```python
import time
from apps.students.models import Student

start = time.time()
count = Student.objects.count()
print(f"Query: {time.time() - start:.3f}s")
# Should be < 0.1 seconds
```

---

## Documentation Files

- `POSTGRESQL_MANUAL_SETUP.md` - Detailed manual instructions
- `POSTGRESQL_SETUP.py` - Configuration examples & guide
- `setup_postgresql.ps1` - Automated PowerShell script
- `setup_postgres_helper.py` - Interactive Python helper

---

**Status:** PostgreSQL configuration ready ✅  
**Next:** Complete setup using one of the three options above
