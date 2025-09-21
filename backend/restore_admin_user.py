#!/usr/bin/env python3
"""
Script to restore the original admin user account for ha@nextstepfwd.com
This script will create or update the user with admin privileges.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath('.')))

from app.core.db import get_database, connect_to_mongo
from app.core import security
from app.models.user import UserRole, UserStatus
from app.services.auth_service import authenticate_user

async def restore_admin_user():
    """Restore the original admin user account"""
    await connect_to_mongo()
    db = get_database()
    
    admin_email = 'ha@nextstepfwd.com'
    
    # Try the most likely original passwords based on code analysis
    potential_passwords = [
        "temp123",      # Found in create_temp_access.py and test_streamlined_filters_simple.py
        "password123",  # Found in test_follow_up_email_api.py
        "admin123",     # Common admin password pattern
        "password",     # Simple fallback
    ]
    
    print(f'🔍 Checking for existing admin user: {admin_email}')
    
    # Check if user already exists
    existing_user = await db.users.find_one({'email': admin_email})
    
    if existing_user:
        print(f'✅ User found in database:')
        print(f'   📧 Email: {existing_user.get("email")}')
        print(f'   🆔 ID: {existing_user.get("id")}')
        print(f'   👤 Role: {existing_user.get("role")}')
        print(f'   📊 Status: {existing_user.get("status")}')
        print(f'   🎯 Premium: {existing_user.get("is_premium")}')
        
        # Test existing passwords
        print(f'\n🔐 Testing existing passwords...')
        working_password = None
        
        for password in potential_passwords:
            print(f'   Testing password: {password}')
            auth_result = await authenticate_user(db, admin_email, password)
            if auth_result:
                print(f'   ✅ Password works: {password}')
                working_password = password
                break
            else:
                print(f'   ❌ Password failed: {password}')
        
        if working_password:
            # Update user to ensure admin role
            await db.users.update_one(
                {'email': admin_email},
                {
                    '$set': {
                        'role': UserRole.admin.value,
                        'status': UserStatus.active.value,
                        'must_change_password': False,
                        'last_login': datetime.utcnow()
                    }
                }
            )
            print(f'✅ Admin user restored successfully!')
            print(f'📧 Email: {admin_email}')
            print(f'🔑 Password: {working_password}')
            return admin_email, working_password
        else:
            # Reset password to temp123 (most commonly used)
            new_password = "temp123"
            hashed_password = security.get_password_hash(new_password)
            
            await db.users.update_one(
                {'email': admin_email},
                {
                    '$set': {
                        'hashed_password': hashed_password,
                        'role': UserRole.admin.value,
                        'status': UserStatus.active.value,
                        'must_change_password': False,
                        'last_login': datetime.utcnow()
                    }
                }
            )
            print(f'🔄 Password reset for existing user')
            print(f'📧 Email: {admin_email}')
            print(f'🔑 New Password: {new_password}')
            return admin_email, new_password
    
    else:
        # Create new admin user
        print(f'❌ User not found. Creating new admin user...')
        
        # Use temp123 as the default password (most commonly used in the codebase)
        admin_password = "temp123"
        hashed_password = security.get_password_hash(admin_password)
        
        # Generate a new UUID for the user
        from uuid import uuid4
        user_id = str(uuid4())
        
        # Create the user document
        user_doc = {
            'id': user_id,
            'email': admin_email,
            'hashed_password': hashed_password,
            'role': UserRole.admin.value,
            'status': UserStatus.active.value,
            'is_premium': True,  # Give admin premium access
            'invitation_id': None,
            'must_change_password': False,
            'created_at': datetime.utcnow(),
            'last_login': None
        }
        
        # Insert the user
        await db.users.insert_one(user_doc)
        
        print(f'✅ New admin user created successfully!')
        print(f'📧 Email: {admin_email}')
        print(f'🔑 Password: {admin_password}')
        print(f'🆔 User ID: {user_id}')
        
        return admin_email, admin_password

async def verify_admin_login(email, password):
    """Verify that the admin user can log in successfully"""
    db = get_database()
    
    print(f'\n🧪 Verifying admin login...')
    auth_result = await authenticate_user(db, email, password)
    
    if auth_result:
        print(f'✅ Admin login verification successful!')
        print(f'   👤 Role: {auth_result.get("role")}')
        print(f'   📊 Status: {auth_result.get("status")}')
        print(f'   🎯 Premium: {auth_result.get("is_premium")}')
        return True
    else:
        print(f'❌ Admin login verification failed!')
        return False

async def main():
    """Main function to restore admin user and verify login"""
    try:
        print("🚀 Starting admin user restoration process...")
        
        # Restore the admin user
        email, password = await restore_admin_user()
        
        # Verify the login works
        login_success = await verify_admin_login(email, password)
        
        if login_success:
            print(f'\n🎉 Admin user restoration completed successfully!')
            print(f'🔐 Final Login Credentials:')
            print(f'   📧 Email: {email}')
            print(f'   🔑 Password: {password}')
            print(f'   👤 Role: admin')
            print(f'   📊 Status: active')
        else:
            print(f'\n❌ Admin user restoration failed - login verification unsuccessful')
            
    except Exception as e:
        print(f'💥 Error during admin user restoration: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())