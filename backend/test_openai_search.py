import asyncio
from app.services.retrieval_service import retrieval_service

async def test_openai_search():
    result = await retrieval_service.retrieve_and_rerank('Product leader at Open AI', '5741eb91-8eb7-41f1-acb3-7ec46dfacca9')
    print(f'Found {len(result)} results for OpenAI search')
    for i, r in enumerate(result):
        profile = r.get('profile', {})
        print(f'{i+1}. {profile.get("fullName", "Unknown")} - {profile.get("title", "Unknown")} at {profile.get("companyName", "Unknown")}')

if __name__ == "__main__":
    asyncio.run(test_openai_search())