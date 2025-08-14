import json
import re
from typing import List, Dict, Any
from app.core.config import settings
import openai

async def search_connections(user_id: str, query: str, connections: List[dict]) -> List[dict]:
    # This is a placeholder for the actual AI search logic.
    # In a real application, you would use a more sophisticated search algorithm.
    
    # For now, we'll just filter by query terms in the description or headline.
    query_terms = query.lower().split()
    
    matching_connections = []
    for conn in connections:
        description = conn.get('description', '') or ''
        headline = conn.get('headline', '') or ''
        
        if any(term in description.lower() or term in headline.lower() for term in query_terms):
            matching_connections.append(conn)
            
    return matching_connections

async def generate_email_content(reason: str) -> str:
    """
    Generate email content using OpenAI's GPT-4o.
    """
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    try:
        system_prompt = "You are a helpful assistant that writes professional outreach emails."
        user_prompt = f"Write a professional outreach email for the following reason: {reason}"

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating email content: {e}")
        return "Error generating email content."