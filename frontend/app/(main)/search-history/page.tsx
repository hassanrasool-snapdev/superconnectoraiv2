'use client';

import { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../../../src/context/AuthContext';
import { getSearchHistory, clearSearchHistory, deleteSearchHistoryEntry } from '../../../src/lib/api';
import { SearchHistory } from '../../../src/lib/types';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../src/components/ui/table";
import { Button } from '../../../src/components/ui/button';
import { useRouter } from 'next/navigation';

export default function SearchHistoryPage() {
  const [searchHistory, setSearchHistory] = useState<SearchHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { token } = useAuth();
  const router = useRouter();

  const fetchSearchHistory = useCallback(() => {
    if (token) {
      setLoading(true);
      getSearchHistory(token)
        .then(setSearchHistory)
        .catch(err => setError(err.message))
        .finally(() => setLoading(false));
    }
  }, [token]);

  useEffect(() => {
    fetchSearchHistory();
  }, [fetchSearchHistory]);

  const handleRunSearch = (search: SearchHistory) => {
    const params = new URLSearchParams();
    params.set('q', search.query);
    if (search.filters) {
      params.set('filters', JSON.stringify(search.filters));
    }
    router.push(`/dashboard?${params.toString()}`);
  };

  const handleDeleteEntry = async (searchId: string) => {
    if (token) {
      try {
        await deleteSearchHistoryEntry(searchId, token);
        fetchSearchHistory(); // Refresh the list
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete entry');
      }
    }
  };

  const handleClearHistory = async () => {
    if (token) {
      try {
        await clearSearchHistory(token);
        fetchSearchHistory(); // Refresh the list
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to clear history');
      }
    }
  };

  if (loading) return <p>Loading search history...</p>;
  if (error) return <p className="text-red-600">Error: {error}</p>;

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Search History</h1>
        <Button variant="destructive" onClick={handleClearHistory}>Clear History</Button>
      </div>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Query</TableHead>
              <TableHead>Searched At</TableHead>
              <TableHead>Results</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {searchHistory.map(search => (
              <TableRow key={search.id}>
                <TableCell>{search.query}</TableCell>
                <TableCell>{new Date(search.searched_at).toLocaleString()}</TableCell>
                <TableCell>{search.results_count}</TableCell>
                <TableCell>
                  <Button onClick={() => handleRunSearch(search)} className="mr-2">Run Again</Button>
                  <Button variant="destructive" onClick={() => handleDeleteEntry(search.id)}>Delete</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}