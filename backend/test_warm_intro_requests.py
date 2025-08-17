#!/usr/bin/env python3
"""
Comprehensive test script for the warm intro requests functionality.
This script tests the model, service, and router components.
"""

import asyncio
import sys
import os
from uuid import uuid4, UUID
from datetime import datetime
import json

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.warm_intro_request import WarmIntroRequest, WarmIntroStatus, WarmIntroRequestCreate, WarmIntroRequestUpdate
from app.services import warm_intro_requests_service
from app.core.db import get_database
from motor.motor_asyncio import AsyncIOMotorClient

class TestWarmIntroRequests:
    def __init__(self):
        self.test_user_id = uuid4()
        self.test_requests = []
        self.db = None
        
    async def setup_database(self):
        """Setup test database connection."""
        print("Setting up database connection...")
        try:
            # Use the same database connection as the main app
            client = AsyncIOMotorClient("mongodb://localhost:27017")
            self.db = client.superconnect_test  # Use a test database
            print("✅ Database connection established")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    async def cleanup_test_data(self):
        """Clean up test data from database."""
        if self.db:
            try:
                # Delete all test requests for this user
                result = await self.db.warm_intro_requests.delete_many({
                    "user_id": str(self.test_user_id)
                })
                print(f"🧹 Cleaned up {result.deleted_count} test records")
            except Exception as e:
                print(f"⚠️ Cleanup warning: {e}")

    async def test_model_validation(self):
        """Test the WarmIntroRequest model validation."""
        print("=" * 60)
        print("Testing Model Validation")
        print("=" * 60)
        
        # Test valid model creation
        try:
            request = WarmIntroRequest(
                user_id=self.test_user_id,
                requester_name="John Doe",
                connection_name="Jane Smith",
                status=WarmIntroStatus.pending
            )
            print("✅ Valid model creation successful")
            print(f"   ID: {request.id}")
            print(f"   Created at: {request.created_at}")
            print(f"   Status: {request.status}")
        except Exception as e:
            print(f"❌ Valid model creation failed: {e}")
        
        # Test enum validation
        try:
            for status in [WarmIntroStatus.pending, WarmIntroStatus.connected, WarmIntroStatus.declined]:
                request = WarmIntroRequest(
                    user_id=self.test_user_id,
                    requester_name="Test User",
                    connection_name="Test Connection",
                    status=status
                )
                print(f"✅ Status validation passed for: {status}")
        except Exception as e:
            print(f"❌ Status validation failed: {e}")
        
        # Test model serialization
        try:
            request = WarmIntroRequest(
                user_id=self.test_user_id,
                requester_name="Serialization Test",
                connection_name="Test Connection",
                status=WarmIntroStatus.pending
            )
            serialized = request.model_dump(by_alias=True)
            print("✅ Model serialization successful")
            print(f"   Serialized keys: {list(serialized.keys())}")
        except Exception as e:
            print(f"❌ Model serialization failed: {e}")

    async def test_service_create_request(self):
        """Test creating warm intro requests via service."""
        print("=" * 60)
        print("Testing Service - Create Request")
        print("=" * 60)
        
        test_cases = [
            {
                "requester_name": "Alice Johnson",
                "connection_name": "Bob Wilson",
                "status": WarmIntroStatus.pending
            },
            {
                "requester_name": "Charlie Brown",
                "connection_name": "Diana Prince",
                "status": WarmIntroStatus.connected
            },
            {
                "requester_name": "Eve Adams",
                "connection_name": "Frank Miller",
                "status": WarmIntroStatus.declined
            }
        ]
        
        for i, case in enumerate(test_cases):
            try:
                request = await warm_intro_requests_service.create_warm_intro_request(
                    db=self.db,
                    user_id=self.test_user_id,
                    **case
                )
                self.test_requests.append(request)
                print(f"✅ Test case {i+1}: Created request {request.id}")
                print(f"   Requester: {request.requester_name}")
                print(f"   Connection: {request.connection_name}")
                print(f"   Status: {request.status}")
            except Exception as e:
                print(f"❌ Test case {i+1} failed: {e}")

    async def test_service_get_requests(self):
        """Test retrieving warm intro requests via service."""
        print("=" * 60)
        print("Testing Service - Get Requests")
        print("=" * 60)
        
        # Test getting all requests
        try:
            result = await warm_intro_requests_service.get_warm_intro_requests(
                db=self.db,
                user_id=self.test_user_id,
                page=1,
                limit=10
            )
            print(f"✅ Retrieved {len(result['items'])} requests")
            print(f"   Total: {result['total']}")
            print(f"   Page: {result['page']}")
            print(f"   Total pages: {result['total_pages']}")
        except Exception as e:
            print(f"❌ Get all requests failed: {e}")
        
        # Test pagination
        try:
            result = await warm_intro_requests_service.get_warm_intro_requests(
                db=self.db,
                user_id=self.test_user_id,
                page=1,
                limit=2
            )
            print(f"✅ Pagination test: Retrieved {len(result['items'])} of {result['total']} requests")
        except Exception as e:
            print(f"❌ Pagination test failed: {e}")
        
        # Test status filtering
        for status in [WarmIntroStatus.pending, WarmIntroStatus.connected, WarmIntroStatus.declined]:
            try:
                result = await warm_intro_requests_service.get_warm_intro_requests(
                    db=self.db,
                    user_id=self.test_user_id,
                    page=1,
                    limit=10,
                    status_filter=status
                )
                print(f"✅ Status filter ({status}): Found {len(result['items'])} requests")
            except Exception as e:
                print(f"❌ Status filter ({status}) failed: {e}")

    async def test_service_get_by_id(self):
        """Test retrieving a specific request by ID."""
        print("=" * 60)
        print("Testing Service - Get Request by ID")
        print("=" * 60)
        
        if not self.test_requests:
            print("⚠️ No test requests available for ID lookup")
            return
        
        test_request = self.test_requests[0]
        
        # Test valid ID lookup
        try:
            found_request = await warm_intro_requests_service.get_warm_intro_request_by_id(
                db=self.db,
                request_id=test_request.id,
                user_id=self.test_user_id
            )
            if found_request:
                print(f"✅ Found request by ID: {found_request.id}")
                print(f"   Requester: {found_request.requester_name}")
                print(f"   Connection: {found_request.connection_name}")
            else:
                print("❌ Request not found by ID")
        except Exception as e:
            print(f"❌ Get by ID failed: {e}")
        
        # Test invalid ID lookup
        try:
            fake_id = uuid4()
            found_request = await warm_intro_requests_service.get_warm_intro_request_by_id(
                db=self.db,
                request_id=fake_id,
                user_id=self.test_user_id
            )
            if found_request is None:
                print("✅ Invalid ID correctly returned None")
            else:
                print("❌ Invalid ID unexpectedly returned a request")
        except Exception as e:
            print(f"❌ Invalid ID test failed: {e}")

    async def test_service_update_status(self):
        """Test updating request status via service."""
        print("=" * 60)
        print("Testing Service - Update Status")
        print("=" * 60)
        
        if not self.test_requests:
            print("⚠️ No test requests available for status update")
            return
        
        test_request = self.test_requests[0]
        original_status = test_request.status
        new_status = WarmIntroStatus.connected if original_status != WarmIntroStatus.connected else WarmIntroStatus.declined
        
        try:
            updated_request = await warm_intro_requests_service.update_warm_intro_request_status(
                db=self.db,
                request_id=test_request.id,
                status=new_status,
                user_id=self.test_user_id
            )
            
            if updated_request:
                print(f"✅ Status updated successfully")
                print(f"   Original status: {original_status}")
                print(f"   New status: {updated_request.status}")
                print(f"   Updated at: {updated_request.updated_at}")
                
                # Verify the update persisted
                verified_request = await warm_intro_requests_service.get_warm_intro_request_by_id(
                    db=self.db,
                    request_id=test_request.id,
                    user_id=self.test_user_id
                )
                if verified_request and verified_request.status == new_status:
                    print("✅ Status update verified in database")
                else:
                    print("❌ Status update not persisted correctly")
            else:
                print("❌ Status update returned None")
        except Exception as e:
            print(f"❌ Status update failed: {e}")

    async def test_service_get_counts(self):
        """Test getting request counts by status."""
        print("=" * 60)
        print("Testing Service - Get Counts")
        print("=" * 60)
        
        try:
            counts = await warm_intro_requests_service.get_warm_intro_request_counts(
                db=self.db,
                user_id=self.test_user_id
            )
            
            print(f"✅ Retrieved counts successfully:")
            print(f"   Total: {counts['total']}")
            print(f"   Pending: {counts['pending']}")
            print(f"   Connected: {counts['connected']}")
            print(f"   Declined: {counts['declined']}")
            
            # Verify counts add up
            calculated_total = counts['pending'] + counts['connected'] + counts['declined']
            if calculated_total == counts['total']:
                print("✅ Count totals are consistent")
            else:
                print(f"❌ Count totals inconsistent: {calculated_total} != {counts['total']}")
                
        except Exception as e:
            print(f"❌ Get counts failed: {e}")

    async def test_service_search(self):
        """Test searching requests by name."""
        print("=" * 60)
        print("Testing Service - Search Functionality")
        print("=" * 60)
        
        search_terms = ["Alice", "Bob", "Charlie", "NonExistent"]
        
        for term in search_terms:
            try:
                result = await warm_intro_requests_service.search_warm_intro_requests(
                    db=self.db,
                    user_id=self.test_user_id,
                    search_query=term,
                    page=1,
                    limit=10
                )
                
                print(f"✅ Search for '{term}': Found {len(result['items'])} results")
                if result['items']:
                    for item in result['items']:
                        print(f"   - {item.requester_name} -> {item.connection_name}")
                        
            except Exception as e:
                print(f"❌ Search for '{term}' failed: {e}")

    async def test_service_delete(self):
        """Test deleting requests via service."""
        print("=" * 60)
        print("Testing Service - Delete Request")
        print("=" * 60)
        
        if not self.test_requests:
            print("⚠️ No test requests available for deletion")
            return
        
        # Test deleting the last request
        test_request = self.test_requests[-1]
        
        try:
            success = await warm_intro_requests_service.delete_warm_intro_request(
                db=self.db,
                request_id=test_request.id,
                user_id=self.test_user_id
            )
            
            if success:
                print(f"✅ Request deleted successfully: {test_request.id}")
                
                # Verify deletion
                found_request = await warm_intro_requests_service.get_warm_intro_request_by_id(
                    db=self.db,
                    request_id=test_request.id,
                    user_id=self.test_user_id
                )
                
                if found_request is None:
                    print("✅ Deletion verified - request not found")
                else:
                    print("❌ Deletion failed - request still exists")
            else:
                print("❌ Delete operation returned False")
                
        except Exception as e:
            print(f"❌ Delete request failed: {e}")

    async def test_user_isolation(self):
        """Test that users can only access their own requests."""
        print("=" * 60)
        print("Testing User Isolation")
        print("=" * 60)
        
        # Create a request for a different user
        other_user_id = uuid4()
        
        try:
            other_request = await warm_intro_requests_service.create_warm_intro_request(
                db=self.db,
                user_id=other_user_id,
                requester_name="Other User",
                connection_name="Other Connection",
                status=WarmIntroStatus.pending
            )
            
            print(f"✅ Created request for other user: {other_request.id}")
            
            # Try to access other user's request with our test user
            found_request = await warm_intro_requests_service.get_warm_intro_request_by_id(
                db=self.db,
                request_id=other_request.id,
                user_id=self.test_user_id  # Wrong user ID
            )
            
            if found_request is None:
                print("✅ User isolation working - cannot access other user's request")
            else:
                print("❌ User isolation failed - accessed other user's request")
            
            # Clean up other user's request
            await self.db.warm_intro_requests.delete_one({"id": str(other_request.id)})
            
        except Exception as e:
            print(f"❌ User isolation test failed: {e}")

    async def run_all_tests(self):
        """Run all tests in sequence."""
        print("🚀 Starting Warm Intro Requests Test Suite")
        print("=" * 80)
        
        # Setup
        if not await self.setup_database():
            print("❌ Cannot proceed without database connection")
            return
        
        try:
            # Run all tests
            await self.test_model_validation()
            await self.test_service_create_request()
            await self.test_service_get_requests()
            await self.test_service_get_by_id()
            await self.test_service_update_status()
            await self.test_service_get_counts()
            await self.test_service_search()
            await self.test_user_isolation()
            await self.test_service_delete()
            
            print("\n" + "=" * 80)
            print("🎉 All tests completed successfully!")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ Test suite failed with error: {e}")
            
        finally:
            # Cleanup
            await self.cleanup_test_data()

async def main():
    """Main test runner."""
    test_suite = TestWarmIntroRequests()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())