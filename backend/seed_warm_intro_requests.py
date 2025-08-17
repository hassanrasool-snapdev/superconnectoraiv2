#!/usr/bin/env python3
"""
Seed script for warm intro requests.
This script creates sample warm intro requests for testing and demonstration purposes.
"""

import asyncio
import sys
import os
from uuid import uuid4
from datetime import datetime, timedelta
import random

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.warm_intro_request import WarmIntroRequest, WarmIntroStatus
from app.services import warm_intro_requests_service
from motor.motor_asyncio import AsyncIOMotorClient

class WarmIntroRequestsSeeder:
    def __init__(self):
        self.db = None
        self.demo_user_id = uuid4()
        
    async def setup_database(self):
        """Setup database connection."""
        print("🔌 Connecting to MongoDB...")
        try:
            client = AsyncIOMotorClient("mongodb://localhost:27017")
            self.db = client.superconnect  # Use the main database
            print("✅ Database connection established")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    async def clear_existing_demo_data(self):
        """Clear any existing demo data."""
        print("🧹 Clearing existing demo data...")
        try:
            result = await self.db.warm_intro_requests.delete_many({
                "user_id": str(self.demo_user_id)
            })
            print(f"✅ Cleared {result.deleted_count} existing demo records")
        except Exception as e:
            print(f"⚠️ Warning during cleanup: {e}")
    
    def generate_sample_data(self):
        """Generate sample warm intro request data."""
        
        # Sample requester names (people asking for intros)
        requesters = [
            "Alice Johnson", "Bob Chen", "Carol Martinez", "David Kim", 
            "Emma Thompson", "Frank Rodriguez", "Grace Liu", "Henry Wilson",
            "Isabella Garcia", "Jack Anderson", "Kate Brown", "Liam Davis",
            "Maya Patel", "Noah Taylor", "Olivia White", "Paul Jackson"
        ]
        
        # Sample connection names (people being introduced to)
        connections = [
            "Sarah Mitchell", "Michael Chang", "Jennifer Lopez", "Robert Taylor",
            "Amanda Foster", "Christopher Lee", "Jessica Wang", "Daniel Smith",
            "Rachel Green", "Matthew Jones", "Lauren Adams", "Kevin Park",
            "Stephanie Clark", "Brandon Miller", "Nicole Turner", "Justin Hall",
            "Megan Cooper", "Tyler Reed", "Ashley Morgan", "Jordan Bell",
            "Samantha Gray", "Ryan Phillips", "Brittany Evans", "Austin King"
        ]
        
        # Generate sample requests with realistic distribution
        sample_requests = []
        
        # Create requests with different statuses and dates
        for i in range(25):  # Generate 25 sample requests
            # Random date within the last 30 days
            days_ago = random.randint(0, 30)
            created_date = datetime.utcnow() - timedelta(days=days_ago)
            
            # Status distribution: 60% pending, 25% connected, 15% declined
            status_weights = [
                (WarmIntroStatus.pending, 0.6),
                (WarmIntroStatus.connected, 0.25),
                (WarmIntroStatus.declined, 0.15)
            ]
            
            rand = random.random()
            cumulative = 0
            status = WarmIntroStatus.pending
            for s, weight in status_weights:
                cumulative += weight
                if rand <= cumulative:
                    status = s
                    break
            
            # Create the request
            request_data = {
                "user_id": self.demo_user_id,
                "requester_name": random.choice(requesters),
                "connection_name": random.choice(connections),
                "status": status,
                "created_at": created_date,
                "updated_at": created_date if status == WarmIntroStatus.pending else created_date + timedelta(hours=random.randint(1, 48))
            }
            
            sample_requests.append(request_data)
        
        return sample_requests
    
    async def seed_warm_intro_requests(self):
        """Seed the database with sample warm intro requests."""
        print("🌱 Seeding warm intro requests...")
        
        sample_data = self.generate_sample_data()
        created_count = 0
        
        for data in sample_data:
            try:
                # Create WarmIntroRequest object
                request = WarmIntroRequest(
                    id=uuid4(),
                    user_id=data["user_id"],
                    requester_name=data["requester_name"],
                    connection_name=data["connection_name"],
                    status=data["status"],
                    created_at=data["created_at"],
                    updated_at=data["updated_at"]
                )
                
                # Insert directly into database
                await self.db.warm_intro_requests.insert_one(request.model_dump(by_alias=True))
                created_count += 1
                
                print(f"✅ Created: {request.requester_name} → {request.connection_name} ({request.status})")
                
            except Exception as e:
                print(f"❌ Failed to create request: {e}")
        
        print(f"\n🎉 Successfully created {created_count} warm intro requests!")
        return created_count
    
    async def display_statistics(self):
        """Display statistics of the seeded data."""
        print("\n📊 Seeded Data Statistics:")
        print("=" * 50)
        
        try:
            # Get counts by status
            counts = await warm_intro_requests_service.get_warm_intro_request_counts(
                db=self.db,
                user_id=self.demo_user_id
            )
            
            print(f"Total Requests: {counts['total']}")
            print(f"Pending: {counts['pending']}")
            print(f"Connected: {counts['connected']}")
            print(f"Declined: {counts['declined']}")
            
            # Get recent requests
            recent_requests = await warm_intro_requests_service.get_warm_intro_requests(
                db=self.db,
                user_id=self.demo_user_id,
                page=1,
                limit=5
            )
            
            print(f"\n📋 Recent Requests (Top 5):")
            for i, request in enumerate(recent_requests['items'], 1):
                print(f"{i}. {request.requester_name} → {request.connection_name} ({request.status})")
            
        except Exception as e:
            print(f"❌ Error displaying statistics: {e}")
    
    async def create_demo_user_info(self):
        """Create a demo user info file for easy reference."""
        demo_info = f"""
# Demo User Information

## User ID
{self.demo_user_id}

## Usage Instructions

### 1. Backend Testing
Use this user ID when testing the backend services:

```python
user_id = UUID("{self.demo_user_id}")
```

### 2. API Testing
Use this user ID in your JWT token or authentication headers when testing API endpoints.

### 3. Frontend Testing
If you need to test with this specific user, ensure your authentication system returns this user ID.

### 4. Database Queries
To view the seeded data directly in MongoDB:

```javascript
db.warm_intro_requests.find({{"user_id": "{self.demo_user_id}"}}).sort({{"created_at": -1}})
```

### 5. Cleanup
To remove all demo data:

```javascript
db.warm_intro_requests.deleteMany({{"user_id": "{self.demo_user_id}"}})
```

## Generated Data Summary
- 25 warm intro requests
- Mixed statuses (pending, connected, declined)
- Dates spanning the last 30 days
- Realistic requester and connection names
"""
        
        try:
            with open("DEMO_USER_INFO.md", "w") as f:
                f.write(demo_info)
            print(f"\n📝 Demo user info saved to DEMO_USER_INFO.md")
            print(f"🆔 Demo User ID: {self.demo_user_id}")
        except Exception as e:
            print(f"⚠️ Could not save demo user info: {e}")
    
    async def run_seeding(self):
        """Run the complete seeding process."""
        print("🚀 Starting Warm Intro Requests Seeding Process")
        print("=" * 60)
        
        # Setup database
        if not await self.setup_database():
            print("❌ Cannot proceed without database connection")
            return False
        
        try:
            # Clear existing demo data
            await self.clear_existing_demo_data()
            
            # Seed new data
            created_count = await self.seed_warm_intro_requests()
            
            # Display statistics
            await self.display_statistics()
            
            # Create demo user info
            await self.create_demo_user_info()
            
            print("\n" + "=" * 60)
            print("🎉 Seeding process completed successfully!")
            print(f"📊 Created {created_count} warm intro requests")
            print(f"🆔 Demo User ID: {self.demo_user_id}")
            print("📝 Check DEMO_USER_INFO.md for usage instructions")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Seeding process failed: {e}")
            return False

async def main():
    """Main seeding function."""
    seeder = WarmIntroRequestsSeeder()
    success = await seeder.run_seeding()
    
    if success:
        print("\n✅ Seeding completed successfully!")
        print("You can now test the warm intro requests functionality with the generated data.")
    else:
        print("\n❌ Seeding failed. Please check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())