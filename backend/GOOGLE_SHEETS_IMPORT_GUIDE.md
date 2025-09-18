# 📊 Google Sheets Import Guide

## Quick Start

**Yes, I can absolutely load from a Google Sheets link!** No need for Excel conversion.

### Simple Usage
```bash
cd backend
python load_google_sheets_connections.py
# Then paste your Google Sheets URL when prompted
```

### Command Line Usage
```bash
cd backend
python load_google_sheets_connections.py "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
```

## 🔧 How It Works

### 1. URL Processing
- Accepts any Google Sheets URL format
- Automatically converts to CSV export URL
- Downloads data directly from Google Sheets

### 2. Smart Column Mapping
The script automatically recognizes common column variations:

**Name Fields**:
- `name`, `full_name`, `full name`, `contact_name`
- `first_name` + `last_name` → combined into `name`

**Company Fields**:
- `company`, `organization`, `employer`, `current_company`

**Title Fields**:
- `title`, `position`, `job_title`, `role`

**Location Fields**:
- `location`, `city`, `region`

**LinkedIn Fields**:
- `linkedin`, `linkedin_url`, `linkedin_profile`, `profile_url`

**Other Fields**:
- `email`, `email_address`
- `description`, `bio`, `summary`, `about`

### 3. Data Processing
- Standardizes column names (lowercase, underscores)
- Fills missing required fields
- Creates MongoDB-compatible documents
- Adds timestamps and default values

## 📋 Google Sheets Requirements

### 1. Make Sheet Public
**Important**: The Google Sheet must be publicly accessible
- Go to your Google Sheet
- Click "Share" → "Change to anyone with the link"
- Set permission to "Viewer"

### 2. Expected Columns
**Minimum Required**:
- Name (or first_name + last_name)
- Company
- Title

**Recommended Additional Columns**:
- Location
- LinkedIn URL
- Email
- Description/Bio

### 3. Data Format
- First row should contain column headers
- No merged cells in data rows
- Text data preferred (avoid complex formulas)

## 🚀 Import Process

### Step 1: Prepare Your Sheet
```
Name          | Company        | Title              | Location      | LinkedIn
John Smith    | Google         | Product Manager    | San Francisco | linkedin.com/in/johnsmith
Jane Doe      | Microsoft      | Software Engineer  | Seattle       | linkedin.com/in/janedoe
```

### Step 2: Run Import
```bash
cd backend
python load_google_sheets_connections.py
```

### Step 3: Provide URL
```
📋 Enter Google Sheets URL: https://docs.google.com/spreadsheets/d/1ABC123.../edit
```

### Step 4: Review Preview
```
📋 Data Preview (first 3 rows):
     Name          Company        Title
0    John Smith    Google         Product Manager
1    Jane Doe      Microsoft      Software Engineer
2    ...

📊 Columns found: ['name', 'company', 'title', 'location', 'linkedin']

❓ Proceed to load 15000 connections? (y/N):
```

### Step 5: Confirm Import
```
✅ Successfully inserted 15000 connections
📊 Total connections in database: 15010
```

## 🔍 Supported URL Formats

All these formats work:
```
https://docs.google.com/spreadsheets/d/1ABC123DEF456/edit#gid=0
https://docs.google.com/spreadsheets/d/1ABC123DEF456/edit
https://docs.google.com/spreadsheets/d/1ABC123DEF456/
```

## 🛠️ Troubleshooting

### Common Issues

**1. "Could not extract sheet ID from URL"**
- Check URL format
- Ensure it's a Google Sheets URL
- Try copying the URL directly from browser

**2. "Error loading from Google Sheets"**
- Make sure sheet is publicly accessible
- Check internet connection
- Verify sheet isn't empty

**3. "No connections to insert"**
- Check that first row contains headers
- Ensure at least 'name' column exists
- Verify data rows aren't empty

### Data Quality Tips

**1. Clean Your Data**:
- Remove empty rows
- Standardize company names
- Use consistent formatting

**2. LinkedIn URLs**:
- Full URLs work best: `https://linkedin.com/in/username`
- Short URLs also work: `linkedin.com/in/username`

**3. Location Format**:
- "City, State" or "City, Country" preferred
- Consistent formatting helps search

## 📊 After Import

### 1. Verify Import
```bash
cd backend
python migrate_production_connections.py
```

### 2. Test Search
- Visit http://localhost:3000
- Try searching for specific people or companies
- Test various search terms

### 3. Check Data Quality
- Review connection details
- Verify search results accuracy
- Test different search queries

## 🎯 Expected Results

After successful import:
- **15,000+ connections** loaded into local database
- **Full search functionality** with real data
- **Gemini AI-powered** search and ranking
- **MongoDB fallback** for reliable results

---

**Ready to import?** Just provide your Google Sheets URL and the script will handle everything automatically!