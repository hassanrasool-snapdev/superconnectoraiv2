#!/usr/bin/env python3
"""
Test script for the one-time password implementation
"""
import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

async def test_otp_flow():
    """Test the complete one-time password flow"""
    async with httpx.AsyncClient() as client:
        print("🧪 Testing One-Time Password Implementation")
        print("=" * 50)
        
        # Step 1: First, we need to login as an admin to test the admin endpoint
        print("\n1. Testing admin login (assuming admin user exists)...")
        
        # For this test, let's assume we have an admin user. In a real scenario,
        # you'd need to create one first or use existing credentials
        admin_email = "admin@example.com"  # Replace with actual admin email
        admin_password = "admin_password"  # Replace with actual admin password
        
        try:
            login_response = await client.post(
                f"{BASE_URL}/auth/login",
                data={
                    "username": admin_email,
                    "password": admin_password
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if login_response.status_code == 200:
                admin_token = login_response.json()["access_token"]
                print("✅ Admin login successful")
                
                # Step 2: Create a new user with OTP
                print("\n2. Creating new user with one-time password...")
                test_email = f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
                
                create_user_response = await client.post(
                    f"{BASE_URL}/admin/users/create",
                    json={"email": test_email},
                    headers={"Authorization": f"Bearer {admin_token}"}
                )
                
                if create_user_response.status_code == 201:
                    user_data = create_user_response.json()
                    temp_password = user_data["otp"]
                    print(f"✅ User created successfully")
                    print(f"   Email: {test_email}")
                    print(f"   Temporary Password: {temp_password}")
                    print(f"   Must Change Password: {user_data['must_change_password']}")
                    
                    # Step 3: Test login with temporary password
                    print("\n3. Testing login with temporary password...")
                    temp_login_response = await client.post(
                        f"{BASE_URL}/auth/login",
                        data={
                            "username": test_email,
                            "password": temp_password
                        },
                        headers={"Content-Type": "application/x-www-form-urlencoded"}
                    )
                    
                    if temp_login_response.status_code == 200:
                        login_data = temp_login_response.json()
                        if "reset_token" in login_data:
                            reset_token = login_data["reset_token"]
                            print("✅ Login with temporary password successful")
                            print("✅ Password reset token received (forced password change)")
                            
                            # Step 4: Reset password
                            print("\n4. Testing password reset...")
                            new_password = "NewSecurePassword123!"
                            
                            reset_response = await client.post(
                                f"{BASE_URL}/auth/reset-password",
                                json={
                                    "new_password": new_password,
                                    "reset_token": reset_token
                                }
                            )
                            
                            if reset_response.status_code == 200:
                                final_token = reset_response.json()["access_token"]
                                print("✅ Password reset successful")
                                print("✅ Access token received")
                                
                                # Step 5: Test normal login with new password
                                print("\n5. Testing login with new password...")
                                final_login_response = await client.post(
                                    f"{BASE_URL}/auth/login",
                                    data={
                                        "username": test_email,
                                        "password": new_password
                                    },
                                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                                )
                                
                                if final_login_response.status_code == 200:
                                    final_data = final_login_response.json()
                                    if "access_token" in final_data:
                                        print("✅ Normal login with new password successful")
                                        print("✅ Regular access token received (no password reset required)")
                                        
                                        # Step 6: Test accessing protected endpoint
                                        print("\n6. Testing access to protected endpoint...")
                                        me_response = await client.get(
                                            f"{BASE_URL}/users/me",
                                            headers={"Authorization": f"Bearer {final_data['access_token']}"}
                                        )
                                        
                                        if me_response.status_code == 200:
                                            user_info = me_response.json()
                                            print("✅ Protected endpoint access successful")
                                            print(f"   User: {user_info['email']}")
                                            print(f"   Must Change Password: {user_info['must_change_password']}")
                                            
                                            print("\n🎉 ALL TESTS PASSED!")
                                            print("The one-time password implementation is working correctly.")
                                        else:
                                            print(f"❌ Protected endpoint access failed: {me_response.status_code}")
                                            print(me_response.text)
                                    else:
                                        print("❌ Final login didn't return access token")
                                        print(final_data)
                                else:
                                    print(f"❌ Final login failed: {final_login_response.status_code}")
                                    print(final_login_response.text)
                            else:
                                print(f"❌ Password reset failed: {reset_response.status_code}")
                                print(reset_response.text)
                        else:
                            print("❌ Expected password reset token but got access token")
                            print(login_data)
                    else:
                        print(f"❌ Temporary password login failed: {temp_login_response.status_code}")
                        print(temp_login_response.text)
                else:
                    print(f"❌ User creation failed: {create_user_response.status_code}")
                    print(create_user_response.text)
            else:
                print(f"❌ Admin login failed: {login_response.status_code}")
                print("Note: You may need to create an admin user first or update the credentials in this script")
                print(login_response.text)
                
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_otp_flow())