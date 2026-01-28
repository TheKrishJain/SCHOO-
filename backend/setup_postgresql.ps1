# PostgreSQL Setup Script for School-OS
# Run this after installing PostgreSQL on Windows

# STEP 1: Open PowerShell as Administrator and run these commands

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PostgreSQL Setup for School-OS v2.0" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if PostgreSQL is installed
$pgPath = "C:\Program Files\PostgreSQL\16\bin\psql.exe"
if (-not (Test-Path $pgPath)) {
    Write-Host "❌ PostgreSQL not found at default location." -ForegroundColor Red
    Write-Host "Please install PostgreSQL from: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    Write-Host "Or update the path in this script if installed elsewhere." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ PostgreSQL found!" -ForegroundColor Green
Write-Host ""

# STEP 2: Create Database and User
Write-Host "Creating database and user..." -ForegroundColor Yellow
Write-Host "You will be prompted for the PostgreSQL 'postgres' user password." -ForegroundColor Yellow
Write-Host ""

$sqlCommands = @"
CREATE DATABASE school_os;
CREATE USER school_os_user WITH PASSWORD 'SchoolOS2026!Secure';
GRANT ALL PRIVILEGES ON DATABASE school_os TO school_os_user;
ALTER DATABASE school_os OWNER TO school_os_user;
"@

# Save SQL commands to temp file
$tempSqlFile = "$env:TEMP\setup_school_os.sql"
$sqlCommands | Out-File -FilePath $tempSqlFile -Encoding UTF8

# Execute SQL commands
& $pgPath -U postgres -f $tempSqlFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database 'school_os' created successfully!" -ForegroundColor Green
    Write-Host "✅ User 'school_os_user' created successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to create database. Check PostgreSQL is running." -ForegroundColor Red
    exit 1
}

# Clean up temp file
Remove-Item $tempSqlFile -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "STEP 3: Update .env file" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Create/update .env file
$envFile = Join-Path $PSScriptRoot ".env"
$envContent = @"
# Backend environment
SECRET_KEY=change-me-in-production
DEBUG=True

# PostgreSQL Database (ACTIVE)
DATABASE_URL=postgresql://school_os_user:SchoolOS2026!Secure@localhost:5432/school_os

# SQLite (Backup - Commented)
# DATABASE_URL=sqlite:///db.sqlite3

ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
"@

$envContent | Out-File -FilePath $envFile -Encoding UTF8

Write-Host "✅ .env file updated with PostgreSQL connection" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "STEP 4: Install Python PostgreSQL Driver" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "Installing psycopg2-binary..." -ForegroundColor Yellow
pip install psycopg2-binary

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ psycopg2-binary installed successfully!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Failed to install psycopg2-binary. Try manually:" -ForegroundColor Yellow
    Write-Host "   pip install psycopg2-binary" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "STEP 5: Migrate Data from SQLite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "Creating backup of SQLite data..." -ForegroundColor Yellow
$backupFile = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"

# Temporarily switch back to SQLite for backup
$envBackup = Get-Content $envFile
$envBackup -replace '^DATABASE_URL=postgresql.*', '# DATABASE_URL=postgresql://school_os_user:SchoolOS2026!Secure@localhost:5432/school_os' `
           -replace '^# DATABASE_URL=sqlite', 'DATABASE_URL=sqlite' | Out-File -FilePath $envFile -Encoding UTF8

python manage.py dumpdata --natural-foreign --natural-primary --exclude=contenttypes --exclude=auth.permission > $backupFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backup created: $backupFile" -ForegroundColor Green
} else {
    Write-Host "⚠️  Backup failed, but continuing..." -ForegroundColor Yellow
}

# Switch back to PostgreSQL
$envBackup | Out-File -FilePath $envFile -Encoding UTF8

Write-Host ""
Write-Host "Running migrations on PostgreSQL..." -ForegroundColor Yellow
python manage.py migrate

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ PostgreSQL migrations completed!" -ForegroundColor Green
} else {
    Write-Host "❌ Migration failed. Check logs above." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Loading data into PostgreSQL..." -ForegroundColor Yellow
if (Test-Path $backupFile) {
    python manage.py loaddata $backupFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Data loaded successfully!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Some data may not have loaded. Check manually." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ PostgreSQL Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Database Details:" -ForegroundColor Cyan
Write-Host "  Database: school_os" -ForegroundColor White
Write-Host "  Username: school_os_user" -ForegroundColor White
Write-Host "  Password: SchoolOS2026!Secure" -ForegroundColor White
Write-Host "  Host: localhost" -ForegroundColor White
Write-Host "  Port: 5432" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  IMPORTANT: Change the password in production!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Test server: python manage.py runserver" -ForegroundColor White
Write-Host "2. Verify data: Open http://localhost:8000/admin" -ForegroundColor White
Write-Host "3. Check student count matches original" -ForegroundColor White
Write-Host ""
