'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { telemetry, TelemetryEvent } from '@/lib/telemetry';
import { BarChart3, TrendingUp, Users, Clock, RefreshCw, Download } from 'lucide-react';

interface AnalyticsMetrics {
  totalEvents: number;
  uniqueSessions: number;
  modalOpens: number;
  requestsCreated: number;
  statusUpdates: number;
  averageFormCompletion: number;
  averageTimeSpent: number;
  topEvents: { event: string; count: number }[];
  recentEvents: TelemetryEvent[];
}

export default function AnalyticsDashboard() {
  const [metrics, setMetrics] = useState<AnalyticsMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [events, setEvents] = useState<TelemetryEvent[]>([]);

  const loadAnalytics = () => {
    setLoading(true);
    
    // Get events from localStorage
    const storedEvents = localStorage.getItem('telemetry_events');
    const allEvents: TelemetryEvent[] = storedEvents ? JSON.parse(storedEvents) : [];
    setEvents(allEvents);
    
    // Calculate metrics
    const uniqueSessions = new Set(allEvents.map(e => e.session_id)).size;
    const modalOpens = allEvents.filter(e => e.event_name === 'modal_opened').length;
    const requestsCreated = allEvents.filter(e => e.event_name === 'warm_intro_request_created').length;
    const statusUpdates = allEvents.filter(e => e.event_name === 'status_update_completed').length;
    
    // Calculate average form completion
    const modalCloseEvents = allEvents.filter(e => e.event_name === 'modal_closed');
    const avgFormCompletion = modalCloseEvents.length > 0 
      ? modalCloseEvents.reduce((sum, e) => sum + (typeof e.properties.form_completion_percentage === 'number' ? e.properties.form_completion_percentage : 0), 0) / modalCloseEvents.length
      : 0;
    
    // Calculate average time spent
    const avgTimeSpent = modalCloseEvents.length > 0
      ? modalCloseEvents.reduce((sum, e) => sum + (typeof e.properties.time_spent_seconds === 'number' ? e.properties.time_spent_seconds : 0), 0) / modalCloseEvents.length
      : 0;
    
    // Get top events
    const eventCounts: { [key: string]: number } = {};
    allEvents.forEach(e => {
      eventCounts[e.event_name] = (eventCounts[e.event_name] || 0) + 1;
    });
    
    const topEvents = Object.entries(eventCounts)
      .map(([event, count]) => ({ event, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);
    
    setMetrics({
      totalEvents: allEvents.length,
      uniqueSessions,
      modalOpens,
      requestsCreated,
      statusUpdates,
      averageFormCompletion: Math.round(avgFormCompletion),
      averageTimeSpent: Math.round(avgTimeSpent),
      topEvents,
      recentEvents: allEvents.slice(-20).reverse(),
    });
    
    setLoading(false);
  };

  useEffect(() => {
    loadAnalytics();
  }, []);

  const exportData = () => {
    const dataStr = JSON.stringify(events, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `warm-intro-analytics-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const clearData = () => {
    if (confirm('Are you sure you want to clear all analytics data? This cannot be undone.')) {
      localStorage.removeItem('telemetry_events');
      loadAnalytics();
    }
  };

  const formatEventName = (eventName: string) => {
    return eventName
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="w-6 h-6 animate-spin mr-2" />
          <span>Loading analytics...</span>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="container mx-auto p-4">
        <Card>
          <CardContent className="pt-6">
            <p className="text-gray-600">No analytics data available.</p>
            <Button onClick={loadAnalytics} className="mt-4">
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Warm Intro Analytics</h1>
          <p className="text-sm text-gray-600 mt-1">
            Real-time insights into user behavior and system performance
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={loadAnalytics}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" size="sm" onClick={exportData}>
            <Download className="w-4 h-4 mr-2" />
            Export Data
          </Button>
          <Button variant="destructive" size="sm" onClick={clearData}>
            Clear Data
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center">
              <BarChart3 className="w-4 h-4 mr-2" />
              Total Events
            </CardDescription>
            <CardTitle className="text-2xl">{metrics.totalEvents}</CardTitle>
          </CardHeader>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center">
              <Users className="w-4 h-4 mr-2" />
              Unique Sessions
            </CardDescription>
            <CardTitle className="text-2xl">{metrics.uniqueSessions}</CardTitle>
          </CardHeader>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center">
              <TrendingUp className="w-4 h-4 mr-2" />
              Requests Created
            </CardDescription>
            <CardTitle className="text-2xl text-green-600">{metrics.requestsCreated}</CardTitle>
          </CardHeader>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center">
              <Clock className="w-4 h-4 mr-2" />
              Avg Time Spent
            </CardDescription>
            <CardTitle className="text-2xl">{metrics.averageTimeSpent}s</CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Additional Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Modal Interactions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Modal Opens:</span>
              <Badge variant="secondary">{metrics.modalOpens}</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Avg Form Completion:</span>
              <Badge variant="secondary">{metrics.averageFormCompletion}%</Badge>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">System Activity</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Status Updates:</span>
              <Badge variant="secondary">{metrics.statusUpdates}</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Success Rate:</span>
              <Badge variant="secondary">
                {metrics.requestsCreated > 0 ? Math.round((metrics.requestsCreated / metrics.modalOpens) * 100) : 0}%
              </Badge>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Session Info</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Current Session:</span>
              <Badge variant="outline" className="text-xs">
                {telemetry.getAnalyticsSummary().sessionId.split('_')[2]}
              </Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Events/Session:</span>
              <Badge variant="secondary">
                {Math.round(metrics.totalEvents / Math.max(metrics.uniqueSessions, 1))}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Events */}
      <Card>
        <CardHeader>
          <CardTitle>Top Events</CardTitle>
          <CardDescription>Most frequently tracked events</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {metrics.topEvents.map((item, index) => (
              <div key={item.event} className="flex items-center justify-between p-2 rounded-lg bg-gray-50">
                <div className="flex items-center space-x-3">
                  <Badge variant="outline">{index + 1}</Badge>
                  <span className="font-medium">{formatEventName(item.event)}</span>
                </div>
                <Badge>{item.count}</Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Events */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Events</CardTitle>
          <CardDescription>Latest 20 tracked events</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Event</TableHead>
                  <TableHead>Timestamp</TableHead>
                  <TableHead>Session</TableHead>
                  <TableHead>Properties</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {metrics.recentEvents.map((event, index) => (
                  <TableRow key={index}>
                    <TableCell className="font-medium">
                      {formatEventName(event.event_name)}
                    </TableCell>
                    <TableCell className="text-sm text-gray-600">
                      {formatTimestamp(event.timestamp)}
                    </TableCell>
                    <TableCell className="text-xs text-gray-500">
                      {event.session_id?.split('_')[2] || 'N/A'}
                    </TableCell>
                    <TableCell className="text-xs">
                      <details className="cursor-pointer">
                        <summary className="text-blue-600 hover:text-blue-800">
                          View ({Object.keys(event.properties).length} props)
                        </summary>
                        <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto max-w-xs">
                          {JSON.stringify(event.properties, null, 2)}
                        </pre>
                      </details>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}