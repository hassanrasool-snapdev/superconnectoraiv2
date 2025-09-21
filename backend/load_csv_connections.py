import asyncio
import csv
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import uuid

async def load_connections_from_csv():
    """Load connections from CSV files into MongoDB"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(os.getenv("DATABASE_URL", "mongodb+srv://ha:suLbGZ1mStktaqEl@cluster0.bfftr4a.mongodb.net/superconnector?retryWrites=true&w=majority&appName=Cluster0"))
    db = client.superconnect_ai
    
    # Clear existing connections first
    result = await db.connections.delete_many({})
    print(f"Cleared {result.deleted_count} existing connections")
    
    connections_loaded = 0
    
    # Load from updated_connections.csv (larger file)
    csv_file = "updated_connections.csv"
    if os.path.exists(csv_file):
        print(f"Loading connections from {csv_file}...")
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            connections = []
            
            for row in reader:
                # Create connection document
                connection = {
                    "_id": str(uuid.uuid4()),
                    "fullName": row.get('fullName', '').strip(),
                    "headline": row.get('headline', ''),
                    "about": row.get('about', ''),
                    "city": row.get('city', ''),
                    "country": row.get('country', ''),
                    "companyName": row.get('companyName', ''),
                    "title": row.get('title', ''),
                    "experiences": row.get('experiences', ''),
                    "education": row.get('education', ''),
                    "skills": row.get('skills', ''),
                    "linkedin_url": row.get('linkedin_url', ''),
                    "followerCount": int(str(row.get('followerCount', '0')).replace(',', '').replace('K', '000').replace('M', '000000')) if row.get('followerCount') else 0,
                    "connectionsCount": int(row.get('connectionsCount', '0')) if row.get('connectionsCount') else 0,
                    "isOpenToWork": row.get('isOpenToWork', '').lower() == 'true',
                    "isHiring": row.get('isHiring', '').lower() == 'true',
                    "is_company_owner": row.get('is_company_owner', '').lower() == 'true',
                    "company_industry": row.get('company_industry', ''),
                    "company_size": row.get('company_size', ''),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                # Skip empty connections
                if connection["fullName"].strip() and connection["companyName"]:
                    connections.append(connection)
                    connections_loaded += 1
                
                # Batch insert every 100 connections
                if len(connections) >= 100:
                    await db.connections.insert_many(connections)
                    print(f"Inserted batch of {len(connections)} connections...")
                    connections = []
            
            # Insert remaining connections
            if connections:
                await db.connections.insert_many(connections)
                print(f"Inserted final batch of {len(connections)} connections...")
    
    # Also load from Connections.csv for additional data
    csv_file2 = "Connections.csv"
    if os.path.exists(csv_file2):
        print(f"Loading additional connections from {csv_file2}...")
        
        with open(csv_file2, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            connections = []
            
            for row in reader:
                # Skip if we already have this person (check by LinkedIn URL)
                linkedin_url = row.get('LinkedinUrl', '')
                if linkedin_url:
                    existing = await db.connections.find_one({"linkedin_url": linkedin_url})
                    if existing:
                        continue
                
                connection = {
                    "_id": str(uuid.uuid4()),
                    "fullName": row.get('fullName', '').strip(),
                    "headline": row.get('headline', ''),
                    "about": row.get('about', ''),
                    "city": row.get('city', ''),
                    "country": row.get('country', ''),
                    "companyName": row.get('companyName', ''),
                    "title": row.get('title', ''),
                    "experiences": row.get('experiences', ''),
                    "education": row.get('education', ''),
                    "skills": row.get('skills', ''),
                    "linkedin_url": linkedin_url,
                    "followerCount": int(str(row.get('followerCount', '0')).replace(',', '').replace('K', '000').replace('M', '000000')) if row.get('followerCount') else 0,
                    "connectionsCount": int(row.get('connectionsCount', '0')) if row.get('connectionsCount') else 0,
                    "isOpenToWork": row.get('isOpenToWork', '').lower() == 'true',
                    "isHiring": row.get('isHiring', '').lower() == 'true',
                    "is_company_owner": row.get('is_company_owner', '').lower() == 'true',
                    "company_industry": row.get('company_industry', ''),
                    "company_size": row.get('company_size', ''),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                if connection["fullName"].strip() and connection["companyName"]:
                    connections.append(connection)
                    connections_loaded += 1
            
            if connections:
                await db.connections.insert_many(connections)
                print(f"Inserted {len(connections)} additional connections from Connections.csv")
    
    # Get final count
    total_count = await db.connections.count_documents({})
    print(f"\n✅ Successfully loaded {connections_loaded} connections")
    print(f"📊 Total connections in database: {total_count}")
    
    # Show some sample connections
    sample_connections = await db.connections.find({}).limit(5).to_list(length=5)
    print(f"\n📋 Sample connections:")
    for i, conn in enumerate(sample_connections, 1):
        print(f"  {i}. {conn.get('fullName')} - {conn.get('title')} at {conn.get('companyName')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(load_connections_from_csv())