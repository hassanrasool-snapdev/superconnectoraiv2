import asyncio
from app.core.db import connect_to_mongo, get_database
from datetime import datetime

async def debug_pending_counts():
    await connect_to_mongo()
    db = get_database()
    
    print("=== DEBUGGING PENDING COUNTS ===")
    
    # Check warm intro requests
    print("\n--- Warm Intro Requests ---")
    warm_intro_total = await db.warm_intro_requests.count_documents({})
    warm_intro_pending = await db.warm_intro_requests.count_documents({"status": "pending"})
    print(f"Total warm intro requests: {warm_intro_total}")
    print(f"Pending warm intro requests: {warm_intro_pending}")
    
    # Get some sample pending requests
    pending_requests = await db.warm_intro_requests.find({"status": "pending"}).limit(5).to_list(length=None)
    print(f"Sample pending requests:")
    for req in pending_requests:
        print(f"  - ID: {req.get('id', req.get('_id'))}, Requester: {req.get('requester_name')}, Status: {req.get('status')}")
    
    # Check follow-up emails
    print("\n--- Follow-up Emails ---")
    follow_up_total = await db.follow_up_emails.count_documents({})
    follow_up_scheduled = await db.follow_up_emails.count_documents({"status": "scheduled"})
    current_time = datetime.utcnow()
    follow_up_due = await db.follow_up_emails.count_documents({
        "status": "scheduled",
        "scheduled_date": {"$lte": current_time}
    })
    print(f"Total follow-up emails: {follow_up_total}")
    print(f"Scheduled follow-up emails: {follow_up_scheduled}")
    print(f"Due follow-up emails: {follow_up_due}")
    
    # Check access requests
    print("\n--- Access Requests ---")
    access_total = await db.access_requests.count_documents({})
    access_pending = await db.access_requests.count_documents({"status": "pending"})
    print(f"Total access requests: {access_total}")
    print(f"Pending access requests: {access_pending}")
    
    print("\n=== END DEBUG ===")

if __name__ == "__main__":
    asyncio.run(debug_pending_counts())