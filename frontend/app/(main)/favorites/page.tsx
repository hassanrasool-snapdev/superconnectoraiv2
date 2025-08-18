'use client';

import { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../../../src/context/AuthContext';
import { getFavoriteConnections, removeFavoriteConnection } from '../../../src/lib/api';
import { FavoriteConnection } from '../../../src/lib/types';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../src/components/ui/table";
import { Button } from '../../../src/components/ui/button';

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState<FavoriteConnection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { token } = useAuth();

  const fetchFavorites = useCallback(() => {
    if (token) {
      setLoading(true);
      getFavoriteConnections(token)
        .then(setFavorites)
        .catch(err => setError(err.message))
        .finally(() => setLoading(false));
    }
  }, [token]);

  useEffect(() => {
    fetchFavorites();
  }, [fetchFavorites]);

  const handleRemoveFavorite = async (connectionId: string) => {
    if (token) {
      try {
        await removeFavoriteConnection(connectionId);
        fetchFavorites(); // Refresh the list
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to remove favorite');
      }
    }
  };

  if (loading) return <p>Loading favorites...</p>;
  if (error) return <p className="text-red-600">Error: {error}</p>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Favorite Connections</h1>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Headline</TableHead>
              <TableHead>Favorited At</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {favorites.map(fav => (
              <TableRow key={fav.favorite_id}>
                <TableCell className="font-medium">{fav.connection.first_name} {fav.connection.last_name}</TableCell>
                <TableCell>{fav.connection.headline}</TableCell>
                <TableCell>{new Date(fav.favorited_at).toLocaleString()}</TableCell>
                <TableCell>
                  <Button variant="destructive" onClick={() => handleRemoveFavorite(fav.connection.id)}>Remove</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}