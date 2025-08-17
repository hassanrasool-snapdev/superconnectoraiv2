'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '../../../src/context/AuthContext';
import { getTippingHistory } from '../../../src/lib/api';
import { Tip } from '../../../src/lib/types';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../src/components/ui/table";

export default function TippingHistoryPage() {
  const [contributionHistory, setContributionHistory] = useState<Tip[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { token } = useAuth();

  useEffect(() => {
    if (token) {
      setLoading(true);
      getTippingHistory(token)
        .then(setContributionHistory)
        .catch(err => setError(err.message))
        .finally(() => setLoading(false));
    }
  }, [token]);

  if (loading) return <p>Loading contribution history...</p>;
  if (error) return <p className="text-red-600">Error: {error}</p>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Contribution History</h1>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Connection ID</TableHead>
              <TableHead>Amount</TableHead>
              <TableHead>Message</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Transaction ID</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {contributionHistory.map(contribution => (
              <TableRow key={contribution.id}>
                <TableCell>{contribution.connection_id}</TableCell>
                <TableCell>${contribution.amount.toFixed(2)}</TableCell>
                <TableCell>{contribution.message}</TableCell>
                <TableCell>{new Date(contribution.created_at).toLocaleString()}</TableCell>
                <TableCell>{contribution.transaction_id}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}