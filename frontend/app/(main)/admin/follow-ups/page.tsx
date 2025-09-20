'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { RefreshCw, Mail, X, Clock, User, Calendar } from "lucide-react";
import { cn } from "@/lib/utils";

interface FollowUpCandidate {
  id: string;
  requester_name: string;
  connection_name: string;
  user_email: string;
  created_at: string;
  days_old: number;
  status: string;
}

interface EmailPreview {
  to_email: string;
  subject: string;
  html_content: string;
  request_id: string;
  requester_name: string;
  connection_name: string;
}

export default function AdminFollowUpsPage() {
  const [candidates, setCandidates] = useState<FollowUpCandidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingIds, setProcessingIds] = useState<Set<string>>(new Set());
  
  const { token } = useAuth();
  const { toast } = useToast();

  const fetchCandidates = async () => {
    if (!token) return;
    
    setLoading(true);
    try {
      const response = await fetch('/api/v1/follow-up-emails/admin/candidates', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setCandidates(data);
      } else {
        throw new Error('Failed to fetch candidates');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch follow-up candidates",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };


  const sendFollowUp = async (requestId: string) => {
    if (!token) return;
    
    setProcessingIds(prev => new Set(prev).add(requestId));
    
    try {
      // Send the follow-up email request - this will return email template data like access requests
      const response = await fetch(`/api/v1/follow-up-emails/admin/send/${requestId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to send follow-up email');
      }

      const result = await response.json();
      
      // Open email client with pre-drafted follow-up email (same approach as access requests)
      if (result.email_template) {
        const { to, subject, body } = result.email_template;
        const mailtoLink = `mailto:${to}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
        window.open(mailtoLink, '_blank');
        
        toast({
          title: "Follow-up Email Ready",
          description: "Your email client should open with a pre-drafted follow-up email.",
        });
      } else {
        toast({
          title: "Follow-up Processed",
          description: "Follow-up email processed successfully, but email template was not generated.",
        });
      }
      
      // Remove from candidates list
      setCandidates(prev => prev.filter(c => c.id !== requestId));
      
    } catch (error) {
      console.error('Error in sendFollowUp:', error);
      toast({
        title: "Error",
        description: "Failed to process follow-up email",
        variant: "destructive",
      });
    } finally {
      setProcessingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(requestId);
        return newSet;
      });
    }
  };

  const skipFollowUp = async (requestId: string) => {
    if (!token) return;
    
    setProcessingIds(prev => new Set(prev).add(requestId));
    
    try {
      const response = await fetch(`/api/v1/follow-up-emails/admin/skip/${requestId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Follow-up email skipped",
        });
        
        // Remove from candidates list
        setCandidates(prev => prev.filter(c => c.id !== requestId));
      } else {
        throw new Error('Failed to skip email');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to skip follow-up email",
        variant: "destructive",
      });
    } finally {
      setProcessingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(requestId);
        return newSet;
      });
    }
  };

  useEffect(() => {
    fetchCandidates();
  }, [token]);

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="w-6 h-6 animate-spin mr-2" />
          <span>Loading follow-up candidates...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Follow-Up Email Management</h1>
          <p className="text-sm text-gray-600 mt-1">
            Manage 14-day follow-up emails for warm introduction requests
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={fetchCandidates}
          disabled={loading}
        >
          <RefreshCw className={cn("w-4 h-4 mr-2", loading && "animate-spin")} />
          Refresh
        </Button>
      </div>

      {/* Stats Card */}
      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Requests Needing Follow-up</CardDescription>
          <CardTitle className="text-3xl text-orange-600">
            {candidates.length}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600">
            Warm intro requests that are 14+ days old and haven't received follow-up emails
          </p>
        </CardContent>
      </Card>

      {/* Candidates List */}
      {candidates.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-8">
              <Mail className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Follow-ups Needed</h3>
              <p className="text-gray-600">
                All warm intro requests are either too recent or have already received follow-up emails.
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {candidates.map((candidate) => (
            <Card key={candidate.id} className="border-l-4 border-l-orange-500">
              <CardContent className="pt-6">
                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-gray-500" />
                      <span className="font-medium">{candidate.requester_name}</span>
                      <span className="text-gray-500">→</span>
                      <span className="font-medium">{candidate.connection_name}</span>
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <Mail className="w-3 h-3" />
                        <span>{candidate.user_email}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        <span>Created: {new Date(candidate.created_at).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        <Badge variant="outline" className="text-orange-600 border-orange-200">
                          {candidate.days_old} days old
                        </Badge>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Button
                      size="sm"
                      onClick={() => sendFollowUp(candidate.id)}
                      disabled={processingIds.has(candidate.id)}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      {processingIds.has(candidate.id) ? (
                        <RefreshCw className="w-4 h-4 mr-1 animate-spin" />
                      ) : (
                        <Mail className="w-4 h-4 mr-1" />
                      )}
                      Send Email
                    </Button>
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => skipFollowUp(candidate.id)}
                      disabled={processingIds.has(candidate.id)}
                      className="text-red-600 border-red-200 hover:bg-red-50"
                    >
                      <X className="w-4 h-4 mr-1" />
                      Skip
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

    </div>
  );
}