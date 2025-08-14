'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { searchConnectionsWithProgress, getConnectionsCount, createSavedSearch, addFavoriteConnection } from '@/lib/api';
import { SearchResult, Connection } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Badge } from '../../../src/components/ui/badge';
import { User, Linkedin, Loader2, Star } from 'lucide-react';
import Image from 'next/image';
import { EmailGenerationModal } from '@/components/shared/EmailGenerationModal';
import { TippingModal } from '@/components/shared/TippingModal';

export default function DashboardPage() {
  const { token } = useAuth();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isTippingModalOpen, setIsTippingModalOpen] = useState(false);
  const [selectedConnection, setSelectedConnection] = useState<Connection | null>(null);
  const [searchProgress, setSearchProgress] = useState(0);
  const [connectionsCount, setConnectionsCount] = useState<number | null>(null);
  const [favoritedStatus, setFavoritedStatus] = useState<{[key: string]: boolean}>({});
 
   useEffect(() => {
     if (token) {
       getConnectionsCount(token)
         .then(data => setConnectionsCount(data.count))
         .catch(err => console.error("Failed to fetch connections count:", err));
     }
   }, [token]);
 
   const handleSearch = async (e: React.FormEvent) => {
     e.preventDefault();
    if (!query.trim() || !token) {
      setError('Authentication token is not available. Please log in again.');
      return;
    }

    setLoading(true);
    setError(null);
    setHasSearched(true);
    setSearchProgress(0);
    setResults([]);

    try {
      const searchResults = await searchConnectionsWithProgress(
        { query: query.trim() },
        token,
        (progress) => {
          setSearchProgress(progress);
        }
      );
      setResults(searchResults);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      setResults([]);
    } finally {
      setLoading(false);
      setSearchProgress(100);
    }
  };

  const handleEmailConnection = (email: string | null | undefined, name: string) => {
    const subject = encodeURIComponent(`Connection from LinkedIn`);
    const body = encodeURIComponent(`Hi ${name},\n\nI hope this message finds you well. I wanted to reach out to connect and explore potential opportunities for collaboration.\n\nBest regards`);
    
    // Use email if available, otherwise leave To: field blank
    const toField = email ? email : '';
    window.open(`mailto:${toField}?subject=${subject}&body=${body}`, '_blank');
  };

  const openEmailModal = (connection: Connection) => {
    setSelectedConnection(connection);
    setIsModalOpen(true);
  };

  const openTippingModal = (connection: Connection) => {
    setSelectedConnection(connection);
    setIsTippingModalOpen(true);
  };
 
   const handleSaveSearch = async () => {
    if (!query.trim() || !token) {
      setError('Cannot save an empty search.');
      return;
    }
    const searchName = prompt('Enter a name for this search:');
    if (searchName && token) {
      try {
        await createSavedSearch(searchName, query.trim(), undefined, token);
        alert('Search saved successfully!');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to save search');
      }
    }
  };

  const handleFavoriteConnection = async (connectionId: string) => {
    if (token) {
      try {
        await addFavoriteConnection(connectionId, token);
        setFavoritedStatus(prev => ({ ...prev, [connectionId]: true }));
        alert('Added to favorites!');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to add to favorites');
      }
    }
  };
 
   return (
     <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-6">SuperConnector AI</h1>
          
          {/* Search Section */}
          <div className="bg-white rounded-lg shadow-sm border p-8 mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-6 text-left">Search Connections</h2>
            
            <form onSubmit={handleSearch} className="flex gap-3">
              <Input
                type="text"
                placeholder="please find me a VC who invests in seed stage consumer startups."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="flex-1 h-12 px-4 text-gray-700"
                disabled={loading}
              />
              <Button 
                type="submit" 
                disabled={loading || !query.trim()}
                className="h-12 px-8 bg-blue-600 hover:bg-blue-700"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Searching...
                  </>
                ) : (
                  'Search'
                )}
              </Button>
            </form>
          </div>
          {loading && (
            <div className="mt-4 text-center">
              <p className="text-lg text-gray-800 mb-2">
                Got it! I'm searching Ha's {connectionsCount?.toLocaleString() ?? ''} 1st degree connections (from LinkedIn).
              </p>
              <p className="text-sm text-gray-500 mb-4">
                This search may take a few minutes so hang tight
              </p>
              <Progress value={searchProgress} className="w-full" />
              <p className="text-sm text-center text-gray-500 mt-2">{searchProgress}% complete</p>
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Search Results */}
        {hasSearched && !loading && (
          <div className="space-y-6">
            {results.length > 0 && (
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-800">
                  Found {results.length} relevant profiles
                </h2>
                <Button onClick={handleSaveSearch} variant="outline">Save Search</Button>
              </div>
            )}
            {results.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">No connections match your search criteria.</p>
                <p className="text-gray-400 mt-2">Try adjusting your search terms or uploading more connection data.</p>
              </div>
            ) : (
              results.map((result) => (
                <div key={result.connection.id} className="bg-white rounded-lg shadow-sm border p-6">
                  {/* Header with avatar, name, and score */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-start space-x-4">
                      {/* Avatar */}
                      <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center overflow-hidden">
                        {result.connection.profile_picture ? (
                          <Image
                            src={result.connection.profile_picture}
                            alt={`${result.connection.first_name} ${result.connection.last_name}`}
                            className="w-full h-full object-cover"
                            width={64}
                            height={64}
                          />
                        ) : (
                          <User className="w-8 h-8 text-gray-500" />
                        )}
                      </div>
                      
                      {/* Name and title */}
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {result.connection.first_name} {result.connection.last_name}
                        </h3>
                        {result.connection.company_name && (
                          <p className="text-md font-semibold text-gray-800 mt-1">
                            {result.connection.company_name}
                          </p>
                        )}
                        <p className="text-gray-600">
                          {result.connection.headline || result.connection.title ? (
                            <>
                              {result.connection.headline}
                              {result.connection.headline && result.connection.title ? ' | ' : ''}
                              {result.connection.title}
                            </>
                          ) : (
                            'No headline or title available'
                          )}
                        </p>
                        {result.connection.email_address && (
                          <p className="text-xs text-gray-500 mt-1">
                            📧 {result.connection.email_address}
                          </p>
                        )}
                        {result.connection.connected_on && (
                          <p className="text-sm text-gray-500 mt-1">
                            Connected on {new Date(result.connection.connected_on).toLocaleDateString('en-US', {
                              day: '2-digit',
                              month: 'short',
                              year: 'numeric'
                            })}
                          </p>
                        )}
                      </div>
                    </div>
                    
                    {/* Score and badges */}
                    <div className="flex items-center space-x-2">
                      {result.score >= 9 && (
                        <Badge className="bg-yellow-500 hover:bg-yellow-600 text-white">
                          Top Match
                        </Badge>
                      )}
                      <div className="text-right">
                        <div className="text-2xl font-bold text-blue-600">{result.score}</div>
                        <div className="text-xs text-gray-500">Relevance</div>
                      </div>
                    </div>
                  </div>

                  {/* Badges */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {result.connection.is_premium && <Badge className="bg-purple-600 hover:bg-purple-700 text-white">Premium</Badge>}
                    {result.connection.is_top_voice && <Badge className="bg-blue-500 hover:bg-blue-600 text-white">Top Voice</Badge>}
                    {result.connection.is_influencer && <Badge className="bg-pink-500 hover:bg-pink-600 text-white">Influencer</Badge>}
                    {result.connection.is_hiring && <Badge className="bg-green-500 hover:bg-green-600 text-white">Hiring</Badge>}
                    {result.connection.is_open_to_work && <Badge className="bg-teal-500 hover:bg-teal-600 text-white">Open to Work</Badge>}
                    {result.connection.is_creator && <Badge className="bg-indigo-500 hover:bg-indigo-600 text-white">Creator</Badge>}
                  </div>

                  {/* Summary */}
                  <p className="text-gray-700 mb-4">{result.summary}</p>

                  {/* Pros */}
                  {result.pros && result.pros.length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-medium text-green-700 mb-2">Why this may be a good match:</h4>
                      <ul className="space-y-1">
                        {result.pros.map((pro, idx) => (
                          <li key={idx} className="text-sm text-gray-700 flex items-start">
                            <span className="text-green-600 mr-2">•</span>
                            {pro}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Cons */}
                  {result.cons && result.cons.length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-medium text-red-700 mb-2">Why this may not be a good match:</h4>
                      <ul className="space-y-1">
                        {result.cons.map((con, idx) => (
                          <li key={idx} className="text-sm text-gray-700 flex items-start">
                            <span className="text-red-600 mr-2">•</span>
                            {con}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex items-center space-x-4 mt-6">
                    <Button
                      onClick={() => handleEmailConnection(
                        result.connection.email_address,
                        `${result.connection.first_name} ${result.connection.last_name}`
                      )}
                      className="bg-blue-600 hover:bg-blue-700 text-white"
                    >
                      Request a Warm Intro
                    </Button>
                    {result.connection.linkedin_url && (
                      <a
                        href={result.connection.linkedin_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-10 px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800"
                      >
                        <Linkedin className="w-5 h-5 mr-2" />
                        LinkedIn Profile
                      </a>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Getting Started */}
        {!hasSearched && (
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold mb-3">Getting Started</h3>
            <div className="space-y-2 text-sm text-gray-600">
              <p>• Use natural language to describe who you&apos;re looking for</p>
              <p>• Try queries like &quot;VCs who invest in seed stage consumer startups&quot;</p>
              <p>• The AI will analyze your connections and provide detailed match analysis</p>
              <p>• Connections with scores 9-10 are marked as &quot;Top Matches&quot;</p>
            </div>
          </div>
        )}
      </div>
      <EmailGenerationModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        connection={selectedConnection}
      />
      <TippingModal
        isOpen={isTippingModalOpen}
        onClose={() => setIsTippingModalOpen(false)}
        connection={selectedConnection}
      />
    </div>
  );
}