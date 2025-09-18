#!/usr/bin/env python3
"""
Google Sheets Connection Loader for SuperconnectAI
Loads connections directly from a Google Sheets URL
"""

import os
import sys
import pandas as pd
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_sheet_id_from_url(url):
    """Extract Google Sheets ID from various URL formats"""
    if '/spreadsheets/d/' in url:
        # Standard Google Sheets URL
        sheet_id = url.split('/spreadsheets/d/')[1].split('/')[0]
        return sheet_id
    elif 'docs.google.com' in url:
        # Alternative format
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
    
    # Convert to CSV export URL
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    return csv_url

def load_from_google_sheets(sheets_url):
    """Load data from Google Sheets URL"""
    try:
        print(f"🔗 Processing Google Sheets URL...")
        csv_url = convert_to_csv_url(sheets_url)
        print(f"📥 Downloading data from: {csv_url}")
        
        # Read CSV data directly from Google Sheets
        df = pd.read_csv(csv_url)
        print(f"✅ Successfully loaded {len(df)} rows from Google Sheets")
        return df
        
    except Exception as e:
        print(f"❌ Error loading from Google Sheets: {str(e)}")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure the Google Sheet is publicly accessible (Anyone with the link can view)")
        print("2. Check that the URL is correct")
        print("3. Ensure the sheet contains the expected columns")
        return None

def standardize_connection_data(df):
    """Standardize column names and data format"""
    print("🔧 Standardizing connection data...")
    
    # Common column name mappings
    column_mappings = {
        # Name variations
        'name': 'name',
        'full_name': 'name',
        'full name': 'name',
        'contact_name': 'name',
        'first_name': 'first_name',
        'last_name': 'last_name',
        
        # Company variations
        'company': 'company',
        'organization': 'company',
        'employer': 'company',
        'current_company': 'company',
        
        # Title variations
        'title': 'title',
        'position': 'title',
        'job_title': 'title',
        'role': 'title',
        
        # Location variations
        'location': 'location',
        'city': 'location',
        'region': 'location',
        
        # LinkedIn variations
        'linkedin': 'linkedin_url',
        'linkedin_url': 'linkedin_url',
        'linkedin_profile': 'linkedin_url',
        'profile_url': 'linkedin_url',
        
        # Email variations
        'email': 'email',
        'email_address': 'email',
        
        # Description/Bio variations
        'description': 'description',
        'bio': 'description',
        'summary': 'description',
        'about': 'description'
    }
    
    # Normalize column names (lowercase, replace spaces with underscores)
    df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')
    
    # Apply column mappings
    df = df.rename(columns=column_mappings)
    
    # Ensure required fields exist
    required_fields = ['name', 'company', 'title']
    for field in required_fields:
        if field not in df.columns:
            if field == 'name' and 'first_name' in df.columns and 'last_name' in df.columns:
                df['name'] = df['first_name'].fillna('') + ' ' + df['last_name'].fillna('')
            else:
                df[field] = ''
    
    # Clean up data
    df = df.fillna('')
    
    print(f"📊 Standardized columns: {list(df.columns)}")
    return df

def create_connection_documents(df):
    """Convert DataFrame to MongoDB connection documents"""
    print("📝 Creating connection documents...")
    
    connections = []
    for index, row in df.iterrows():
        # Create connection document
        connection = {
            "name": str(row.get('name', '')).strip(),
            "company": str(row.get('company', '')).strip(),
            "title": str(row.get('title', '')).strip(),
            "location": str(row.get('location', '')).strip(),
            "linkedin_url": str(row.get('linkedin_url', '')).strip(),
            "email": str(row.get('email', '')).strip(),
            "description": str(row.get('description', '')).strip(),
            "connection_strength": "2nd",  # Default connection strength
            "tags": [],
            "notes": "",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Add any additional fields from the spreadsheet
        for col in df.columns:
            if col not in ['name', 'company', 'title', 'location', 'linkedin_url', 'email', 'description']:
                connection[col] = str(row.get(col, '')).strip()
        
        # Only add connections with at least a name
        if connection['name']:
            connections.append(connection)
    
    print(f"✅ Created {len(connections)} connection documents")
    return connections

def save_to_mongodb(connections):
    """Save connections to MongoDB"""
    try:
        # Connect to MongoDB
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL not found in environment variables")
        
        print(f"🔗 Connecting to MongoDB...")
        client = MongoClient(database_url)
        db = client.get_default_database()
        collection = db.connections
        
        print(f"💾 Saving {len(connections)} connections to MongoDB...")
        
        # Insert connections
        if connections:
            result = collection.insert_many(connections)
            print(f"✅ Successfully inserted {len(result.inserted_ids)} connections")
            
            # Show summary
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
    print("🚀 Google Sheets Connection Loader")
    print("=" * 50)
    
    # Check if URL provided as argument
    if len(sys.argv) > 1:
        sheets_url = sys.argv[1]
    else:
        sheets_url = input("📋 Enter Google Sheets URL: ").strip()
    
    if not sheets_url:
        print("❌ No URL provided")
        return
    
    # Load data from Google Sheets
    df = load_from_google_sheets(sheets_url)
    if df is None:
        return
    
    # Show preview of data
    print(f"\n📋 Data Preview (first 3 rows):")
    print(df.head(3).to_string())
    print(f"\n📊 Columns found: {list(df.columns)}")
    
    # Ask for confirmation
    proceed = input(f"\n❓ Proceed to load {len(df)} connections? (y/N): ").strip().lower()
    if proceed != 'y':
        print("❌ Operation cancelled")
        return
    
    # Standardize data
    df = standardize_connection_data(df)
    
    # Create connection documents
    connections = create_connection_documents(df)
    
    # Save to MongoDB
    success = save_to_mongodb(connections)
    
    if success:
        print("\n🎉 Google Sheets import completed successfully!")
        print("\n📋 Next steps:")
        print("1. Test search functionality at http://localhost:3000")
        print("2. Verify connections are searchable")
        print("3. Check data quality and completeness")
    else:
        print("\n❌ Import failed. Please check the error messages above.")

if __name__ == "__main__":
    main()