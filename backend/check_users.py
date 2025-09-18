import os
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'superconnector')

client = MongoClient(DATABASE_URL, tlsCAFile=certifi.where())
db = client[DATABASE_NAME]

users = list(db.users.find({}, {'email': 1, 'id': 1, '_id': 0}))
print('Available users:')
for user in users[:5]:  # Show first 5 users
    print(f'  - {user.get("email", "No email")} (ID: {user.get("id", "No ID")})')

client.close()