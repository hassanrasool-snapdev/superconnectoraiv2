'use client';

import React, { useState, useEffect } from 'react';
import {
  Bookmark,
  Play,
  Edit,
  Trash2,
  Plus,
  Search,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { getSavedSearches, createSavedSearch, deleteSavedSearch } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';

interface SavedSearch {
  id: string;
  name: string;
  query: string;
  filters?: any;
  created_at: string;
}

interface SavedSearchesProps {
  onRunSearch: (query: string, filters?: any) => void;
  currentQuery?: string;
  currentFilters?: any;
}

const SavedSearches: React.FC<SavedSearchesProps> = ({
  onRunSearch,
  currentQuery = '',
  currentFilters = {}
}) => {
  const { token } = useAuth();
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingSearch, setEditingSearch] = useState<SavedSearch | null>(null);
  const [searchName, setSearchName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);

  // Load saved searches on component mount
  useEffect(() => {
    loadSavedSearches();
  }, []);

  const loadSavedSearches = async () => {
    if (!token) return;
    
    try {
      setIsLoading(true);
      const searches = await getSavedSearches(token);
      setSavedSearches(searches);
    } catch (error) {
      console.error('Failed to load saved searches:', error);
      setSavedSearches([]);
    } finally {
      setIsLoading(false);
    }
  };

  const saveCurrentSearch = async () => {
    if (!searchName.trim()) {
      setError('Please enter a name for your search');
      return;
    }

    if (!currentQuery.trim()) {
      setError('No search query to save');
      return;
    }

    if (!token) {
      setError('Authentication required');
      return;
    }

    try {
      await createSavedSearch(searchName.trim(), currentQuery, currentFilters, token);
      setShowSaveModal(false);
      setSearchName('');
      setError(null);
      await loadSavedSearches();
    } catch (error) {
      setError('Error saving search');
      console.error('Error saving search:', error);
    }
  };

  const updateSearch = async () => {
    if (!searchName.trim() || !editingSearch) {
      setError('Please enter a name for your search');
      return;
    }

    if (!token) {
      setError('Authentication required');
      return;
    }

    try {
      // For now, we'll implement a simple update by calling the API directly
      // This should be moved to api.ts if update functionality is needed
      const response = await fetch(`http://localhost:8000/api/v1/saved-searches/${editingSearch.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: searchName.trim(),
        }),
      });

      if (response.ok) {
        setShowEditModal(false);
        setEditingSearch(null);
        setSearchName('');
        setError(null);
        await loadSavedSearches();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to update search');
      }
    } catch (error) {
      setError('Error updating search');
      console.error('Error updating search:', error);
    }
  };

  const deleteSearch = async (searchId: string) => {
    if (!confirm('Are you sure you want to delete this saved search?')) {
      return;
    }

    if (!token) {
      console.error('Authentication required');
      return;
    }

    try {
      await deleteSavedSearch(searchId, token);
      await loadSavedSearches();
    } catch (error) {
      console.error('Error deleting search:', error);
    }
  };

  const runSavedSearch = async (search: SavedSearch) => {
    onRunSearch(search.query, search.filters);
  };

  const openSaveModal = () => {
    setSearchName('');
    setError(null);
    setShowSaveModal(true);
  };

  const openEditModal = (search: SavedSearch) => {
    setEditingSearch(search);
    setSearchName(search.name);
    setError(null);
    setShowEditModal(true);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="px-4 sm:px-6 py-3 border-b border-gray-200">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center space-x-2 text-left hover:text-blue-600 transition-colors"
          >
            {isExpanded ? (
              <ChevronDown className="h-4 w-4 text-gray-500" />
            ) : (
              <ChevronRight className="h-4 w-4 text-gray-500" />
            )}
            <Bookmark className="h-5 w-5 text-blue-600" />
            <h3 className="text-lg font-medium text-gray-900">
              Saved Searches {savedSearches.length > 0 && `(${savedSearches.length})`}
            </h3>
          </button>
          {currentQuery && (
            <Button
              onClick={openSaveModal}
              variant="outline"
              size="sm"
              className="text-blue-700 border-blue-200 hover:bg-blue-50 w-full sm:w-auto"
            >
              <Plus className="h-4 w-4 mr-1" />
              Save Current Search
            </Button>
          )}
        </div>
      </div>

      {isExpanded && (
        <div className="p-4 sm:p-6">
        {isLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-500">Loading saved searches...</p>
          </div>
        ) : savedSearches.length === 0 ? (
          <div className="text-center py-8">
            <Bookmark className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No saved searches</h3>
            <p className="mt-1 text-sm text-gray-500">
              Save your searches to quickly access them later.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {savedSearches.map((search) => (
              <div
                key={search.id}
                className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-3 sm:p-4 border border-gray-200 rounded-lg hover:bg-gray-50 gap-3"
              >
                <div className="flex-1 min-w-0 w-full sm:w-auto">
                  <div className="flex items-start sm:items-center space-x-3">
                    <Search className="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5 sm:mt-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {search.name}
                      </p>
                      <p className="text-sm text-gray-500 truncate">
                        "{search.query}"
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        Saved on {formatDate(search.created_at)}
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center justify-end space-x-1 sm:space-x-2 w-full sm:w-auto sm:ml-4">
                  <Button
                    onClick={() => runSavedSearch(search)}
                    variant="ghost"
                    size="sm"
                    className="p-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50 flex-1 sm:flex-none"
                    title="Run this search"
                  >
                    <Play className="h-4 w-4" />
                    <span className="ml-1 sm:hidden">Run</span>
                  </Button>
                  <Button
                    onClick={() => openEditModal(search)}
                    variant="ghost"
                    size="sm"
                    className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-50 flex-1 sm:flex-none"
                    title="Edit search name"
                  >
                    <Edit className="h-4 w-4" />
                    <span className="ml-1 sm:hidden">Edit</span>
                  </Button>
                  <Button
                    onClick={() => deleteSearch(search.id)}
                    variant="ghost"
                    size="sm"
                    className="p-2 text-red-600 hover:text-red-800 hover:bg-red-50 flex-1 sm:flex-none"
                    title="Delete search"
                  >
                    <Trash2 className="h-4 w-4" />
                    <span className="ml-1 sm:hidden">Delete</span>
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
        </div>
      )}

      {/* Save Search Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 p-4">
          <div className="relative top-20 mx-auto p-5 border w-full max-w-md shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Save Search</h3>
              
              <div className="mb-4">
                <Label className="block text-sm font-medium text-gray-700 mb-2">
                  Search Name
                </Label>
                <Input
                  type="text"
                  value={searchName}
                  onChange={(e) => setSearchName(e.target.value)}
                  placeholder="Enter a name for this search"
                  autoFocus
                />
              </div>

              <div className="mb-4">
                <Label className="block text-sm font-medium text-gray-700 mb-2">
                  Query
                </Label>
                <p className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                  "{currentQuery}"
                </p>
              </div>

              {error && (
                <div className="mb-4 text-sm text-red-600">
                  {error}
                </div>
              )}

              <div className="flex justify-end space-x-3">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowSaveModal(false);
                    setSearchName('');
                    setError(null);
                  }}
                >
                  Cancel
                </Button>
                <Button
                  onClick={saveCurrentSearch}
                >
                  Save Search
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Search Modal */}
      {showEditModal && editingSearch && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 p-4">
          <div className="relative top-20 mx-auto p-5 border w-full max-w-md shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Edit Search</h3>
              
              <div className="mb-4">
                <Label className="block text-sm font-medium text-gray-700 mb-2">
                  Search Name
                </Label>
                <Input
                  type="text"
                  value={searchName}
                  onChange={(e) => setSearchName(e.target.value)}
                  placeholder="Enter a name for this search"
                  autoFocus
                />
              </div>

              {error && (
                <div className="mb-4 text-sm text-red-600">
                  {error}
                </div>
              )}

              <div className="flex justify-end space-x-3">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowEditModal(false);
                    setEditingSearch(null);
                    setSearchName('');
                    setError(null);
                  }}
                >
                  Cancel
                </Button>
                <Button
                  onClick={updateSearch}
                >
                  Update Search
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SavedSearches;