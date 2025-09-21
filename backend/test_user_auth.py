#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo
from app.services.auth_service import authenticate_user

async def test_user_login():
    """Test if the existing test user can authenticate"""
    
    # Initialize database connection
    await connect_to_mongo()
    db = get_database()
    
    # Test credentials
    test_email = "test@example.com"
    test_password = "testpass123"
    
    print(f"🔍 Testing login for: {test_email}")
    
    # Check if user exists in database
    user = await db.users.find_one({"email": test_email})
    if user:
        print(f"✅ User found in database:")
        print(f"   📧 Email: {user.get('email')}")
        print(f"   🆔 ID: {user.get('id')}")
        print(f"   👤 Role: {user.get('role')}")
        print(f"   📊 Status: {user.get('status')}")
        print(f"   🎯 Premium: {user.get('is_premium')}")
        
        # Test authentication
        auth_result = await authenticate_user(db, test_email, test_password)
        if auth_result:
            print(f"✅ Authentication successful!")
            print(f"\n🎯 Login Credentials:")
            print(f"   📧 Email: {test_email}")
            print(f"   🔑 Password: {test_password}")
            return True
        else:
            print(f"❌ Authentication failed!")
            return False
    else:
        print(f"❌ User not found in database!")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_user_login())
    if result:
        print(f"\n🎉 Test user is ready for login!")
    else:
        print(f"\n❌ Test user authentication failed!")