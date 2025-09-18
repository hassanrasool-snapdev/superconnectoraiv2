#!/usr/bin/env python3
"""
Test script to verify Gemini integration is working correctly.
This script tests both the embeddings service and AI service.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.gemini_embeddings_service import gemini_embeddings_service
from app.services.ai_service import generate_email_content

async def test_gemini_embeddings():
    """Test Gemini embeddings service"""
    print("🧪 Testing Gemini Embeddings Service...")
    
    try:
        # Test single embedding generation
        test_text = "Software engineer with 5 years of experience in Python and machine learning"
        embedding = await gemini_embeddings_service.generate_embedding(test_text)
        
        print(f"✅ Successfully generated embedding for text: '{test_text[:50]}...'")
        print(f"   Embedding dimension: {len(embedding)}")
        print(f"   First 5 values: {embedding[:5]}")
        
        # Test batch embedding generation
        test_texts = [
            "Data scientist with expertise in deep learning",
            "Product manager with experience in SaaS companies",
            "Marketing specialist focused on digital campaigns"
        ]
        
        embeddings = await gemini_embeddings_service.generate_embeddings_batch(test_texts)
        print(f"✅ Successfully generated {len(embeddings)} batch embeddings")
        print(f"   All embeddings have same dimension: {all(len(emb) == len(embeddings[0]) for emb in embeddings)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini embeddings test failed: {e}")
        return False

async def test_gemini_ai_service():
    """Test Gemini AI service for text generation"""
    print("\n🧪 Testing Gemini AI Service...")
    
    try:
        # Test email content generation
        test_reason = "I would like to connect with you to discuss potential collaboration opportunities in AI and machine learning projects."
        
        email_content = await generate_email_content(test_reason)
        
        print(f"✅ Successfully generated email content")
        print(f"   Reason: '{test_reason[:50]}...'")
        print(f"   Generated email preview: '{email_content[:100]}...'")
        print(f"   Email length: {len(email_content)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini AI service test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Gemini Integration Tests\n")
    
    # Test embeddings service
    embeddings_success = await test_gemini_embeddings()
    
    # Test AI service
    ai_service_success = await test_gemini_ai_service()
    
    # Summary
    print("\n📊 Test Results Summary:")
    print(f"   Gemini Embeddings Service: {'✅ PASS' if embeddings_success else '❌ FAIL'}")
    print(f"   Gemini AI Service: {'✅ PASS' if ai_service_success else '❌ FAIL'}")
    
    if embeddings_success and ai_service_success:
        print("\n🎉 All tests passed! Gemini integration is working correctly.")
        print("   The system has been successfully migrated from OpenAI to Gemini.")
        return True
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)