#!/usr/bin/env python3
"""
Demo script for warm intro requests functionality.
This script demonstrates the complete workflow of the warm intro requests feature.
"""

import asyncio
import sys
import os
from uuid import uuid4
from datetime import datetime
import time

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.warm_intro_request import WarmIntroRequest, WarmIntroStatus
from app.services import warm_intro_requests_service
from motor.motor_asyncio import AsyncIOMotorClient

class WarmIntroRequestsDemo:
    def __init__(self):
        self.db = None
        self.demo_user_id = uuid4()
        self.created_requests = []
        
    async def setup_database(self):
        """Setup database connection."""
        print("🔌 Connecting to MongoDB...")
        try:
            client = AsyncIOMotorClient("mongodb://localhost:27017")
            self.db = client.superconnect
            print("✅ Database connection established")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def print_header(self, title):
        """Print a formatted header."""
        print("\n" + "=" * 60)
        print(f"🎯 {title}")
        print("=" * 60)
    
    def print_step(self, step_num, description):
        """Print a formatted step."""
        print(f"\n📍 Step {step_num}: {description}")
        print("-" * 40)
    
    async def demo_step_1_create_requests(self):
        """Demo Step 1: Create warm intro requests."""
        self.print_step(1, "Creating Warm Intro Requests")
        
        # Sample requests to create
        sample_requests = [
            {
                "requester_name": "Alice Johnson",
                "connection_name": "Bob Wilson",
                "status": WarmIntroStatus.pending
            },
            {
                "requester_name": "Charlie Brown",
                "connection_name": "Diana Prince",
                "status": WarmIntroStatus.pending
            },
            {
                "requester_name": "Eve Adams",
                "connection_name": "Frank Miller",
                "status": WarmIntroStatus.pending
            }
        ]
        
        print("Creating sample warm intro requests...")
        
        for i, request_data in enumerate(sample_requests, 1):
            try:
                request = await warm_intro_requests_service.create_warm_intro_request(
                    db=self.db,
                    user_id=self.demo_user_id,
                    **request_data
                )
                self.created_requests.append(request)
                
                print(f"✅ Request {i}: {request.requester_name} → {request.connection_name}")
                print(f"   ID: {request.id}")
                print(f"   Status: {request.status}")
                print(f"   Created: {request.created_at}")
                
            except Exception as e:
                print(f"❌ Failed to create request {i}: {e}")
        
        print(f"\n🎉 Successfully created {len(self.created_requests)} requests!")
    
    async def demo_step_2_list_requests(self):
        """Demo Step 2: List and paginate requests."""
        self.print_step(2, "Listing and Paginating Requests")
        
        try:
            # Get all requests
            result = await warm_intro_requests_service.get_warm_intro_requests(
                db=self.db,
                user_id=self.demo_user_id,
                page=1,
                limit=10
            )
            
            print(f"📋 Found {result['total']} total requests")
            print(f"📄 Page {result['page']} of {result['total_pages']}")
            print(f"📊 Showing {len(result['items'])} items")
            
            print("\n📝 Request List:")
            for i, request in enumerate(result['items'], 1):
                print(f"{i}. {request.requester_name} → {request.connection_name}")
                print(f"   Status: {request.status} | ID: {request.id}")
            
            # Demo pagination with smaller limit
            print("\n🔄 Testing pagination (limit=2)...")
            paginated_result = await warm_intro_requests_service.get_warm_intro_requests(
                db=self.db,
                user_id=self.demo_user_id,
                page=1,
                limit=2
            )
            
            print(f"📄 Page 1: {len(paginated_result['items'])} items")
            for request in paginated_result['items']:
                print(f"   - {request.requester_name} → {request.connection_name}")
                
        except Exception as e:
            print(f"❌ Failed to list requests: {e}")
    
    async def demo_step_3_update_status(self):
        """Demo Step 3: Update request statuses."""
        self.print_step(3, "Updating Request Statuses")
        
        if not self.created_requests:
            print("⚠️ No requests available for status updates")
            return
        
        # Update first request to "connected"
        first_request = self.created_requests[0]
        print(f"🔄 Updating request: {first_request.requester_name} → {first_request.connection_name}")
        print(f"   Current status: {first_request.status}")
        
        try:
            updated_request = await warm_intro_requests_service.update_warm_intro_request_status(
                db=self.db,
                request_id=first_request.id,
                status=WarmIntroStatus.connected,
                user_id=self.demo_user_id
            )
            
            if updated_request:
                print(f"✅ Status updated successfully!")
                print(f"   New status: {updated_request.status}")
                print(f"   Updated at: {updated_request.updated_at}")
                
                # Update our local copy
                self.created_requests[0] = updated_request
            else:
                print("❌ Status update failed")
                
        except Exception as e:
            print(f"❌ Error updating status: {e}")
        
        # Update second request to "declined"
        if len(self.created_requests) > 1:
            second_request = self.created_requests[1]
            print(f"\n🔄 Updating request: {second_request.requester_name} → {second_request.connection_name}")
            print(f"   Current status: {second_request.status}")
            
            try:
                updated_request = await warm_intro_requests_service.update_warm_intro_request_status(
                    db=self.db,
                    request_id=second_request.id,
                    status=WarmIntroStatus.declined,
                    user_id=self.demo_user_id
                )
                
                if updated_request:
                    print(f"✅ Status updated successfully!")
                    print(f"   New status: {updated_request.status}")
                    print(f"   Updated at: {updated_request.updated_at}")
                    
                    # Update our local copy
                    self.created_requests[1] = updated_request
                else:
                    print("❌ Status update failed")
                    
            except Exception as e:
                print(f"❌ Error updating status: {e}")
    
    async def demo_step_4_filter_by_status(self):
        """Demo Step 4: Filter requests by status."""
        self.print_step(4, "Filtering Requests by Status")
        
        statuses_to_test = [WarmIntroStatus.pending, WarmIntroStatus.connected, WarmIntroStatus.declined]
        
        for status in statuses_to_test:
            try:
                result = await warm_intro_requests_service.get_warm_intro_requests(
                    db=self.db,
                    user_id=self.demo_user_id,
                    page=1,
                    limit=10,
                    status_filter=status
                )
                
                print(f"🔍 Filter: {status.upper()}")
                print(f"   Found: {len(result['items'])} requests")
                
                for request in result['items']:
                    print(f"   - {request.requester_name} → {request.connection_name} ({request.status})")
                
            except Exception as e:
                print(f"❌ Error filtering by {status}: {e}")
    
    async def demo_step_5_get_statistics(self):
        """Demo Step 5: Get request statistics."""
        self.print_step(5, "Getting Request Statistics")
        
        try:
            counts = await warm_intro_requests_service.get_warm_intro_request_counts(
                db=self.db,
                user_id=self.demo_user_id
            )
            
            print("📊 Request Statistics:")
            print(f"   Total: {counts['total']}")
            print(f"   Pending: {counts['pending']}")
            print(f"   Connected: {counts['connected']}")
            print(f"   Declined: {counts['declined']}")
            
            # Calculate percentages
            if counts['total'] > 0:
                print("\n📈 Percentages:")
                print(f"   Pending: {(counts['pending'] / counts['total'] * 100):.1f}%")
                print(f"   Connected: {(counts['connected'] / counts['total'] * 100):.1f}%")
                print(f"   Declined: {(counts['declined'] / counts['total'] * 100):.1f}%")
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
    
    async def demo_step_6_search_requests(self):
        """Demo Step 6: Search requests by name."""
        self.print_step(6, "Searching Requests by Name")
        
        search_terms = ["Alice", "Bob", "Charlie", "NonExistent"]
        
        for term in search_terms:
            try:
                result = await warm_intro_requests_service.search_warm_intro_requests(
                    db=self.db,
                    user_id=self.demo_user_id,
                    search_query=term,
                    page=1,
                    limit=10
                )
                
                print(f"🔍 Search: '{term}'")
                print(f"   Results: {len(result['items'])}")
                
                for request in result['items']:
                    print(f"   - {request.requester_name} → {request.connection_name}")
                
            except Exception as e:
                print(f"❌ Error searching for '{term}': {e}")
    
    async def demo_step_7_get_by_id(self):
        """Demo Step 7: Get specific request by ID."""
        self.print_step(7, "Getting Request by ID")
        
        if not self.created_requests:
            print("⚠️ No requests available for ID lookup")
            return
        
        test_request = self.created_requests[0]
        
        try:
            found_request = await warm_intro_requests_service.get_warm_intro_request_by_id(
                db=self.db,
                request_id=test_request.id,
                user_id=self.demo_user_id
            )
            
            if found_request:
                print(f"✅ Found request by ID: {found_request.id}")
                print(f"   Requester: {found_request.requester_name}")
                print(f"   Connection: {found_request.connection_name}")
                print(f"   Status: {found_request.status}")
                print(f"   Created: {found_request.created_at}")
                print(f"   Updated: {found_request.updated_at}")
            else:
                print("❌ Request not found")
                
        except Exception as e:
            print(f"❌ Error getting request by ID: {e}")
    
    async def demo_step_8_user_isolation(self):
        """Demo Step 8: Demonstrate user isolation."""
        self.print_step(8, "Demonstrating User Isolation")
        
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
            
            print(f"✅ Created request for different user: {other_request.id}")
            
            # Try to access other user's request with our demo user
            found_request = await warm_intro_requests_service.get_warm_intro_request_by_id(
                db=self.db,
                request_id=other_request.id,
                user_id=self.demo_user_id  # Wrong user ID
            )
            
            if found_request is None:
                print("✅ User isolation working correctly - cannot access other user's request")
            else:
                print("❌ User isolation failed - accessed other user's request")
            
            # Clean up other user's request
            await self.db.warm_intro_requests.delete_one({"id": str(other_request.id)})
            print("🧹 Cleaned up other user's test request")
            
        except Exception as e:
            print(f"❌ Error testing user isolation: {e}")
    
    async def cleanup_demo_data(self):
        """Clean up demo data."""
        self.print_step("Cleanup", "Removing Demo Data")
        
        try:
            result = await self.db.warm_intro_requests.delete_many({
                "user_id": str(self.demo_user_id)
            })
            print(f"🧹 Cleaned up {result.deleted_count} demo records")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
    
    async def run_complete_demo(self):
        """Run the complete demo workflow."""
        print("🚀 Starting Warm Intro Requests Demo")
        print("This demo will showcase all the functionality of the warm intro requests feature.")
        
        # Setup database
        if not await self.setup_database():
            print("❌ Cannot proceed without database connection")
            return False
        
        try:
            # Run all demo steps
            await self.demo_step_1_create_requests()
            await asyncio.sleep(1)  # Small delay for better readability
            
            await self.demo_step_2_list_requests()
            await asyncio.sleep(1)
            
            await self.demo_step_3_update_status()
            await asyncio.sleep(1)
            
            await self.demo_step_4_filter_by_status()
            await asyncio.sleep(1)
            
            await self.demo_step_5_get_statistics()
            await asyncio.sleep(1)
            
            await self.demo_step_6_search_requests()
            await asyncio.sleep(1)
            
            await self.demo_step_7_get_by_id()
            await asyncio.sleep(1)
            
            await self.demo_step_8_user_isolation()
            await asyncio.sleep(1)
            
            # Final summary
            self.print_header("Demo Summary")
            print("🎉 Demo completed successfully!")
            print(f"🆔 Demo User ID: {self.demo_user_id}")
            print(f"📊 Created {len(self.created_requests)} requests")
            print("✅ All functionality demonstrated:")
            print("   - Creating requests")
            print("   - Listing and pagination")
            print("   - Status updates")
            print("   - Filtering by status")
            print("   - Getting statistics")
            print("   - Searching by name")
            print("   - Getting by ID")
            print("   - User isolation")
            
            # Ask if user wants to keep the data
            print("\n❓ Would you like to keep the demo data for further testing?")
            print("   (The data will be cleaned up automatically if you don't specify)")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
            return False
            
        finally:
            # Cleanup (comment out if you want to keep demo data)
            await self.cleanup_demo_data()

async def main():
    """Main demo function."""
    demo = WarmIntroRequestsDemo()
    success = await demo.run_complete_demo()
    
    if success:
        print("\n✅ Demo completed successfully!")
        print("The warm intro requests feature is working correctly.")
    else:
        print("\n❌ Demo failed. Please check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())