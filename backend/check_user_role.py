import asyncio
from app.core.db import get_database, connect_to_mongo

async def check_user_role():
    await connect_to_mongo()
    db = get_database()
    user = await db.users.find_one({'email': 'ha@nextstepfwd.com'})
    if user:
        print(f'User found: {user.get("email")}')
        print(f'Role: {user.get("role", "No role field")}')
        print(f'Full user data: {user}')
    else:
        print('User not found')

if __name__ == "__main__":
    asyncio.run(check_user_role())