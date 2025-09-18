#!/usr/bin/env python3
"""
Automated Google Sheets Connection Loader for SuperconnectAI
Automatically imports connections from Google Sheets without manual confirmation
"""

import os
import sys
import pandas as pd
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_sheet_id_from_url(url):
    """Extract Google Sheets ID from various URL formats"""
    if '/spreadsheets/d/' in url:
        sheet_id = url.split('/spreadsheets/d/')[1].split('/')[0]
        return sheet_id
    elif 'docs.google.com' in url:
        parts = url.split('/')
        for i, part in enumerate(parts):
            if part == 'd' and i + 1 < len(parts):
                return parts[i + 1]
    return None

def convert_to_csv_url(sheets_url):
    """Convert Google Sheets URL to CSV export URL"""
    sheet_id = extract_sheet_id_from_url(sheets_url)
    if not sheet_id:
        raise ValueError("Could not extract sheet ID from URL")
    
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    return csv_url

def load_from_google_sheets(sheets_url):
    """Load data from Google Sheets URL"""
    try:
        print(f"🔗 Processing Google Sheets URL...")
        csv_url = convert_to_csv_url(sheets_url)
        print(f"📥 Downloading data from: {csv_url}")
        
        df = pd.read_csv(csv_url)
        print(f"✅ Successfully loaded {len(df)} rows from Google Sheets")
        return df
        
    except Exception as e:
        print(f"❌ Error loading from Google Sheets: {str(e)}")
        return None

def create_connection_documents(df):
    """Convert DataFrame to MongoDB connection documents"""
    print("📝 Creating connection documents...")
    
    connections = []
    for index, row in df.iterrows():
        # Map Google Sheets columns to our connection format
        connection = {
            "name": str(row.get('fullName', row.get('firstName', '') + ' ' + row.get('lastName', ''))).strip(),
            "company": str(row.get('companyName', '')).strip(),
            "title": str(row.get('headline', '')).strip(),
            "location": (str(row.get('city', '') if pd.notna(row.get('city')) else '') + ', ' + str(row.get('country', '') if pd.notna(row.get('country')) else '')).strip().strip(',').strip(),
            "linkedin_url": f"https://linkedin.com/in/{row.get('publicIdentifier', '')}" if row.get('publicIdentifier') else '',
            "email": '',  # Not available in LinkedIn data
            "description": str(row.get('about', '')).strip(),
            "connection_strength": "1st",  # LinkedIn connections are 1st degree
            "tags": [],
            "notes": "",
            "experiences": str(row.get('experiences', '')).strip(),
            "education": str(row.get('education', '')).strip(),
            "skills": str(row.get('skills', '')).strip(),
            "follower_count": int(row.get('followerCount', 0)) if pd.notna(row.get('followerCount')) else 0,
            "connections_count": int(row.get('connectionsCount', 0)) if pd.notna(row.get('connectionsCount')) else 0,
            "is_premium": bool(row.get('isPremium', False)),
            "is_creator": bool(row.get('isCreator', False)),
            "is_influencer": bool(row.get('isInfluencer', False)),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Only add connections with at least a name
        if connection['name'] and connection['name'] != 'nan':
            connections.append(connection)
    
    print(f"✅ Created {len(connections)} connection documents")
    return connections

def save_to_mongodb(connections):
    """Save connections to MongoDB"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL not found in environment variables")
        
        print(f"🔗 Connecting to MongoDB...")
        client = MongoClient(database_url)
        db = client.get_default_database()
        collection = db.connections
        
        print(f"💾 Saving {len(connections)} connections to MongoDB...")
        
        if connections:
            # Clear existing connections first
            print("🗑️ Clearing existing connections...")
            collection.delete_many({})
            
            # Insert new connections
            result = collection.insert_many(connections)
            print(f"✅ Successfully inserted {len(result.inserted_ids)} connections")
            
            total_connections = collection.count_documents({})
            print(f"📊 Total connections in database: {total_connections}")
            
            return True
        else:
            print("⚠️ No connections to insert")
            return False
            
    except Exception as e:
        print(f"❌ Error saving to MongoDB: {str(e)}")
        return False

def main():
    print("🚀 Automated Google Sheets Connection Loader")
    print("=" * 50)
    
    # Use the provided Google Sheets URL
    sheets_url = "https://docs.google.com/spreadsheets/d/1sRu_umuWAmMYYbD_ST3LibIcrVb8bdLsHF8i3qNXAdo/edit?gid=1114436387#gid=1114436387"
    
    # Load data from Google Sheets
    df = load_from_google_sheets(sheets_url)
    if df is None:
        print("❌ Failed to load data from Google Sheets")
        return
    
    print(f"\n📊 Loaded {len(df)} rows with columns: {list(df.columns)}")
    
    # Create connection documents
    connections = create_connection_documents(df)
    
    # Save to MongoDB
    success = save_to_mongodb(connections)
    
    if success:
        print("\n🎉 Google Sheets import completed successfully!")
        print(f"📊 Imported {len(connections)} connections")
        print("\n📋 Next steps:")
        print("1. Test search functionality at http://localhost:3000")
        print("2. Verify connections are searchable")
        print("3. Check data quality and completeness")
    else:
        print("\n❌ Import failed. Please check the error messages above.")

if __name__ == "__main__":
    main()