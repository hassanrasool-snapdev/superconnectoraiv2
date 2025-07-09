#!/usr/bin/env python3
"""
Test script for the embeddings functionality.
This script demonstrates how to use the embeddings service.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.embeddings_service import EmbeddingsService

async def test_canonicalization():
    """Test the canonicalization function."""
    print("=== Testing Profile Text Canonicalization ===")
    
    service = EmbeddingsService()
    
    # Test data
    test_cases = [
        {
            "name": "John Doe Sr.",
            "headline": "Senior Software Engineer",
            "experience": "Experienced developer with <strong>10+ years</strong> in Python 🐍",
            "skills": "Python, JavaScript, React",
            "location": "San Francisco, CA"
        },
        {
            "name": "Jane Smith",
            "headline": "Product Manager",
            "experience": "Leading product teams at tech startups",
            "skills": "Product Strategy, Agile, Scrum",
            "location": "New York, NY"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Original: {test_case}")
        
        canonical = service.canonicalize_profile_text(
            name=test_case["name"],
            headline=test_case["headline"],
            experience=test_case["experience"],
            skills=test_case["skills"],
            location=test_case["location"]
        )
        
        print(f"Canonicalized: '{canonical}'")

async def test_embedding_generation():
    """Test embedding generation (requires OpenAI API key)."""
    print("\n=== Testing Embedding Generation ===")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Skipping embedding test - OPENAI_API_KEY not set")
        return
    
    service = EmbeddingsService()
    
    test_text = "john doe senior software engineer experienced developer with 10+ years in python python, javascript, react san francisco, ca"
    
    try:
        embedding = await service.generate_embedding(test_text)
        print(f"Generated embedding with {len(embedding)} dimensions")
        print(f"First 5 values: {embedding[:5]}")
        print(f"Embedding type: {type(embedding[0])}")
    except Exception as e:
        print(f"Error generating embedding: {e}")

async def test_csv_loading():
    """Test CSV data loading."""
    print("\n=== Testing CSV Data Loading ===")
    
    service = EmbeddingsService()
    
    try:
        df = service.load_connections_data("Connections.csv")
        print(f"Loaded {len(df)} rows from CSV")
        print(f"Columns: {list(df.columns)}")
        
        # Show first row metadata
        if len(df) > 0:
            first_row = df.iloc[0]
            metadata = service.extract_metadata(first_row)
            print(f"Sample metadata: {metadata}")
            
    except Exception as e:
        print(f"Error loading CSV: {e}")

async def main():
    """Run all tests."""
    print("Starting Embeddings Service Tests")
    print("=" * 50)
    
    await test_canonicalization()
    await test_embedding_generation()
    await test_csv_loading()
    
    print("\n" + "=" * 50)
    print("Tests completed!")

if __name__ == "__main__":
    asyncio.run(main())