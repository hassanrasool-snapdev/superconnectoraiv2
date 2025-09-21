'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '../../../src/context/AuthContext';
import { getConnections, getConnectionsCount } from '../../../src/lib/api';
import { Connection } from '../../../src/lib/types';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../src/components/ui/table";
import { Button } from '../../../src/components/ui/button';
import { Label } from "../../../src/components/ui/label";
import WarmIntroModal from '@/components/shared/WarmIntroModal';

export default function ConnectionsPage() {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState<number | null>(null);
  // const [minRating, setMinRating] = useState<number>(6);
  const { token } = useAuth();
  const [selectedConnection, setSelectedConnection] = useState<Connection | null>(null);

  useEffect(() => {
    if (token) {
      setLoading(true);
      
      Promise.all([
        getConnections(token, page, 10),
        getConnectionsCount(token)
      ])
        .then(([connectionsData, countData]) => {
          setConnections(connectionsData.items);
          setTotalCount(countData.count);
        })
        .catch(err => setError(err.message))
        .finally(() => setLoading(false));
    }
  }, [token, page]); // minRating dependency commented out

  if (loading) return <p>Loading connections...</p>;
  if (error) return <p className="text-red-600">Error: {error}</p>;

  return (
    <>
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
          {/* Filter feature commented out */}
          {/* <div className="w-full max-w-xs">
            <Label htmlFor="min-rating">Minimum Rating: {minRating}</Label>
            <input
              id="min-rating"
              type="range"
              min={6}
              max={10}
              step={1}
              value={minRating}
              onChange={(e) => setMinRating(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>6</span>
              <span>10</span>
            </div>
          </div> */}
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
                <TableHead>Rating</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {connections.map(conn => (
                <TableRow key={conn.id}>
                  <TableCell className="font-medium">
                    <div>
                      <div className="flex items-center gap-2">
                        <span>{conn.first_name} {conn.last_name}</span>
                      </div>
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
                  <TableCell className="text-sm">{conn.rating || 'N/A'}</TableCell>
                  <TableCell>
                    <Button onClick={() => setSelectedConnection(conn)} size="sm">
                      Request Intro
                    </Button>
                  </TableCell>
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
            disabled={connections.length < 10}
          >
            Next
          </Button>
        </div>
      </div>
      {selectedConnection && (
        <WarmIntroModal
          isOpen={!!selectedConnection}
          onClose={() => setSelectedConnection(null)}
          targetFirstName={selectedConnection.first_name}
          targetLastName={selectedConnection.last_name}
          theirCompany={selectedConnection.company_name || ''}
          linkedinUrl={selectedConnection.linkedin_url || undefined}
          profilePicture={selectedConnection.profile_picture || undefined}
        />
      )}
    </>
  );
}