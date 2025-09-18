#!/usr/bin/env python3
"""
Script to create a sample end-user account with restricted permissions.
This user will only have access to the dashboard search functionality,
without seeing the admin navigation links.
"""

import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import UserRole, UserStatus
from datetime import datetime
import uuid

async def create_sample_enduser():
    """Create a sample end-user account for testing restricted permissions."""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.DATABASE_URL)
    db = client[settings.DATABASE_NAME]
    
    try:
        # Sample end-user details
        sample_user = {
            "id": str(uuid.uuid4()),
            "email": "enduser@example.com",
            "hashed_password": get_password_hash("password123"),
            "role": UserRole.user.value,  # Regular user role (not admin)
            "status": UserStatus.active.value,
            "is_premium": False,
            "invitation_id": None,
            "created_at": datetime.utcnow(),
            "last_login": None
        }
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": sample_user["email"]})
        if existing_user:
            print(f"User {sample_user['email']} already exists!")
            print("Login credentials:")
            print(f"  Email: {sample_user['email']}")
            print(f"  Password: password123")
            print(f"  Role: {sample_user['role']}")
            return
        
        # Insert the sample user
        result = await db.users.insert_one(sample_user)
        
        if result.inserted_id:
            print("✅ Sample end-user created successfully!")
            print("\n📋 Login Credentials:")
            print(f"  Email: {sample_user['email']}")
            print(f"  Password: password123")
            print(f"  Role: {sample_user['role']}")
            print(f"  User ID: {sample_user['id']}")
            
            print("\n🔒 Permissions:")
            print("  - Can access dashboard and search connections")
            print("  - Cannot see 'Upload Connections' link")
            print("  - Cannot see 'Warm Intro Requests' link")
            print("  - Cannot access admin-only features")
            
            print("\n🧪 Testing Instructions:")
            print("1. Go to http://localhost:3000/login")
            print("2. Login with the credentials above")
            print("3. Verify that the navigation bar only shows 'Superconnect AI' logo")
            print("4. Confirm no admin navigation links are visible")
            print("5. Test that search functionality still works on dashboard")
            
        else:
            print("❌ Failed to create sample end-user")
            
    except Exception as e:
        print(f"❌ Error creating sample end-user: {e}")
        
    finally:
        client.close()

if __name__ == "__main__":
    print("🚀 Creating sample end-user account...")
    asyncio.run(create_sample_enduser())