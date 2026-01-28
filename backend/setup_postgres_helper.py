"""
Quick PostgreSQL Setup Helper
Run: python setup_postgres_helper.py
"""

import os
import sys
import subprocess

print("=" * 60)
print("PostgreSQL Setup Helper for School-OS v2.0")
print("=" * 60)
print()

# Check if PostgreSQL is installed
def check_postgresql():
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL found: {result.stdout.strip()}")
            return True
        else:
            print("❌ PostgreSQL not found")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL not found in PATH")
        return False

# Check if psycopg2 is installed
def check_psycopg2():
    try:
        import psycopg2
        print(f"✅ psycopg2 installed: {psycopg2.__version__}")
        return True
    except ImportError:
        print("❌ psycopg2 not installed")
        return False

# Install psycopg2
def install_psycopg2():
    print("\nInstalling psycopg2-binary...")
    result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'psycopg2-binary'])
    return result.returncode == 0

# Create .env file
def create_env_file():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if os.path.exists(env_path):
        print(f"\n⚠️  .env file already exists at: {env_path}")
        response = input("Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Skipping .env creation")
            return False
    
    print("\n📝 Creating .env file...")
    print("Please provide the following details:")
    
    db_name = input("Database name [school_os]: ").strip() or "school_os"
    db_user = input("Database user [school_os_user]: ").strip() or "school_os_user"
    db_password = input("Database password [SchoolOS2026!Secure]: ").strip() or "SchoolOS2026!Secure"
    db_host = input("Database host [localhost]: ").strip() or "localhost"
    db_port = input("Database port [5432]: ").strip() or "5432"
    
    env_content = f"""# School-OS Backend Environment Configuration

# Django
SECRET_KEY=django-insecure-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
DATABASE_URL=postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}

# To switch back to SQLite, comment above and uncomment below:
# DATABASE_URL=sqlite:///db.sqlite3

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"✅ .env file created at: {env_path}")
    return True

# Show SQL commands
def show_sql_commands(db_name, db_user, db_password):
    print("\n" + "=" * 60)
    print("SQL Commands to Run in PostgreSQL")
    print("=" * 60)
    print("\nOpen 'SQL Shell (psql)' from Windows Start menu")
    print("Press Enter for defaults, then enter postgres password")
    print("\nThen copy and paste these commands:\n")
    
    print(f"CREATE DATABASE {db_name};")
    print(f"CREATE USER {db_user} WITH PASSWORD '{db_password}';")
    print(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};")
    print(f"ALTER DATABASE {db_name} OWNER TO {db_user};")
    print("\\q")
    
    print("\n" + "=" * 60)

# Main setup flow
def main():
    print("\nStep 1: Checking PostgreSQL installation...")
    if not check_postgresql():
        print("\n⚠️  Please install PostgreSQL first:")
        print("   https://www.postgresql.org/download/windows/")
        print("\nAfter installation, restart PowerShell and run this script again.")
        return
    
    print("\nStep 2: Checking psycopg2...")
    if not check_psycopg2():
        response = input("\nInstall psycopg2-binary now? (Y/n): ")
        if response.lower() != 'n':
            if install_psycopg2():
                print("✅ psycopg2-binary installed")
            else:
                print("❌ Installation failed")
                return
    
    print("\nStep 3: Environment configuration...")
    response = input("\nCreate/update .env file? (Y/n): ")
    if response.lower() != 'n':
        create_env_file()
    
    print("\nStep 4: Database setup...")
    print("\nYou need to create the PostgreSQL database manually.")
    show_sql = input("Show SQL commands? (Y/n): ")
    if show_sql.lower() != 'n':
        show_sql_commands("school_os", "school_os_user", "SchoolOS2026!Secure")
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Create the database using the SQL commands above")
    print("2. Run: python manage.py migrate")
    print("3. Run: python manage.py runserver")
    print("\nTo migrate data from SQLite, see POSTGRESQL_MANUAL_SETUP.md")
    print()

if __name__ == '__main__':
    main()
