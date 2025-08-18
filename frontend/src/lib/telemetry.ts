/**
 * Centralized telemetry system for tracking user interactions and system events
 * across the warm intro requests feature
 */

export interface TelemetryEvent {
  event_name: string;
  timestamp: string;
  user_id?: string;
  session_id?: string;
  page_url?: string;
  user_agent?: string;
  properties: Record<string, unknown>;
}

export interface WarmIntroAnalytics {
  // Modal events
  modal_opened: {
    target_name: string;
    target_company: string;
    has_linkedin_url: boolean;
    has_profile_picture: boolean;
  };
  
  modal_closed: {
    target_name: string;
    form_completion_percentage: number;
    time_spent_seconds: number;
    close_method: 'button' | 'escape' | 'outside_click' | 'unsaved_warning';
  };
  
  // Form interaction events
  form_field_focused: {
    field_name: string;
    field_type: string;
    form_completion_percentage: number;
  };
  
  form_field_completed: {
    field_name: string;
    field_length: number;
    validation_passed: boolean;
  };
  
  quick_chip_used: {
    chip_label: string;
    chip_text: string;
    existing_text_length: number;
  };
  
  example_template_viewed: {
    target_name: string;
  };
  
  example_template_applied: {
    target_name: string;
    overwrite_existing: boolean;
    existing_reason_length: number;
    existing_about_length: number;
  };
  
  autosave_triggered: {
    fields_saved: string[];
    total_characters: number;
  };
  
  autosave_restored: {
    fields_restored: string[];
    age_hours: number;
  };
  
  // Submission events
  form_validation_failed: {
    invalid_fields: string[];
    form_completion_percentage: number;
    time_spent_seconds: number;
  };
  
  email_generation_started: {
    requester_name_length: number;
    reason_length: number;
    about_length: number;
    include_email: boolean;
    target_name: string;
  };
  
  email_client_opened: {
    method: 'link_click' | 'location_href' | 'window_open';
    email_length: number;
  };
  
  email_fallback_used: {
    fallback_method: 'clipboard' | 'manual_alert';
    email_length: number;
  };
  
  warm_intro_request_created: {
    requester_name: string;
    connection_name: string;
    creation_method: 'success' | 'fallback';
  };
  
  warm_intro_request_creation_failed: {
    error_type: string;
    requester_name: string;
    connection_name: string;
  };
  
  // Page events
  requests_page_loaded: {
    total_requests: number;
    pending_count: number;
    connected_count: number;
    declined_count: number;
    current_page: number;
    status_filter: string;
  };
  
  requests_page_filtered: {
    previous_filter: string;
    new_filter: string;
    results_count: number;
  };
  
  requests_page_paginated: {
    previous_page: number;
    new_page: number;
    total_pages: number;
    status_filter: string;
  };
  
  requests_page_refreshed: {
    current_page: number;
    status_filter: string;
    manual_refresh: boolean;
  };
  
  // Status update events
  status_update_initiated: {
    request_id: string;
    previous_status: string;
    new_status: string;
    requester_name: string;
    connection_name: string;
  };
  
  status_update_completed: {
    request_id: string;
    previous_status: string;
    new_status: string;
    update_duration_ms: number;
  };
  
  status_update_failed: {
    request_id: string;
    attempted_status: string;
    error_type: string;
  };
  
  // Performance events
  api_request_performance: {
    endpoint: string;
    method: string;
    duration_ms: number;
    status_code: number;
    success: boolean;
  };
  
  page_load_performance: {
    page_name: string;
    load_time_ms: number;
    initial_data_load_ms: number;
  };
}

class TelemetryService {
  private sessionId: string;
  private userId?: string;
  private pageLoadTime: number;
  
  constructor() {
    this.sessionId = this.generateSessionId();
    this.pageLoadTime = Date.now();
    
    // Initialize session tracking
    if (typeof window !== 'undefined') {
      this.initializeSession();
    }
  }
  
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  private initializeSession() {
    // Try to get existing session from sessionStorage
    const existingSession = sessionStorage.getItem('telemetry_session_id');
    if (existingSession) {
      this.sessionId = existingSession;
    } else {
      sessionStorage.setItem('telemetry_session_id', this.sessionId);
    }
  }
  
  setUserId(userId: string) {
    this.userId = userId;
  }
  
  private createBaseEvent(): Omit<TelemetryEvent, 'event_name' | 'properties'> {
    return {
      timestamp: new Date().toISOString(),
      user_id: this.userId,
      session_id: this.sessionId,
      page_url: typeof window !== 'undefined' ? window.location.href : undefined,
      user_agent: typeof navigator !== 'undefined' ? navigator.userAgent : undefined,
    };
  }
  
  track<K extends keyof WarmIntroAnalytics>(
    eventName: K,
    properties: WarmIntroAnalytics[K]
  ): void {
    const event: TelemetryEvent = {
      ...this.createBaseEvent(),
      event_name: eventName as string,
      properties: properties as Record<string, unknown>,
    };
    
    this.sendEvent(event);
  }
  
  trackCustom(eventName: string, properties: Record<string, unknown>): void {
    const event: TelemetryEvent = {
      ...this.createBaseEvent(),
      event_name: eventName,
      properties,
    };
    
    this.sendEvent(event);
  }
  
  private sendEvent(event: TelemetryEvent): void {
    // For now, log to console (in production, this would send to analytics service)
    console.log(`[Telemetry] ${event.event_name}`, {
      timestamp: event.timestamp,
      session: event.session_id,
      user: event.user_id,
      properties: event.properties,
    });
    
    // Store events locally for debugging/development
    if (typeof window !== 'undefined') {
      const events = JSON.parse(localStorage.getItem('telemetry_events') || '[]');
      events.push(event);
      
      // Keep only last 100 events to prevent storage bloat
      if (events.length > 100) {
        events.splice(0, events.length - 100);
      }
      
      localStorage.setItem('telemetry_events', JSON.stringify(events));
    }
    
    // In production, you would send to your analytics service:
    // this.sendToAnalyticsService(event);
  }
  
  // Helper method to calculate form completion percentage
  calculateFormCompletion(fields: Record<string, string | boolean>): number {
    const totalFields = Object.keys(fields).length;
    const completedFields = Object.values(fields).filter(value => {
      if (typeof value === 'boolean') return value;
      if (typeof value === 'string') return value.trim().length > 0;
      return false;
    }).length;
    
    return Math.round((completedFields / totalFields) * 100);
  }
  
  // Helper method to calculate time spent
  calculateTimeSpent(startTime: number): number {
    return Math.round((Date.now() - startTime) / 1000);
  }
  
  // Method to get analytics summary (useful for debugging)
  getAnalyticsSummary(): {
    sessionId: string;
    userId?: string;
    eventsCount: number;
    recentEvents: TelemetryEvent[];
  } {
    const events = typeof window !== 'undefined' 
      ? JSON.parse(localStorage.getItem('telemetry_events') || '[]')
      : [];
    
    return {
      sessionId: this.sessionId,
      userId: this.userId,
      eventsCount: events.length,
      recentEvents: events.slice(-10), // Last 10 events
    };
  }
}

// Export singleton instance
export const telemetry = new TelemetryService();

// Export helper functions
export const logTelemetry = telemetry.track.bind(telemetry);
export const logCustomTelemetry = telemetry.trackCustom.bind(telemetry);