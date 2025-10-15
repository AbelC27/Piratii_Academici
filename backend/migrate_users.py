#!/usr/bin/env python3
"""
Migration script to move users from app.User to Django's auth.User
This fixes the login issue by moving users to the correct table.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PBMate.settings')
django.setup()

from app.models import User as CustomUser
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.hashers import make_password

print("=" * 60)
print("User Migration Script")
print("=" * 60)

# Get existing custom users
custom_users = CustomUser.objects.all()
print(f"\n📊 Found {custom_users.count()} user(s) in app_user table:")

migrated = 0
skipped = 0

for custom_user in custom_users:
    print(f"\n  Username: {custom_user.username}")
    print(f"  Email: {custom_user.email}")
    
    # Check if user already exists in auth_user
    if AuthUser.objects.filter(username=custom_user.username).exists():
        print(f"  ⚠️  User already exists in auth_user - skipping")
        skipped += 1
        continue
    
    # Create in Django's auth_user table
    # Note: The password is already hashed, so we use it directly
    auth_user = AuthUser(
        username=custom_user.username,
        email=custom_user.email,
        password=custom_user.password,  # Already hashed
        date_joined=custom_user.created_at
    )
    auth_user.save()
    migrated += 1
    print(f"  ✅ Migrated to auth_user")

print("\n" + "=" * 60)
print(f"✅ Migration complete!")
print(f"   • Migrated: {migrated} user(s)")
print(f"   • Skipped: {skipped} user(s)")
print("=" * 60)
print("\n💡 Note: You can now delete the custom User model from models.py")
print("   and use Django's built-in User model instead.\n")
