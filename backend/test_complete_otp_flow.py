#!/usr/bin/env python3
"""
Complete test script for the one-time password implementation including access requests
"""
import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

async def test_complete_flow():
    """Test the complete flow: access request -> admin approval -> user login -> password reset"""
    async with httpx.AsyncClient() as client:
        print("🧪 Testing Complete One-Time Password Flow with Access Requests")
        print("=" * 70)
        
        # Step 1: Submit an access request (public endpoint)
        print("\n1. Submitting access request...")
        test_email = f"newuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
        
        access_request_response = await client.post(
            f"{BASE_URL}/access-requests",
            json={
                "email": test_email,
                "full_name": "Test User",
                "reason": "I need access to test the new OTP system",
                "organization": "Test Organization"
            }
        )
        
        if access_request_response.status_code == 201:
            request_data = access_request_response.json()
            request_id = request_data["id"]
            print(f"✅ Access request submitted successfully")
            print(f"   Request ID: {request_id}")
            print(f"   Email: {test_email}")
            print(f"   Status: {request_data['status']}")
            
            # Step 2: Admin login (using existing user)
            print("\n2. Admin logging in...")
            # Using one of the existing users from the check_users.py output
            admin_email = "ha@nextstepfwd.com"  # Assuming this user has admin role
            admin_password = "your_admin_password"  # You'll need to set this
            
            try:
                admin_login_response = await client.post(
                    f"{BASE_URL}/auth/login",
                    data={
                        "username": admin_email,
                        "password": admin_password
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if admin_login_response.status_code == 200:
                    admin_token = admin_login_response.json()["access_token"]
                    print("✅ Admin login successful")
                    
                    # Step 3: Admin views access requests
                    print("\n3. Admin viewing access requests...")
                    requests_response = await client.get(
                        f"{BASE_URL}/admin/access-requests",
                        headers={"Authorization": f"Bearer {admin_token}"}
                    )
                    
                    if requests_response.status_code == 200:
                        requests_list = requests_response.json()
                        print(f"✅ Retrieved {len(requests_list)} access requests")
                        
                        # Step 4: Admin approves the request and creates user
                        print("\n4. Admin approving access request and creating user...")
                        approve_response = await client.post(
                            f"{BASE_URL}/admin/access-requests/{request_id}/approve",
                            headers={"Authorization": f"Bearer {admin_token}"}
                        )
                        
                        if approve_response.status_code == 200:
                            user_data = approve_response.json()
                            temp_password = user_data["otp"]
                            print(f"✅ Access request approved and user created")
                            print(f"   Email: {test_email}")
                            print(f"   Temporary Password: {temp_password}")
                            print(f"   Must Change Password: {user_data['must_change_password']}")
                            
                            # Step 5: New user logs in with temporary password
                            print("\n5. New user logging in with temporary password...")
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
                                    
                                    # Step 6: User resets password
                                    print("\n6. User resetting password...")
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
                                        
                                        # Step 7: User logs in normally with new password
                                        print("\n7. User logging in with new password...")
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
                                                print("✅ Regular access token received")
                                                
                                                # Step 8: Test protected endpoint access
                                                print("\n8. Testing protected endpoint access...")
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
                                                    print("The complete one-time password flow is working correctly!")
                                                    
                                                    # Summary
                                                    print("\n📋 FLOW SUMMARY:")
                                                    print("1. ✅ User submitted access request")
                                                    print("2. ✅ Admin viewed pending requests")
                                                    print("3. ✅ Admin approved request and created user with OTP")
                                                    print("4. ✅ User logged in with temporary password")
                                                    print("5. ✅ System forced password reset")
                                                    print("6. ✅ User successfully reset password")
                                                    print("7. ✅ User can now log in normally")
                                                    print("8. ✅ User has full access to protected endpoints")
                                                else:
                                                    print(f"❌ Protected endpoint access failed: {me_response.status_code}")
                                                    print(me_response.text)
                                            else:
                                                print("❌ Final login didn't return access token")
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
                            print(f"❌ Access request approval failed: {approve_response.status_code}")
                            print(approve_response.text)
                    else:
                        print(f"❌ Failed to retrieve access requests: {requests_response.status_code}")
                        print(requests_response.text)
                else:
                    print(f"❌ Admin login failed: {admin_login_response.status_code}")
                    print("Note: You may need to update the admin credentials in this script")
                    print("Or ensure the user has admin role in the database")
                    print(admin_login_response.text)
                    
            except Exception as e:
                print(f"❌ Admin login failed with exception: {e}")
                print("Note: Please update admin credentials in the script")
                
        else:
            print(f"❌ Access request submission failed: {access_request_response.status_code}")
            print(access_request_response.text)

if __name__ == "__main__":
    asyncio.run(test_complete_flow())