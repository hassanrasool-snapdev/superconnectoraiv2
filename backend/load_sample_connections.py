#!/usr/bin/env python3
"""
Script to load sample connections data for testing the search functionality.
This will create sample connections in MongoDB and generate embeddings in Pinecone.
"""

import asyncio
import sys
import os
from datetime import datetime
from uuid import uuid4

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.db import get_database
from app.services.gemini_embeddings_service import gemini_embeddings_service
import pandas as pd

# Sample connections data
SAMPLE_CONNECTIONS = [
    {
        "fullName": "Sarah Johnson",
        "firstName": "Sarah",
        "lastName": "Johnson",
        "headline": "Senior Product Manager at Tech Innovations Inc",
        "about": "Experienced product manager with 8+ years in SaaS and fintech. Passionate about user experience and data-driven product decisions. Led multiple successful product launches.",
        "city": "San Francisco",
        "state": "California",
        "country": "United States",
        "companyName": "Tech Innovations Inc",
        "title": "Senior Product Manager",
        "experiences": "Product Manager at StartupXYZ (2019-2022), Associate Product Manager at BigCorp (2017-2019)",
        "education": "MBA from Stanford University, BS Computer Science from UC Berkeley",
        "skills": "Product Management, Data Analysis, User Research, Agile, SQL, Python",
        "linkedin_url": "https://linkedin.com/in/sarah-johnson-pm",
        "publicIdentifier": "sarah-johnson-pm",
        "followerCount": 2500,
        "connectionsCount": 1200,
        "isOpenToWork": False,
        "isHiring": True,
        "company_industry": "Technology",
        "company_size": "201-500 employees"
    },
    {
        "fullName": "Michael Chen",
        "firstName": "Michael",
        "lastName": "Chen",
        "headline": "Software Engineering Manager at Redwood Credit Union",
        "about": "Engineering leader with 10+ years experience building scalable financial systems. Expert in cloud architecture and team leadership.",
        "city": "Santa Rosa",
        "state": "California", 
        "country": "United States",
        "companyName": "Redwood Credit Union",
        "title": "Software Engineering Manager",
        "experiences": "Senior Software Engineer at FinanceApp (2018-2021), Software Engineer at BankTech (2015-2018)",
        "education": "MS Computer Science from UC Davis, BS Engineering from Cal Poly",
        "skills": "Software Engineering, Team Leadership, Cloud Architecture, Python, Java, AWS",
        "linkedin_url": "https://linkedin.com/in/michael-chen-eng",
        "publicIdentifier": "michael-chen-eng",
        "followerCount": 1800,
        "connectionsCount": 950,
        "isOpenToWork": False,
        "isHiring": True,
        "company_industry": "Financial Services",
        "company_size": "1001-5000 employees"
    },
    {
        "fullName": "Emily Rodriguez",
        "firstName": "Emily",
        "lastName": "Rodriguez",
        "headline": "VP of Product at Redwood Credit Union",
        "about": "Product executive with 12+ years in financial services. Led digital transformation initiatives and mobile banking product development.",
        "city": "San Rafael",
        "state": "California",
        "country": "United States", 
        "companyName": "Redwood Credit Union",
        "title": "VP of Product",
        "experiences": "Director of Product at CreditTech (2019-2022), Senior Product Manager at FinanceFirst (2016-2019)",
        "education": "MBA from UC Berkeley Haas, BA Economics from UCLA",
        "skills": "Product Strategy, Digital Banking, Team Leadership, Fintech, Mobile Apps",
        "linkedin_url": "https://linkedin.com/in/emily-rodriguez-vp",
        "publicIdentifier": "emily-rodriguez-vp",
        "followerCount": 3200,
        "connectionsCount": 1500,
        "isOpenToWork": False,
        "isHiring": True,
        "company_industry": "Financial Services",
        "company_size": "1001-5000 employees"
    },
    {
        "fullName": "David Kim",
        "firstName": "David",
        "lastName": "Kim",
        "headline": "Data Scientist at Google",
        "about": "Machine learning engineer and data scientist with expertise in NLP and recommendation systems. PhD in Computer Science.",
        "city": "Mountain View",
        "state": "California",
        "country": "United States",
        "companyName": "Google",
        "title": "Senior Data Scientist",
        "experiences": "Data Scientist at Meta (2020-2023), ML Engineer at Netflix (2018-2020)",
        "education": "PhD Computer Science from MIT, MS Statistics from Stanford",
        "skills": "Machine Learning, Python, TensorFlow, NLP, Data Science, Statistics",
        "linkedin_url": "https://linkedin.com/in/david-kim-ds",
        "publicIdentifier": "david-kim-ds",
        "followerCount": 4500,
        "connectionsCount": 2100,
        "isOpenToWork": False,
        "isHiring": False,
        "company_industry": "Technology",
        "company_size": "10000+ employees"
    },
    {
        "fullName": "Lisa Thompson",
        "firstName": "Lisa",
        "lastName": "Thompson",
        "headline": "Marketing Director at Startup Accelerator",
        "about": "Growth marketing expert with 7+ years helping startups scale. Specialized in B2B SaaS marketing and demand generation.",
        "city": "Austin",
        "state": "Texas",
        "country": "United States",
        "companyName": "Startup Accelerator",
        "title": "Marketing Director",
        "experiences": "Senior Marketing Manager at SaaS Company (2019-2022), Marketing Specialist at TechStart (2017-2019)",
        "education": "MBA Marketing from UT Austin, BA Communications from Texas A&M",
        "skills": "Digital Marketing, Growth Hacking, B2B Marketing, Content Strategy, Analytics",
        "linkedin_url": "https://linkedin.com/in/lisa-thompson-marketing",
        "publicIdentifier": "lisa-thompson-marketing",
        "followerCount": 1900,
        "connectionsCount": 1100,
        "isOpenToWork": False,
        "isHiring": True,
        "company_industry": "Technology",
        "company_size": "11-50 employees"
    },
    {
        "fullName": "James Wilson",
        "firstName": "James",
        "lastName": "Wilson",
        "headline": "Founder & CEO at FinTech Innovations",
        "about": "Serial entrepreneur with 15+ years in fintech. Founded 3 companies, 2 successful exits. Angel investor and startup advisor.",
        "city": "New York",
        "state": "New York",
        "country": "United States",
        "companyName": "FinTech Innovations",
        "title": "Founder & CEO",
        "experiences": "Co-founder at PaymentTech (2018-2022, acquired), VP Product at BigBank (2015-2018)",
        "education": "MBA from Wharton, BS Finance from NYU Stern",
        "skills": "Entrepreneurship, Fintech, Product Strategy, Fundraising, Team Building",
        "linkedin_url": "https://linkedin.com/in/james-wilson-ceo",
        "publicIdentifier": "james-wilson-ceo",
        "followerCount": 5200,
        "connectionsCount": 2800,
        "isOpenToWork": False,
        "isHiring": True,
        "is_company_owner": True,
        "company_industry": "Financial Services",
        "company_size": "51-200 employees"
    }
]

async def load_sample_connections():
    """Load sample connections for the test user"""
    
    # User ID from the terminal logs
    user_id = "5741eb91-8eb7-41f1-acb3-7ec46dfacca9"
    
    print(f"🚀 Loading sample connections for user: {user_id}")
    
    try:
        # Initialize database connection
        from app.core.db import connect_to_mongo
        await connect_to_mongo()
        
        # Get database connection
        db = get_database()
        connections_collection = db.connections
        
        # Prepare connections data
        connections_to_insert = []
        vectors_for_pinecone = []
        
        for i, conn_data in enumerate(SAMPLE_CONNECTIONS):
            # Add required fields
            connection_doc = {
                **conn_data,
                "_id": str(uuid4()),
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "urn": f"urn:li:person:{uuid4()}",
                "connected_on": "2024-01-15"
            }
            
            connections_to_insert.append(connection_doc)
            
            # Generate embedding for this connection
            print(f"📝 Processing connection {i+1}/{len(SAMPLE_CONNECTIONS)}: {conn_data['fullName']}")
            
            # Create a pandas Series to use the canonicalize_profile_text method
            row_data = pd.Series(conn_data)
            canonical_text = gemini_embeddings_service.canonicalize_profile_text(row_data)
            
            # Generate embedding
            embedding = await gemini_embeddings_service.generate_embedding(canonical_text)
            
            # Extract metadata for Pinecone
            metadata = gemini_embeddings_service.extract_metadata(row_data)
            metadata["canonical_text"] = canonical_text
            
            # Prepare vector for Pinecone
            vector_id = connection_doc["_id"]
            vectors_for_pinecone.append((vector_id, embedding, metadata))
            
            print(f"   ✅ Generated {len(embedding)}-dimensional embedding")
        
        # Insert connections into MongoDB
        print(f"\n💾 Inserting {len(connections_to_insert)} connections into MongoDB...")
        result = await connections_collection.insert_many(connections_to_insert)
        print(f"   ✅ Inserted {len(result.inserted_ids)} connections")
        
        # Upload vectors to Pinecone
        print(f"\n🔍 Uploading {len(vectors_for_pinecone)} vectors to Pinecone...")
        gemini_embeddings_service.batch_upsert_to_pinecone(vectors_for_pinecone, namespace=user_id)
        print(f"   ✅ Uploaded vectors to namespace: {user_id}")
        
        print(f"\n🎉 Successfully loaded sample connections!")
        print(f"   - MongoDB: {len(connections_to_insert)} connections")
        print(f"   - Pinecone: {len(vectors_for_pinecone)} vectors")
        print(f"   - User namespace: {user_id}")
        
        # Test search functionality
        print(f"\n🧪 Testing search functionality...")
        from app.services.retrieval_service import retrieval_service
        
        test_query = "product manager at redwood credit union"
        results = await retrieval_service.retrieve_and_rerank(
            user_query=test_query,
            user_id=user_id,
            enable_query_rewrite=True
        )
        
        print(f"   ✅ Search test completed: Found {len(results)} results for '{test_query}'")
        if results:
            for i, result in enumerate(results[:3]):
                profile = result.get('profile', {})
                print(f"      {i+1}. {profile.get('fullName', 'Unknown')} - Score: {result.get('score', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading sample connections: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(load_sample_connections())
    sys.exit(0 if success else 1)