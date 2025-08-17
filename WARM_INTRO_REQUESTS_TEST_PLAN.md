# Warm Intro Requests - Comprehensive Test Plan

## Overview
This document outlines the comprehensive test plan for the Warm Intro Requests feature, covering backend services, API endpoints, frontend components, and end-to-end user workflows.

## Backend Tests

### Automated Test Suite
Run the automated backend test suite:
```bash
cd Dev/superconnectoraiv2/backend
python test_warm_intro_requests.py
```

### Test Coverage
The automated test suite covers:

#### 1. Model Validation Tests
- ✅ Valid WarmIntroRequest model creation
- ✅ Enum validation for all status types (pending, connected, declined)
- ✅ Model serialization and deserialization
- ✅ UUID generation and timestamp handling

#### 2. Service Layer Tests
- ✅ Create warm intro requests
- ✅ Retrieve requests with pagination
- ✅ Filter requests by status
- ✅ Get request by ID
- ✅ Update request status
- ✅ Get count statistics by status
- ✅ Search requests by name
- ✅ Delete requests
- ✅ User isolation (security)

#### 3. Database Integration Tests
- ✅ MongoDB connection and operations
- ✅ Data persistence verification
- ✅ Index performance (created_at DESC, status+created_at composite)
- ✅ User-scoped data isolation

## API Endpoint Tests

### Manual API Testing
Use tools like Postman, curl, or the browser to test these endpoints:

#### 1. Create Warm Intro Request
```bash
POST /api/v1/warm-intro-requests/
Authorization: Bearer <token>
Content-Type: application/json

{
  "requester_name": "John Doe",
  "connection_name": "Jane Smith",
  "status": "pending"
}
```

**Expected Response:** 201 Created with request details

#### 2. Get Warm Intro Requests (Paginated)
```bash
GET /api/v1/warm-intro-requests/?page=1&limit=10&status=pending
Authorization: Bearer <token>
```

**Expected Response:** 200 OK with paginated results

#### 3. Get Request by ID
```bash
GET /api/v1/warm-intro-requests/{request_id}
Authorization: Bearer <token>
```

**Expected Response:** 200 OK with request details or 404 Not Found

#### 4. Update Request Status
```bash
PATCH /api/v1/warm-intro-requests/{request_id}/status
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "connected"
}
```

**Expected Response:** 200 OK with updated request

#### 5. Get Statistics
```bash
GET /api/v1/warm-intro-requests/stats/counts
Authorization: Bearer <token>
```

**Expected Response:** 200 OK with count statistics

### Security Tests
- ✅ Authentication required for all endpoints
- ✅ User can only access their own requests
- ✅ Proper error handling for unauthorized access
- ✅ Input validation and sanitization

## Frontend Tests

### Component Testing Checklist

#### 1. Warm Intro Modal Integration
- [ ] Modal opens when warm intro is requested
- [ ] Form validation works correctly
- [ ] Successful submission creates database record
- [ ] Error handling displays appropriate messages
- [ ] Modal closes after successful submission
- [ ] Database record is created with correct data

#### 2. Warm Intro Requests Page
- [ ] Page loads without errors
- [ ] Navigation link works correctly
- [ ] Requests are displayed in a table format
- [ ] Pagination controls work properly
- [ ] Status filter dropdown functions correctly
- [ ] Status badges display correct colors
- [ ] Statistics cards show accurate counts
- [ ] Refresh button updates data

#### 3. Status Management
- [ ] Status update buttons appear for pending requests
- [ ] Connect button changes status to "connected"
- [ ] Decline button changes status to "declined"
- [ ] Reset button changes status back to "pending"
- [ ] Optimistic UI updates work correctly
- [ ] Error handling for failed status updates

#### 4. URL Persistence
- [ ] Page number persists in URL
- [ ] Status filter persists in URL
- [ ] Browser back/forward buttons work correctly
- [ ] Direct URL access works with parameters
- [ ] URL updates when filters change

#### 5. Responsive Design
- [ ] Page works on desktop (1920x1080)
- [ ] Page works on tablet (768x1024)
- [ ] Page works on mobile (375x667)
- [ ] Table scrolls horizontally on small screens
- [ ] Navigation adapts to screen size

## End-to-End User Workflow Tests

### Test Scenario 1: Complete Warm Intro Flow
1. **Setup:** User is logged in and on the dashboard
2. **Action:** User clicks on a connection and requests warm intro
3. **Verify:** Modal opens with correct connection details
4. **Action:** User fills out the form and submits
5. **Verify:** Success message appears and modal closes
6. **Action:** User navigates to Warm Intro Requests page
7. **Verify:** New request appears in the list with "pending" status
8. **Action:** User clicks "Connect" button
9. **Verify:** Status changes to "connected" and UI updates
10. **Verify:** Statistics cards update to reflect new counts

### Test Scenario 2: Filtering and Pagination
1. **Setup:** Multiple warm intro requests exist with different statuses
2. **Action:** User navigates to Warm Intro Requests page
3. **Verify:** All requests are displayed by default
4. **Action:** User selects "Pending" from status filter
5. **Verify:** Only pending requests are shown
6. **Verify:** URL updates with status parameter
7. **Action:** User navigates to page 2 (if applicable)
8. **Verify:** Pagination works and URL updates
9. **Action:** User refreshes the page
10. **Verify:** Filters and pagination state are preserved

### Test Scenario 3: Error Handling
1. **Setup:** User is on Warm Intro Requests page
2. **Action:** Simulate network error (disconnect internet)
3. **Action:** User tries to update a request status
4. **Verify:** Error message is displayed
5. **Verify:** UI doesn't break and remains functional
6. **Action:** Restore network connection
7. **Action:** User clicks refresh
8. **Verify:** Data loads correctly

## Performance Tests

### Load Testing
- [ ] Page loads within 2 seconds with 100 requests
- [ ] Pagination performs well with large datasets
- [ ] Status updates respond within 1 second
- [ ] Search functionality is responsive

### Database Performance
- [ ] Queries use proper indexes
- [ ] Pagination doesn't cause N+1 queries
- [ ] Status filtering is efficient
- [ ] User isolation doesn't impact performance

## Browser Compatibility Tests

### Desktop Browsers
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

### Mobile Browsers
- [ ] Chrome Mobile
- [ ] Safari Mobile
- [ ] Firefox Mobile

## Accessibility Tests

### WCAG Compliance
- [ ] Keyboard navigation works throughout
- [ ] Screen reader compatibility
- [ ] Color contrast meets standards
- [ ] Focus indicators are visible
- [ ] Alt text for images/icons
- [ ] Proper heading hierarchy

## Data Integrity Tests

### Database Consistency
- [ ] Timestamps are accurate and consistent
- [ ] Status transitions are logged correctly
- [ ] User associations are maintained
- [ ] No orphaned records after operations

### Backup and Recovery
- [ ] Data survives server restarts
- [ ] Database migrations work correctly
- [ ] Data export/import functionality

## Security Tests

### Authentication & Authorization
- [ ] Unauthenticated users cannot access endpoints
- [ ] Users cannot access other users' data
- [ ] JWT tokens are validated correctly
- [ ] Session management works properly

### Input Validation
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF protection
- [ ] Input sanitization

## Test Results Documentation

### Test Execution Log
Document test results in this format:

```
Test: [Test Name]
Date: [YYYY-MM-DD]
Tester: [Name]
Result: [PASS/FAIL]
Notes: [Any observations or issues]
```

### Bug Tracking
- Use GitHub issues or similar for bug tracking
- Include steps to reproduce
- Attach screenshots/logs when applicable
- Assign priority levels

## Continuous Testing

### Automated Testing Integration
- Backend tests run on every deployment
- API tests included in CI/CD pipeline
- Performance monitoring in production

### Manual Testing Schedule
- Full regression testing before major releases
- Smoke testing after each deployment
- User acceptance testing with stakeholders

## Test Data Management

### Test Data Setup
```sql
-- Sample test data for manual testing
INSERT INTO warm_intro_requests (user_id, requester_name, connection_name, status, created_at, updated_at)
VALUES 
  ('user-123', 'Alice Johnson', 'Bob Wilson', 'pending', NOW(), NOW()),
  ('user-123', 'Charlie Brown', 'Diana Prince', 'connected', NOW(), NOW()),
  ('user-123', 'Eve Adams', 'Frank Miller', 'declined', NOW(), NOW());
```

### Test Data Cleanup
- Automated cleanup after test runs
- Separate test database for development
- Data anonymization for production testing

---

## Conclusion

This comprehensive test plan ensures the Warm Intro Requests feature is thoroughly tested across all layers of the application. Regular execution of these tests will maintain high quality and reliability of the feature.

For questions or issues with testing, refer to the development team or create an issue in the project repository.