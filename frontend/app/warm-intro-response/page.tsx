'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../src/components/ui/card';
import { Button } from '../../src/components/ui/button';
import { CheckCircle, XCircle, Heart, Loader2 } from 'lucide-react';

export default function WarmIntroResponsePage() {
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const [connected, setConnected] = useState<boolean | null>(null);

  useEffect(() => {
    const handleResponse = async () => {
      const requestId = searchParams.get('request_id');
      const response = searchParams.get('response');

      if (!requestId || !response) {
        setStatus('error');
        setMessage('Invalid response link. Please check the link from your email.');
        return;
      }

      const isConnected = response === 'yes';
      setConnected(isConnected);

      try {
        const apiResponse = await fetch(`/api/v1/public/warm-intro-requests/${requestId}/respond`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            connected: isConnected
          }),
        });

        if (apiResponse.ok) {
          const data = await apiResponse.json();
          setStatus('success');
          setMessage(data.message || 'Thank you for your response!');
        } else {
          const errorData = await apiResponse.json();
          setStatus('error');
          setMessage(errorData.detail || 'Failed to record your response. Please try again.');
        }
      } catch (error) {
        setStatus('error');
        setMessage('An error occurred while processing your response. Please try again.');
      }
    };

    handleResponse();
  }, [searchParams]);

  const handleDonateClick = () => {
    // Redirect to donation page
    window.location.href = '/donate';
  };

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardContent className="flex flex-col items-center justify-center p-8">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600 mb-4" />
            <p className="text-gray-600">Processing your response...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            {status === 'success' ? (
              <CheckCircle className="h-16 w-16 text-green-500" />
            ) : (
              <XCircle className="h-16 w-16 text-red-500" />
            )}
          </div>
          <CardTitle className="text-2xl font-bold">
            {status === 'success' ? 'Response Recorded!' : 'Oops!'}
          </CardTitle>
          <CardDescription className="text-lg">
            {message}
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          {status === 'success' && (
            <>
              {connected && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                    <p className="text-green-800 font-medium">
                      Excellent! We're thrilled to hear your warm introduction was successful. Your feedback helps us improve our service and shows the value of our networking platform.
                    </p>
                  </div>
                </div>
              )}

              {!connected && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <XCircle className="h-5 w-5 text-blue-500 mr-2" />
                    <p className="text-blue-800 font-medium">
                      No worries! We understand that connections don't always happen immediately. Sometimes timing isn't right, or it takes multiple touchpoints. Feel free to make another warm intro request if you'd like to try connecting with someone else.
                    </p>
                  </div>
                </div>
              )}

              <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-6">
                <div className="text-center">
                  <Heart className="h-8 w-8 text-pink-500 mx-auto mb-3" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Help Keep Superconnector AI Alive!
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Your response helps us track the success of our warm introductions and improve our service. If you found this networking platform valuable, please consider supporting us with a donation to keep the connections flowing.
                  </p>
                  <Button 
                    onClick={handleDonateClick}
                    className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-medium px-6 py-2"
                  >
                    Make a Donation
                  </Button>
                </div>
              </div>

              <div className="text-center text-sm text-gray-500">
                <p>Thank you for taking the time to respond to our follow-up!</p>
                <p className="mt-1">
                  Your feedback helps us measure our impact and improve our warm introduction service.
                </p>
                <p className="mt-2">
                  Questions? Contact us at{' '}
                  <a href="mailto:support@superconnector.ai" className="text-blue-600 hover:underline">
                    support@superconnector.ai
                  </a>
                </p>
              </div>
            </>
          )}

          {status === 'error' && (
            <div className="text-center">
              <p className="text-gray-600 mb-4">
                If you continue to experience issues, please contact our support team.
              </p>
              <Button 
                onClick={() => window.location.href = 'mailto:support@superconnector.ai'}
                variant="outline"
              >
                Contact Support
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}