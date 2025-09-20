#!/usr/bin/env python3
"""
Manual trigger script for testing automated follow-up emails.
Manually invokes the process_automated_follow_ups function and prints email content to console.
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import connect_to_mongo, get_database, close_mongo_connection
from app.services.follow_up_email_service import (
    get_eligible_warm_intro_requests,
    send_automated_follow_up_email,
    generate_automated_follow_up_content
)

# Configure logging to show email content
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def simulate_email_send_with_output(to_email: str, subject: str, html_content: str) -> bool:
    """Enhanced simulation that prints the full email content for testing"""
    print("\n" + "=" * 80)
    print("📧 SIMULATED EMAIL SEND - FOLLOW-UP EMAIL CONTENT")
    print("=" * 80)
    print(f"📬 TO: {to_email}")
    print(f"📝 SUBJECT: {subject}")
    print(f"📅 TIMESTAMP: {datetime.utcnow()}")
    print("-" * 80)
    print("📄 EMAIL CONTENT (HTML):")
    print("-" * 80)
    print(html_content)
    print("-" * 80)
    print("🔗 RESPONSE LINKS EXTRACTED:")
    print("-" * 80)
    
    # Extract and display the response links for easy testing
    import re
    yes_link_match = re.search(r'href="([^"]*response=yes[^"]*)"', html_content)
    no_link_match = re.search(r'href="([^"]*response=no[^"]*)"', html_content)
    donate_link_match = re.search(r'href="([^"]*donate[^"]*)"', html_content)
    
    if yes_link_match:
        print(f"✅ YES LINK: {yes_link_match.group(1)}")
    if no_link_match:
        print(f"❌ NO LINK: {no_link_match.group(1)}")
    if donate_link_match:
        print(f"💰 DONATE LINK: {donate_link_match.group(1)}")
    
    print("=" * 80)
    print("✨ Copy and paste these links into your browser to test the response pages!")
    print("=" * 80)
    
    return True

async def manual_process_follow_ups():
    """Manually process automated follow-ups with enhanced output for testing"""
    
    # Connect to database
    await connect_to_mongo()
    db = get_database()
    
    print("🔍 Searching for eligible warm intro requests...")
    
    # Get eligible requests
    eligible_requests = await get_eligible_warm_intro_requests(db)
    
    if not eligible_requests:
        print("❌ No eligible warm intro requests found for follow-up.")
        print("💡 Make sure you've run 'python seed_test_follow_up.py' first!")
        await close_mongo_connection()
        return 0
    
    print(f"✅ Found {len(eligible_requests)} eligible request(s) for follow-up")
    
    sent_count = 0
    
    for i, request in enumerate(eligible_requests, 1):
        print(f"\n📋 Processing request {i}/{len(eligible_requests)}:")
        print(f"   Request ID: {request['id']}")
        print(f"   Requester: {request['requester_name']}")
        print(f"   Connection: {request['connection_name']}")
        print(f"   Created: {request['created_at']}")
        print(f"   Status: {request['status']}")
        
        # Get user email
        user = await db.users.find_one({"id": request["user_id"]})
        if not user:
            print(f"❌ User not found for request {request['id']}")
            continue
        
        user_email = user["email"]
        
        # Generate email content
        email_content = generate_automated_follow_up_content(
            request["requester_name"],
            request["connection_name"],
            request["id"]
        )
        
        # Simulate sending email with enhanced output
        success = await simulate_email_send_with_output(
            to_email=user_email,
            subject="Following up on your introduction request",
            html_content=email_content
        )
        
        if success:
            # Update the warm intro request with follow-up sent date
            await db.warm_intro_requests.update_one(
                {"id": request["id"]},
                {
                    "$set": {
                        "follow_up_sent_date": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            sent_count += 1
            print(f"✅ Follow-up email processed for request {request['id']}")
        else:
            print(f"❌ Failed to process follow-up email for request {request['id']}")
    
    print(f"\n🎉 SUMMARY: Successfully processed {sent_count} follow-up email(s)")
    
    # Close database connection
    await close_mongo_connection()
    
    return sent_count

async def main():
    """Main function to run the trigger script"""
    try:
        print("🚀 AUTOMATED FOLLOW-UP EMAIL TRIGGER SCRIPT")
        print("=" * 50)
        print("This script will:")
        print("1. Find eligible warm intro requests (15+ days old)")
        print("2. Generate follow-up emails")
        print("3. Print email content to console (simulated send)")
        print("4. Update database with follow_up_sent_date")
        print("=" * 50)
        
        sent_count = await manual_process_follow_ups()
        
        if sent_count > 0:
            print(f"\n✨ SUCCESS: Processed {sent_count} follow-up email(s)")
            print("📋 Next steps for testing:")
            print("1. Copy the response links from the email content above")
            print("2. Follow-up emails now ask users to reply directly to the email")
            print("3. The warm-intro-response pages have been removed from the system")
            print("4. Check that the donate page works correctly")
        else:
            print("\n⚠️  No emails were processed.")
            print("💡 Make sure to run 'python seed_test_follow_up.py' first!")
        
        return sent_count
        
    except Exception as e:
        print(f"❌ Error processing follow-ups: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    asyncio.run(main())