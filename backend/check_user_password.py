#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database, connect_to_mongo

async def main():
    print("🔍 Checking User Password Information...")
    print("=" * 50)
    
    try:
        # Connect to database
        await connect_to_mongo()
        db = get_database()
        print("✅ Connected to database successfully!")
        
        # Find the specific user
        user_email = "nnguyen0646@gmail.com"
        user = await db.users.find_one({"email": user_email})
        
        if not user:
            print(f"❌ User {user_email} not found!")
            return
        
        print(f"\n👤 User Information:")
        print(f"Email: {user.get('email')}")
        print(f"ID: {str(user.get('_id'))}")
        print(f"Name: {user.get('name', 'N/A')}")
        print(f"Role: {user.get('role', 'N/A')}")
        print(f"Created: {user.get('created_at', 'N/A')}")
        
        # Check if password exists
        if 'password' in user:
            print(f"Password Hash: {user['password'][:50]}... (truncated)")
            print("✅ User has a password set")
        else:
            print("❌ No password field found!")
        
        # Check if this is an OTP-only user
        if 'otp_enabled' in user:
            print(f"OTP Enabled: {user.get('otp_enabled')}")
        
        if 'last_otp' in user:
            print(f"Last OTP: {user.get('last_otp')}")
            print(f"OTP Expires: {user.get('otp_expires_at')}")
        
        print(f"\n💡 RECOMMENDATION:")
        if 'password' not in user or not user.get('password'):
            print("❌ This user doesn't have a password set!")
            print("🔧 SOLUTIONS:")
            print("1. Use OTP login if enabled")
            print("2. Create a password for this user")
            print("3. Use a different user account that has a password")
            
            # Show other users with passwords
            print(f"\n👥 Other users in database:")
            all_users = await db.users.find({}).to_list(length=10)
            for i, u in enumerate(all_users[:5], 1):
                has_password = "✅" if u.get('password') else "❌"
                print(f"{i}. {u.get('email')} {has_password}")
        else:
            print("✅ User has a password - login should work")
            print("🔧 If login fails, the password might be incorrect")
            print("   Try using OTP login or reset the password")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())