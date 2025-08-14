'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '../../../src/context/AuthContext';
import { getSavedSearches, deleteSavedSearch } from '../../../src/lib/api';
import { SavedSearch } from '../../../src/lib/types';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../src/components/ui/table";
import { Button } from '../../../src/components/ui/button';
import { useRouter } from 'next/navigation';

export default function SavedSearchesPage() {
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { token } = useAuth();
  const router = useRouter();

  const fetchSavedSearches = () => {
    if (token) {
      setLoading(true);
      getSavedSearches(token)
        .then(setSavedSearches)
        .catch(err => setError(err.message))
        .finally(() => setLoading(false));
    }
  };

  useEffect(() => {
    fetchSavedSearches();
  }, [token]);

  const handleRunSearch = (search: SavedSearch) => {
    const params = new URLSearchParams();
    params.set('q', search.query);
    if (search.filters) {
      params.set('filters', JSON.stringify(search.filters));
    }
    router.push(`/dashboard?${params.toString()}`);
  };

  const handleDeleteSearch = async (searchId: string) => {
    if (token) {
      try {
        await deleteSavedSearch(searchId, token);
        fetchSavedSearches(); // Refresh the list
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete search');
      }
    }
  };

  if (loading) return <p>Loading saved searches...</p>;
  if (error) return <p className="text-red-600">Error: {error}</p>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Saved Searches</h1>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Query</TableHead>
              <TableHead>Created At</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {savedSearches.map(search => (
              <TableRow key={search.id}>
                <TableCell className="font-medium">{search.name}</TableCell>
                <TableCell>{search.query}</TableCell>
                <TableCell>{new Date(search.created_at).toLocaleString()}</TableCell>
                <TableCell>
                  <Button onClick={() => handleRunSearch(search)} className="mr-2">Run</Button>
                  <Button variant="destructive" onClick={() => handleDeleteSearch(search.id)}>Delete</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}