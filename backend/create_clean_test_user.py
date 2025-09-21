#!/usr/bin/env python3

import asyncio
import sys
import os
from datetime import datetime
from uuid import uuid4

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo
from app.core.security import get_password_hash

async def create_clean_test_user():
    """Create a clean test user for testing search functionality"""
    
    # Initialize database connection
    await connect_to_mongo()
    db = get_database()
    
    # Clean test user credentials
    test_email = "test@example.com"
    test_password = "testpass123"
    user_id = str(uuid4())  # Generate a new clean user ID
    
    print(f"🔧 Creating clean test user: {test_email}")
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": test_email})
    if existing_user:
        print(f"✅ Test user already exists with ID: {existing_user.get('id', existing_user.get('_id'))}")
        return existing_user.get('id', existing_user.get('_id'))
    
    # Hash the password
    hashed_password = get_password_hash(test_password)
    
    # Create user document
    user_doc = {
        "id": user_id,
        "_id": user_id,
        "email": test_email,
        "hashed_password": hashed_password,
        "role": "user",
        "status": "active",
        "is_premium": False,
        "invitation_id": None,
        "must_change_password": False,
        "created_at": datetime.utcnow(),
        "last_login": None
    }
    
    # Insert user
    try:
        await db.users.insert_one(user_doc)
        print(f"✅ Successfully created clean test user!")
        print(f"   📧 Email: {test_email}")
        print(f"   🔑 Password: {test_password}")
        print(f"   🆔 User ID: {user_id}")
        print(f"\n🎯 You can now login to test search functionality!")
        return user_id
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(create_clean_test_user())