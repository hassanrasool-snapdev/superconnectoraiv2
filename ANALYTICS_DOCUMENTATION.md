# Warm Intro Requests Analytics System

## Overview

This document describes the comprehensive analytics system implemented for the warm intro requests feature. The system tracks user interactions, system performance, and business metrics to provide insights into user behavior and system health.

## Architecture

### Core Components

1. **Telemetry Service** (`/src/lib/telemetry.ts`)
   - Centralized event tracking system
   - Type-safe event definitions
   - Local storage for development/debugging
   - Session management and user identification

2. **Analytics Dashboard** (`/src/components/analytics/AnalyticsDashboard.tsx`)
   - Real-time metrics visualization
   - Event history and analysis
   - Data export capabilities
   - Performance monitoring

3. **Integration Points**
   - WarmIntroModal component (form interactions)
   - Warm intro requests page (status management)
   - API layer (performance tracking)

## Tracked Events

### Modal Interactions

#### `modal_opened`
Tracks when the warm intro modal is opened.
```typescript
{
  target_name: string;           // Name of the connection target
  target_company: string;        // Company of the target
  has_linkedin_url: boolean;     // Whether LinkedIn URL is available
  has_profile_picture: boolean;  // Whether profile picture is available
}
```

#### `modal_closed`
Tracks when the modal is closed and how.
```typescript
{
  target_name: string;              // Name of the connection target
  form_completion_percentage: number; // 0-100% form completion
  time_spent_seconds: number;       // Time spent in modal
  close_method: 'button' | 'escape' | 'outside_click' | 'unsaved_warning';
}
```

### Form Interactions

#### `form_field_focused`
Tracks when a form field receives focus.
```typescript
{
  field_name: string;               // Name of the focused field
  field_type: string;               // Type of field (text, textarea, etc.)
  form_completion_percentage: number; // Current form completion
}
```

#### `form_field_completed`
Tracks when a form field is completed and validated.
```typescript
{
  field_name: string;        // Name of the completed field
  field_length: number;      // Length of the entered content
  validation_passed: boolean; // Whether validation passed
}
```

#### `quick_chip_used`
Tracks usage of quick starter chips.
```typescript
{
  chip_label: string;           // Label of the used chip
  chip_text: string;            // Text inserted by the chip
  existing_text_length: number; // Length of existing text before insertion
}
```

#### `example_template_viewed`
Tracks when the example template is viewed.
```typescript
{
  target_name: string; // Name of the connection target
}
```

#### `example_template_applied`
Tracks when the example template is applied.
```typescript
{
  target_name: string;           // Name of the connection target
  overwrite_existing: boolean;   // Whether existing content was overwritten
  existing_reason_length: number; // Length of existing reason text
  existing_about_length: number;  // Length of existing about text
}
```

### Autosave Events

#### `autosave_triggered`
Tracks when autosave is triggered.
```typescript
{
  fields_saved: string[];    // Array of field names saved
  total_characters: number;  // Total characters saved
}
```

#### `autosave_restored`
Tracks when autosaved data is restored.
```typescript
{
  fields_restored: string[]; // Array of field names restored
  age_hours: number;         // Age of the restored data in hours
}
```

### Email Generation Events

#### `email_generation_started`
Tracks when email generation begins.
```typescript
{
  requester_name_length: number; // Length of requester name
  reason_length: number;         // Length of reason text
  about_length: number;          // Length of about text
  include_email: boolean;        // Whether email is included
  target_name: string;           // Name of the connection target
}
```

#### `email_client_opened`
Tracks successful email client opening.
```typescript
{
  method: 'link_click' | 'location_href' | 'window_open'; // Method used
  email_length: number; // Length of the generated email
}
```

#### `email_fallback_used`
Tracks when email fallback methods are used.
```typescript
{
  fallback_method: 'clipboard' | 'manual_alert'; // Fallback method used
  email_length: number; // Length of the email content
}
```

### Database Events

#### `warm_intro_request_created`
Tracks successful creation of warm intro requests.
```typescript
{
  requester_name: string;                    // Name of the requester
  connection_name: string;                   // Name of the connection
  creation_method: 'success' | 'fallback';  // How the request was created
}
```

#### `warm_intro_request_creation_failed`
Tracks failed creation attempts.
```typescript
{
  error_type: string;        // Type of error encountered
  requester_name: string;    // Name of the requester
  connection_name: string;   // Name of the connection
}
```

### Page Events

#### `requests_page_loaded`
Tracks when the requests page loads.
```typescript
{
  total_requests: number;   // Total number of requests
  pending_count: number;    // Number of pending requests
  connected_count: number;  // Number of connected requests
  declined_count: number;   // Number of declined requests
  current_page: number;     // Current page number
  status_filter: string;    // Applied status filter
}
```

#### `requests_page_filtered`
Tracks when filters are applied.
```typescript
{
  previous_filter: string; // Previous filter value
  new_filter: string;      // New filter value
  results_count: number;   // Number of results after filtering
}
```

#### `requests_page_paginated`
Tracks pagination interactions.
```typescript
{
  previous_page: number; // Previous page number
  new_page: number;      // New page number
  total_pages: number;   // Total number of pages
  status_filter: string; // Current status filter
}
```

#### `requests_page_refreshed`
Tracks manual page refreshes.
```typescript
{
  current_page: number;   // Current page number
  status_filter: string;  // Current status filter
  manual_refresh: boolean; // Whether refresh was manual
}
```

### Status Update Events

#### `status_update_initiated`
Tracks when a status update is initiated.
```typescript
{
  request_id: string;      // ID of the request being updated
  previous_status: string; // Previous status value
  new_status: string;      // New status value
  requester_name: string;  // Name of the requester
  connection_name: string; // Name of the connection
}
```

#### `status_update_completed`
Tracks successful status updates.
```typescript
{
  request_id: string;        // ID of the updated request
  previous_status: string;   // Previous status value
  new_status: string;        // New status value
  update_duration_ms: number; // Time taken for the update
}
```

#### `status_update_failed`
Tracks failed status updates.
```typescript
{
  request_id: string;      // ID of the request
  attempted_status: string; // Status that was attempted
  error_type: string;      // Type of error encountered
}
```

### Performance Events

#### `api_request_performance`
Tracks API request performance.
```typescript
{
  endpoint: string;      // API endpoint called
  method: string;        // HTTP method used
  duration_ms: number;   // Request duration in milliseconds
  status_code: number;   // HTTP status code
  success: boolean;      // Whether the request was successful
}
```

#### `page_load_performance`
Tracks page load performance.
```typescript
{
  page_name: string;           // Name of the page
  load_time_ms: number;        // Total load time
  initial_data_load_ms: number; // Time to load initial data
}
```

## Usage Examples

### Basic Event Tracking
```typescript
import { telemetry } from '@/lib/telemetry';

// Track a modal opening
telemetry.track('modal_opened', {
  target_name: 'John Smith',
  target_company: 'TechCorp',
  has_linkedin_url: true,
  has_profile_picture: false,
});
```

### Custom Event Tracking
```typescript
// Track custom events not in the predefined schema
telemetry.trackCustom('custom_interaction', {
  feature: 'warm_intro',
  action: 'special_case',
  value: 42,
});
```

### Helper Functions
```typescript
// Calculate form completion percentage
const completion = telemetry.calculateFormCompletion({
  name: 'John Doe',
  email: 'john@example.com',
  message: '',
  terms: true,
});

// Calculate time spent
const timeSpent = telemetry.calculateTimeSpent(startTime);
```

## Analytics Dashboard

### Accessing the Dashboard
Navigate to `/analytics` to view the comprehensive analytics dashboard.

### Key Metrics Displayed
- **Total Events**: Overall event count
- **Unique Sessions**: Number of unique user sessions
- **Requests Created**: Number of warm intro requests created
- **Average Time Spent**: Average time users spend in the modal
- **Form Completion Rate**: Average form completion percentage
- **Status Updates**: Number of status changes made

### Features
- **Real-time Updates**: Refresh button to load latest data
- **Data Export**: Export analytics data as JSON
- **Event History**: View recent events with details
- **Top Events**: Most frequently tracked events
- **Performance Metrics**: API response times and success rates

## Testing

### Automated Testing
Run the analytics test script to generate sample data:

```javascript
// In browser console
analyticsTest.generateTestData();
```

### Manual Testing Checklist
1. **Modal Interactions**
   - [ ] Open modal (track `modal_opened`)
   - [ ] Use quick chips (track `quick_chip_used`)
   - [ ] View example template (track `example_template_viewed`)
   - [ ] Apply template (track `example_template_applied`)
   - [ ] Fill form fields (track `form_field_focused`, `form_field_completed`)
   - [ ] Close modal (track `modal_closed`)

2. **Requests Page**
   - [ ] Load page (track `requests_page_loaded`)
   - [ ] Apply filters (track `requests_page_filtered`)
   - [ ] Change pages (track `requests_page_paginated`)
   - [ ] Update status (track `status_update_*`)
   - [ ] Refresh page (track `requests_page_refreshed`)

3. **Error Scenarios**
   - [ ] Form validation errors (track `form_validation_failed`)
   - [ ] Email client failures (track `email_fallback_used`)
   - [ ] API failures (track `*_failed` events)

### Data Validation
```javascript
// Validate stored analytics data
analyticsTest.validateAnalyticsData();
```

## Data Storage

### Development Environment
- Events are stored in `localStorage` under the key `telemetry_events`
- Maximum of 100 events stored locally to prevent storage bloat
- Data persists across browser sessions

### Production Environment
In production, events would be sent to an analytics service such as:
- Google Analytics
- Mixpanel
- Amplitude
- Custom analytics backend

## Privacy and Compliance

### Data Collection
- No personally identifiable information (PII) is collected
- User names and connection names are included for business metrics
- Session IDs are generated locally and not tied to user accounts
- No sensitive form content is tracked

### Data Retention
- Local storage: 100 most recent events
- Production: Follow company data retention policies
- Users can clear their analytics data via the dashboard

## Performance Considerations

### Client-Side Impact
- Minimal performance impact (< 1ms per event)
- Asynchronous event processing
- Local storage used for development only
- Events are batched in production

### Storage Efficiency
- Compact event structure
- Automatic cleanup of old events
- Configurable storage limits

## Troubleshooting

### Common Issues

#### Events Not Appearing
1. Check browser console for errors
2. Verify telemetry import is correct
3. Ensure localStorage is enabled
4. Check event structure matches schema

#### Dashboard Not Loading
1. Verify analytics page route exists
2. Check for component import errors
3. Ensure localStorage has data
4. Refresh the page

#### Performance Issues
1. Check event frequency (should be reasonable)
2. Verify local storage size
3. Clear old analytics data if needed

### Debug Commands
```javascript
// Get analytics summary
telemetry.getAnalyticsSummary();

// View all stored events
JSON.parse(localStorage.getItem('telemetry_events') || '[]');

// Clear analytics data
localStorage.removeItem('telemetry_events');
```

## Future Enhancements

### Planned Features
1. **Real-time Dashboard**: WebSocket-based live updates
2. **Advanced Filtering**: Date ranges, event types, user segments
3. **Export Formats**: CSV, Excel, PDF reports
4. **Alerting**: Automated alerts for anomalies
5. **A/B Testing**: Built-in experiment tracking
6. **Funnel Analysis**: User journey visualization
7. **Cohort Analysis**: User retention metrics

### Integration Opportunities
1. **Backend Analytics**: Server-side event tracking
2. **Error Monitoring**: Integration with Sentry/Bugsnag
3. **Performance Monitoring**: Integration with monitoring tools
4. **Business Intelligence**: Data warehouse integration

## Conclusion

The analytics system provides comprehensive insights into the warm intro requests feature, enabling data-driven decisions for product improvements and user experience optimization. The type-safe event system ensures consistent data collection, while the dashboard provides immediate visibility into key metrics and user behavior patterns.