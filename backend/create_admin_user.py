import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import connect_to_mongo, close_mongo_connection, get_database
from app.models.user import UserInDB, UserRole, UserStatus
from app.core import security
from datetime import datetime

async def create_admin_user():
    """Create an admin user for testing"""
    print("Creating admin user...")
    
    # Connect to database
    await connect_to_mongo()
    db = get_database()
    
    # Check if admin user already exists
    existing_admin = await db.users.find_one({"email": "admin@superconnect.ai"})
    if existing_admin:
        print("✅ Admin user already exists!")
        print(f"Email: admin@superconnect.ai")
        return
    
    # Create admin user
    hashed_password = security.get_password_hash("admin123")
    
    admin_user = UserInDB(
        email="admin@superconnect.ai",
        hashed_password=hashed_password,
        role=UserRole.admin,
        status=UserStatus.active,
        is_premium=False,
        must_change_password=False,
        created_at=datetime.utcnow()
    )
    
    # Convert to dict for MongoDB storage
    user_dict = admin_user.model_dump()
    user_dict["id"] = str(user_dict["id"])  # Convert UUID to string
    if user_dict.get("invitation_id"):
        user_dict["invitation_id"] = str(user_dict["invitation_id"])
    
    # Insert admin user
    result = await db.users.insert_one(user_dict)
    
    if result.inserted_id:
        print("✅ Admin user created successfully!")
        print(f"Email: admin@superconnect.ai")
        print(f"Password: admin123")
        print(f"Role: {UserRole.admin}")
    else:
        print("❌ Failed to create admin user")
    
    # Close database connection
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(create_admin_user())