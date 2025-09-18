import os
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'superconnector')

client = MongoClient(DATABASE_URL, tlsCAFile=certifi.where())
db = client[DATABASE_NAME]

# Fix the user record by adding missing role field
test_email = "ha@nextstepfwd.com"

# Update the user to include the missing role field
result = db.users.update_one(
    {"email": test_email},
    {
        "$set": {
            "role": "user"  # Set default role as 'user'
        }
    }
)

if result.modified_count > 0:
    print(f"✅ Successfully added role field to user {test_email}")
    
    # Verify the update
    user = db.users.find_one({"email": test_email})
    print(f"📋 User record now has role: {user.get('role', 'NOT SET')}")
else:
    print(f"❌ Failed to update user {test_email}")

client.close()