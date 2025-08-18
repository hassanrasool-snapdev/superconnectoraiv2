'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { getGeneratedEmails } from '@/lib/api';
import { GeneratedEmail } from '@/lib/types';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";

export default function GeneratedEmailsPage() {
  const [emails, setEmails] = useState<GeneratedEmail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { token } = useAuth();

  useEffect(() => {
    if (token) {
      setLoading(true);
      getGeneratedEmails(token)
        .then(setEmails)
        .catch((err: Error) => setError(err.message))
        .finally(() => setLoading(false));
    }
  }, [token]);

  if (loading) return <p>Loading generated emails...</p>;
  if (error) return <p className="text-red-600">Error: {error}</p>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Generated Emails</h1>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Connection</TableHead>
            <TableHead>Reason</TableHead>
            <TableHead>Generated Content</TableHead>
            <TableHead>Created At</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {emails.map(email => (
            <TableRow key={email.id}>
              <TableCell>{email.connection_id}</TableCell>
              <TableCell>{email.reason_for_connecting}</TableCell>
              <TableCell>{email.generated_content}</TableCell>
              <TableCell>{new Date(email.created_at).toLocaleString()}</TableCell>
              <TableCell>
                <Button variant="outline" size="sm" className="mr-2">Edit</Button>
                <Button variant="destructive" size="sm">Delete</Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}