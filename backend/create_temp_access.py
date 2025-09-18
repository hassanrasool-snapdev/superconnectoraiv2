import os
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi
import bcrypt
from datetime import datetime

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'superconnector')

client = MongoClient(DATABASE_URL, tlsCAFile=certifi.where())
db = client[DATABASE_NAME]

# Create a simple password hash
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Option 1: Update existing user with known password
test_email = "ha@nextstepfwd.com"  # Using existing user
test_password = "temp123"  # Simple temporary password

# Hash the password
hashed_password = hash_password(test_password)

# Update the user's password
result = db.users.update_one(
    {"email": test_email},
    {
        "$set": {
            "hashed_password": hashed_password,
            "status": "active"
        }
    }
)

if result.modified_count > 0:
    print(f"✅ Successfully updated password for {test_email}")
    print(f"📧 Email: {test_email}")
    print(f"🔑 Password: {test_password}")
    print(f"🌐 Login at: http://localhost:3000/login")
else:
    print(f"❌ Failed to update user {test_email}")

client.close()