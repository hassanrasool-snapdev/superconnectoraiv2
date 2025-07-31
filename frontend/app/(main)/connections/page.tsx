'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '../../../src/context/AuthContext';
import { getConnections, getConnectionsCount } from '../../../src/lib/api';
import { Connection } from '../../../src/lib/types';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../src/components/ui/table";
import { Button } from '../../../src/components/ui/button';

export default function ConnectionsPage() {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState<number | null>(null);
  const { token } = useAuth();

  useEffect(() => {
    if (token) {
      setLoading(true);
      
      // Fetch both connections and total count
      Promise.all([
        getConnections(token, page),
        getConnectionsCount(token)
      ])
        .then(([connectionsData, countData]) => {
          setConnections(connectionsData);
          setTotalCount(countData.count);
        })
        .catch(err => setError(err.message))
        .finally(() => setLoading(false));
    }
  }, [token, page]);

  if (loading) return <p>Loading connections...</p>;
  if (error) return <p className="text-red-600">Error: {error}</p>;

  return (
    <div className="container mx-auto p-4">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">My Connections</h1>
          {totalCount !== null && (
            <p className="text-gray-600 mt-1">
              Total connections available for search: <span className="font-semibold text-blue-600">{totalCount.toLocaleString()}</span>
            </p>
          )}
        </div>
      </div>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Headline</TableHead>
              <TableHead>LinkedIn</TableHead>
              <TableHead>Company</TableHead>
              <TableHead>Location</TableHead>
              <TableHead>Followers</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {connections.map(conn => (
              <TableRow key={conn.id}>
                <TableCell className="font-medium">
                  <div>
                    <div>{conn.first_name} {conn.last_name}</div>
                    {conn.email_address && (
                      <div className="text-xs text-gray-500">{conn.email_address}</div>
                    )}
                  </div>
                </TableCell>
                <TableCell className="text-sm max-w-xs">
                  <div className="truncate" title={conn.headline || 'N/A'}>
                    {conn.headline || 'N/A'}
                  </div>
                </TableCell>
                <TableCell>
                  {conn.linkedin_url ? (
                    <a
                      href={conn.linkedin_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      LinkedIn
                    </a>
                  ) : (
                    <span className="text-gray-400 text-sm">N/A</span>
                  )}
                </TableCell>
                <TableCell>
                  <div>
                    {conn.company && <div className="font-medium">{conn.company}</div>}
                    {conn.company_name && conn.company_name !== conn.company && (
                      <div className="text-xs text-gray-600">{conn.company_name}</div>
                    )}
                    {conn.company_website && (
                      <a
                        href={conn.company_website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-blue-600 hover:text-blue-800"
                      >
                        Website
                      </a>
                    )}
                  </div>
                </TableCell>
                <TableCell className="text-sm">
                  {[conn.city, conn.state, conn.country].filter(Boolean).join(', ') || 'N/A'}
                </TableCell>
                <TableCell className="text-sm">{conn.followers || 'N/A'}</TableCell>
                <TableCell className="text-sm">{conn.followers || 'N/A'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-end space-x-2 py-4">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page === 1}
        >
          Previous
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setPage(p => p + 1)}
          disabled={connections.length < 10} // Simple pagination check
        >
          Next
        </Button>
      </div>
    </div>
  );
}