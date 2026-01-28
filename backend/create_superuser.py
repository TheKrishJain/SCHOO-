#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Create superuser if it doesn't exist
if not User.objects.filter(email='admin@school-os.com').exists():
    User.objects.create_superuser(
        email='admin@school-os.com',
        password='Admin@123456',
        first_name='Admin',
        last_name='User'
    )
    print("✓ Superuser created: admin@school-os.com / Admin@123456")
else:
    admin = User.objects.get(email='admin@school-os.com')
    admin.set_password('Admin@123456')
    admin.save()
    print("✓ Admin user already exists, password reset to: Admin@123456")

print("\nSuperuser Credentials:")
print("Email: admin@school-os.com")
print("Password: Admin@123456")
