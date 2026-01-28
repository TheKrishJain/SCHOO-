# Manual PostgreSQL Setup Instructions
# If the automated script doesn't work, follow these steps

## STEP 1: Install PostgreSQL
1. Download from: https://www.postgresql.org/download/windows/
2. Run installer, remember the password you set for 'postgres' user
3. Default port: 5432
4. Add PostgreSQL bin to PATH (installer should do this)

## STEP 2: Open SQL Shell (psql)
Search for "SQL Shell (psql)" in Windows Start menu

## STEP 3: Create Database
When prompted, press Enter for defaults except password.
Then run these commands:

```sql
CREATE DATABASE school_os;
CREATE USER school_os_user WITH PASSWORD 'SchoolOS2026!Secure';
GRANT ALL PRIVILEGES ON DATABASE school_os TO school_os_user;
ALTER DATABASE school_os OWNER TO school_os_user;
\q
```

## STEP 4: Install Python Driver
Open PowerShell in backend directory:
```powershell
pip install psycopg2-binary
```

## STEP 5: Update .env File
Edit `backend\.env` file:

```env
# Change this line:
DATABASE_URL=sqlite:///db.sqlite3

# To this:
DATABASE_URL=postgresql://school_os_user:SchoolOS2026!Secure@localhost:5432/school_os
```

## STEP 6: Backup SQLite Data
```powershell
# Backup current data
python manage.py dumpdata --natural-foreign --natural-primary --exclude=contenttypes --exclude=auth.permission > backup.json
```

## STEP 7: Run Migrations on PostgreSQL
```powershell
python manage.py migrate
```

## STEP 8: Load Data
```powershell
python manage.py loaddata backup.json
```

## STEP 9: Verify
```powershell
python manage.py shell
```

In Python shell:
```python
from apps.students.models import Student
print(f"Total students: {Student.objects.count()}")
# Should show 739

from apps.enrollments.models import StudentEnrollment
print(f"Active: {StudentEnrollment.objects.filter(status='ACTIVE').count()}")
print(f"Graduated: {StudentEnrollment.objects.filter(status='GRADUATED').count()}")
# Should show 539 active, 180 graduated

exit()
```

## STEP 10: Test Server
```powershell
python manage.py runserver
```

Visit http://localhost:8000/admin and login to verify data.

## Troubleshooting

### "psql is not recognized"
Add PostgreSQL bin to PATH:
1. Search "Environment Variables" in Windows
2. Edit System PATH
3. Add: `C:\Program Files\PostgreSQL\16\bin`
4. Restart PowerShell

### "psycopg2 installation failed"
Try binary version:
```powershell
pip install psycopg2-binary
```

### "Connection refused"
Check PostgreSQL is running:
```powershell
# Start PostgreSQL service
net start postgresql-x64-16
```

### "Authentication failed"
Check password in .env matches what you created

### "loaddata failed"
Some data may have dependencies. Try loading in order:
```powershell
python manage.py loaddata auth.json
python manage.py loaddata accounts.json
python manage.py loaddata schools.json
python manage.py loaddata students.json
# ... etc
```

Or load without auth/contenttypes:
```powershell
python manage.py dumpdata --exclude=contenttypes --exclude=auth.permission > backup_clean.json
python manage.py loaddata backup_clean.json
```

## Performance Check

After setup, run:
```powershell
python manage.py shell
```

```python
import time
from apps.students.models import Student

# Test query speed
start = time.time()
count = Student.objects.count()
elapsed = time.time() - start

print(f"Query time: {elapsed:.3f} seconds")
# Should be < 0.1 seconds for 739 students
```

## Connection String Format

PostgreSQL:
```
DATABASE_URL=postgresql://username:password@host:port/database
```

Examples:
```
# Local
DATABASE_URL=postgresql://school_os_user:password@localhost:5432/school_os

# Remote
DATABASE_URL=postgresql://user:pass@192.168.1.100:5432/school_os

# With special characters in password (URL encode)
DATABASE_URL=postgresql://user:p%40ssw0rd@localhost:5432/school_os
```

## Backup Strategy

Create weekly backups:
```powershell
# Create backup script: backup.ps1
$date = Get-Date -Format "yyyyMMdd_HHmmss"
$env:PGPASSWORD = "SchoolOS2026!Secure"
pg_dump -U school_os_user -h localhost school_os > "backups\school_os_$date.sql"
gzip "backups\school_os_$date.sql"
```

Schedule with Task Scheduler to run weekly.

## Production Checklist

Before deploying to production:

- [ ] Change database password
- [ ] Update SECRET_KEY in .env
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable SSL for database connection
- [ ] Set up automated backups
- [ ] Configure connection pooling
- [ ] Monitor query performance
- [ ] Set up database replication (optional)

## Need Help?

Check logs:
- Django: `backend/logs/django.log`
- PostgreSQL: `C:\Program Files\PostgreSQL\16\data\log\`

Test connection:
```powershell
psql -U school_os_user -d school_os -h localhost
# Enter password when prompted
# Should connect successfully
```
