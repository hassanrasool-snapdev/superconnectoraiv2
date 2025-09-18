import asyncio
from app.services.retrieval_service import retrieval_service

async def test_search():
    # Test search for someone we know is in the data
    result = await retrieval_service.retrieve_and_rerank('venture capital andreessen horowitz', '5741eb91-8eb7-41f1-acb3-7ec46dfacca9')
    print(f'Found {len(result)} results for Andreessen Horowitz search')
    for i, r in enumerate(result):
        profile = r.get('profile', {})
        print(f'{i+1}. {profile.get("fullName", "Unknown")} - {profile.get("title", "Unknown")} at {profile.get("companyName", "Unknown")}')
    
    print("\n" + "="*50)
    
    # Test search for Jason Calacanis
    result2 = await retrieval_service.retrieve_and_rerank('jason calacanis podcast', '5741eb91-8eb7-41f1-acb3-7ec46dfacca9')
    print(f'Found {len(result2)} results for Jason Calacanis search')
    for i, r in enumerate(result2):
        profile = r.get('profile', {})
        print(f'{i+1}. {profile.get("fullName", "Unknown")} - {profile.get("title", "Unknown")} at {profile.get("companyName", "Unknown")}')

if __name__ == "__main__":
    asyncio.run(test_search())