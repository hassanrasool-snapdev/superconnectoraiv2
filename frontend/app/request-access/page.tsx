'use client';

import { useState } from 'react';
import { submitAccessRequest } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import Link from 'next/link';

export default function RequestAccessPage() {
  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    organization: '',
    reason: ''
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    console.log('Submitting to API Base URL:', process.env.NEXT_PUBLIC_API_BASE_URL);
    try {
      await submitAccessRequest(formData);
      setSuccess(true);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (success) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
        <Card className="w-full max-w-lg">
          <CardHeader className="space-y-4 pb-8">
            <CardTitle className="text-4xl font-bold text-center text-green-600">Request Submitted!</CardTitle>
            <CardDescription className="text-lg text-center text-gray-600">
              Your access request has been submitted successfully.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center space-y-6">
            <p className="text-base text-gray-600">
              We&apos;ll review your request and get back to you via email within 1-2 business days.
            </p>
            <p className="text-base text-gray-500">
              If you already have an account, you can{' '}
              <Link href="/login" className="text-blue-600 hover:text-blue-800 underline font-medium">
                sign in here
              </Link>
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
      <Card className="w-full max-w-lg">
        <CardHeader className="space-y-4 pb-8">
          <CardTitle className="text-4xl font-bold text-center">Request Access</CardTitle>
          <CardDescription className="text-lg text-center text-gray-600">
            Fill out the form below to request access to Superconnect AI.
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="grid gap-6">
            <div className="grid gap-3">
              <Label htmlFor="full_name" className="text-base font-medium">Full Name *</Label>
              <Input
                id="full_name"
                name="full_name"
                type="text"
                placeholder="John Doe"
                required
                value={formData.full_name}
                onChange={handleInputChange}
                className="h-12 text-base"
              />
            </div>
            <div className="grid gap-3">
              <Label htmlFor="email" className="text-base font-medium">Email Address *</Label>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="john@example.com"
                required
                value={formData.email}
                onChange={handleInputChange}
                className="h-12 text-base"
              />
            </div>
            <div className="grid gap-3">
              <Label htmlFor="organization" className="text-base font-medium">Your LinkedIn Profile</Label>
              <Input
                id="organization"
                name="organization"
                type="text"
                placeholder="Enter your LinkedIn Profile URL"
                value={formData.organization}
                onChange={handleInputChange}
                className="h-12 text-base"
              />
            </div>
            <div className="grid gap-3">
              <Label htmlFor="reason" className="text-base font-medium">Reason for Access</Label>
              <Textarea
                id="reason"
                name="reason"
                placeholder="Share how you know Ha and the reason for your access request"
                rows={4}
                value={formData.reason}
                onChange={handleInputChange}
                className="text-base min-h-[100px]"
              />
            </div>
            {error && <p className="text-red-500 text-base font-medium">{error}</p>}
          </CardContent>
          <CardFooter className="flex flex-col pt-6">
            <Button type="submit" className="w-full h-12 text-base font-medium" disabled={isSubmitting}>
              {isSubmitting ? 'Submitting Request...' : 'Submit Request'}
            </Button>
            <p className="mt-6 text-base text-center text-gray-700">
              Already have an account?{' '}
              <Link href="/login" className="underline font-medium text-blue-600 hover:text-blue-800">
                Sign in
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}