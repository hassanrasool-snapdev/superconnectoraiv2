/**
 * Analytics Testing Script
 * 
 * This script demonstrates and tests the comprehensive analytics system
 * implemented for the warm intro requests feature.
 * 
 * Run this in the browser console to generate sample analytics data.
 */

// Import telemetry (this would be available in the browser context)
// const { telemetry } = require('./src/lib/telemetry');

console.log('🔍 Analytics Testing Script for Warm Intro Requests');
console.log('================================================');

// Simulate a complete user journey through the warm intro system
function simulateUserJourney() {
  console.log('\n📊 Simulating complete user journey...');
  
  // 1. Modal opened
  telemetry.track('modal_opened', {
    target_name: 'John Smith',
    target_company: 'TechCorp Inc',
    has_linkedin_url: true,
    has_profile_picture: true,
  });
  
  // 2. User views example template
  setTimeout(() => {
    telemetry.track('example_template_viewed', {
      target_name: 'John Smith',
    });
  }, 1000);
  
  // 3. User uses quick chip
  setTimeout(() => {
    telemetry.track('quick_chip_used', {
      chip_label: 'Career advice',
      chip_text: "I'm exploring career opportunities in ",
      existing_text_length: 0,
    });
  }, 2000);
  
  // 4. Form field interactions
  setTimeout(() => {
    telemetry.track('form_field_focused', {
      field_name: 'requesterName',
      field_type: 'text',
      form_completion_percentage: 25,
    });
  }, 3000);
  
  setTimeout(() => {
    telemetry.track('form_field_completed', {
      field_name: 'requesterName',
      field_length: 12,
      validation_passed: true,
    });
  }, 4000);
  
  // 5. Autosave triggered
  setTimeout(() => {
    telemetry.track('autosave_triggered', {
      fields_saved: ['requesterName', 'reason'],
      total_characters: 85,
    });
  }, 5000);
  
  // 6. Email generation started
  setTimeout(() => {
    telemetry.track('email_generation_started', {
      requester_name_length: 12,
      reason_length: 45,
      about_length: 38,
      include_email: true,
      target_name: 'John Smith',
    });
  }, 6000);
  
  // 7. Email client opened successfully
  setTimeout(() => {
    telemetry.track('email_client_opened', {
      method: 'link_click',
      email_length: 342,
    });
  }, 7000);
  
  // 8. Warm intro request created
  setTimeout(() => {
    telemetry.track('warm_intro_request_created', {
      requester_name: 'Jane Doe',
      connection_name: 'John Smith',
      creation_method: 'success',
    });
  }, 8000);
  
  // 9. Modal closed
  setTimeout(() => {
    telemetry.track('modal_closed', {
      target_name: 'John Smith',
      form_completion_percentage: 100,
      time_spent_seconds: 45,
      close_method: 'button',
    });
  }, 9000);
  
  console.log('✅ User journey simulation completed!');
}

// Simulate requests page interactions
function simulateRequestsPageActivity() {
  console.log('\n📋 Simulating requests page activity...');
  
  // 1. Page loaded
  telemetry.track('requests_page_loaded', {
    total_requests: 15,
    pending_count: 8,
    connected_count: 5,
    declined_count: 2,
    current_page: 1,
    status_filter: 'all',
  });
  
  // 2. Filter applied
  setTimeout(() => {
    telemetry.track('requests_page_filtered', {
      previous_filter: 'all',
      new_filter: 'pending',
      results_count: 8,
    });
  }, 2000);
  
  // 3. Status update initiated
  setTimeout(() => {
    telemetry.track('status_update_initiated', {
      request_id: 'req_123',
      previous_status: 'pending',
      new_status: 'connected',
      requester_name: 'Alice Johnson',
      connection_name: 'Bob Wilson',
    });
  }, 4000);
  
  // 4. Status update completed
  setTimeout(() => {
    telemetry.track('status_update_completed', {
      request_id: 'req_123',
      previous_status: 'pending',
      new_status: 'connected',
      update_duration_ms: 850,
    });
  }, 5000);
  
  // 5. Page refreshed
  setTimeout(() => {
    telemetry.track('requests_page_refreshed', {
      current_page: 1,
      status_filter: 'pending',
      manual_refresh: true,
    });
  }, 7000);
  
  console.log('✅ Requests page simulation completed!');
}

// Simulate API performance tracking
function simulateAPIPerformance() {
  console.log('\n⚡ Simulating API performance tracking...');
  
  // Successful API calls
  telemetry.track('api_request_performance', {
    endpoint: '/warm-intro-requests',
    method: 'GET',
    duration_ms: 245,
    status_code: 200,
    success: true,
  });
  
  setTimeout(() => {
    telemetry.track('api_request_performance', {
      endpoint: '/warm-intro-requests/status',
      method: 'PUT',
      duration_ms: 180,
      status_code: 200,
      success: true,
    });
  }, 1000);
  
  // Failed API call
  setTimeout(() => {
    telemetry.track('api_request_performance', {
      endpoint: '/warm-intro-requests',
      method: 'POST',
      duration_ms: 5000,
      status_code: 500,
      success: false,
    });
  }, 2000);
  
  console.log('✅ API performance simulation completed!');
}

// Simulate error scenarios
function simulateErrorScenarios() {
  console.log('\n❌ Simulating error scenarios...');
  
  // Form validation failure
  telemetry.track('form_validation_failed', {
    invalid_fields: ['requesterLinkedIn', 'reason'],
    form_completion_percentage: 60,
    time_spent_seconds: 120,
  });
  
  // Email fallback used
  setTimeout(() => {
    telemetry.track('email_fallback_used', {
      fallback_method: 'clipboard',
      email_length: 298,
    });
  }, 1000);
  
  // Request creation failed
  setTimeout(() => {
    telemetry.track('warm_intro_request_creation_failed', {
      error_type: 'NetworkError',
      requester_name: 'Test User',
      connection_name: 'Test Connection',
    });
  }, 2000);
  
  // Status update failed
  setTimeout(() => {
    telemetry.track('status_update_failed', {
      request_id: 'req_456',
      attempted_status: 'connected',
      error_type: 'ValidationError',
    });
  }, 3000);
  
  console.log('✅ Error scenarios simulation completed!');
}

// Generate comprehensive test data
function generateTestData() {
  console.log('\n🎯 Generating comprehensive test data...');
  
  simulateUserJourney();
  
  setTimeout(() => {
    simulateRequestsPageActivity();
  }, 10000);
  
  setTimeout(() => {
    simulateAPIPerformance();
  }, 18000);
  
  setTimeout(() => {
    simulateErrorScenarios();
  }, 21000);
  
  setTimeout(() => {
    console.log('\n📈 Analytics Summary:');
    console.log('====================');
    const summary = telemetry.getAnalyticsSummary();
    console.log(`Session ID: ${summary.sessionId}`);
    console.log(`Total Events: ${summary.eventsCount}`);
    console.log(`Recent Events: ${summary.recentEvents.length}`);
    
    console.log('\n🎉 All analytics testing completed!');
    console.log('💡 Visit /analytics to view the dashboard');
    console.log('💾 Data is stored in localStorage under "telemetry_events"');
  }, 25000);
}

// Analytics validation functions
function validateAnalyticsData() {
  console.log('\n✅ Validating analytics data structure...');
  
  const events = JSON.parse(localStorage.getItem('telemetry_events') || '[]');
  
  if (events.length === 0) {
    console.log('⚠️  No analytics data found. Run generateTestData() first.');
    return;
  }
  
  const requiredFields = ['event_name', 'timestamp', 'session_id', 'properties'];
  const validEvents = events.filter(event => 
    requiredFields.every(field => event.hasOwnProperty(field))
  );
  
  console.log(`📊 Total events: ${events.length}`);
  console.log(`✅ Valid events: ${validEvents.length}`);
  console.log(`❌ Invalid events: ${events.length - validEvents.length}`);
  
  // Event type distribution
  const eventTypes = {};
  events.forEach(event => {
    eventTypes[event.event_name] = (eventTypes[event.event_name] || 0) + 1;
  });
  
  console.log('\n📈 Event Distribution:');
  Object.entries(eventTypes)
    .sort(([,a], [,b]) => b - a)
    .forEach(([event, count]) => {
      console.log(`  ${event}: ${count}`);
    });
}

// Export functions for browser console use
if (typeof window !== 'undefined') {
  window.analyticsTest = {
    generateTestData,
    simulateUserJourney,
    simulateRequestsPageActivity,
    simulateAPIPerformance,
    simulateErrorScenarios,
    validateAnalyticsData,
  };
  
  console.log('\n🚀 Analytics testing functions available:');
  console.log('  analyticsTest.generateTestData() - Generate all test data');
  console.log('  analyticsTest.simulateUserJourney() - Simulate modal interaction');
  console.log('  analyticsTest.simulateRequestsPageActivity() - Simulate page interactions');
  console.log('  analyticsTest.validateAnalyticsData() - Validate stored data');
}

// Instructions for manual testing
console.log('\n📋 Manual Testing Instructions:');
console.log('================================');
console.log('1. Open browser console on the warm intro requests page');
console.log('2. Run: analyticsTest.generateTestData()');
console.log('3. Wait for all simulations to complete (~25 seconds)');
console.log('4. Navigate to /analytics to view the dashboard');
console.log('5. Interact with the warm intro modal to generate real data');
console.log('6. Use analyticsTest.validateAnalyticsData() to check data quality');
console.log('\n🎯 Key Metrics to Verify:');
console.log('- Modal open/close events with timing');
console.log('- Form completion percentages');
console.log('- Email generation success/failure rates');
console.log('- Status update performance');
console.log('- API response times');
console.log('- Error tracking and recovery');