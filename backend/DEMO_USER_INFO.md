
# Demo User Information

## User ID
9f3da685-9eaa-4f39-a2ae-2a7c17506c3d

## Usage Instructions

### 1. Backend Testing
Use this user ID when testing the backend services:

```python
user_id = UUID("9f3da685-9eaa-4f39-a2ae-2a7c17506c3d")
```

### 2. API Testing
Use this user ID in your JWT token or authentication headers when testing API endpoints.

### 3. Frontend Testing
If you need to test with this specific user, ensure your authentication system returns this user ID.

### 4. Database Queries
To view the seeded data directly in MongoDB:

```javascript
db.warm_intro_requests.find({"user_id": "9f3da685-9eaa-4f39-a2ae-2a7c17506c3d"}).sort({"created_at": -1})
```

### 5. Cleanup
To remove all demo data:

```javascript
db.warm_intro_requests.deleteMany({"user_id": "9f3da685-9eaa-4f39-a2ae-2a7c17506c3d"})
```

## Generated Data Summary
- 25 warm intro requests
- Mixed statuses (pending, connected, declined)
- Dates spanning the last 30 days
- Realistic requester and connection names
