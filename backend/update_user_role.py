import asyncio
from app.core.db import get_database, connect_to_mongo

async def update_user_role():
    await connect_to_mongo()
    db = get_database()
    
    # Update the user's role to admin
    result = await db.users.update_one(
        {'email': 'ha@nextstepfwd.com'},
        {'$set': {'role': 'admin'}}
    )
    
    if result.modified_count > 0:
        print(f'Successfully updated user role to admin')
        
        # Verify the update
        user = await db.users.find_one({'email': 'ha@nextstepfwd.com'})
        print(f'Updated user role: {user.get("role")}')
    else:
        print('No user was updated')

if __name__ == "__main__":
    asyncio.run(update_user_role())