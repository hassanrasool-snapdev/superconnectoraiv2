'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Filter,
  X,
  MapPin,
  Building2,
  Users,
  Briefcase,
  TrendingUp,
  UserCheck,
  Loader2
} from 'lucide-react';
import { getFilterOptions } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';

export interface SearchFilters {
  open_to_work?: boolean;
  country?: string;
}

interface SearchFiltersProps {
  filters: SearchFilters;
  onFiltersChange: (filters: SearchFilters) => void;
  onClearFilters: () => void;
}


export default function SearchFiltersComponent({ filters, onFiltersChange, onClearFilters }: SearchFiltersProps) {
  const { token } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [tempFilters, setTempFilters] = useState<SearchFilters>(filters);
  const [dynamicOptions, setDynamicOptions] = useState<{
    countries: string[];
    open_to_work_count: number;
    total_connections: number;
    generated_from: string;
  } | null>(null);
  const [loadingOptions, setLoadingOptions] = useState(false);

  // Load dynamic filter options when component mounts or when dialog opens
  useEffect(() => {
    if (isOpen && token && !dynamicOptions) {
      loadFilterOptions();
    }
  }, [isOpen, token, dynamicOptions]);

  const loadFilterOptions = async () => {
    if (!token) return;
    
    setLoadingOptions(true);
    try {
      const options = await getFilterOptions(token);
      setDynamicOptions(options);
    } catch (error) {
      console.error('Failed to load dynamic filter options:', error);
      // Keep static fallback options if dynamic loading fails
    } finally {
      setLoadingOptions(false);
    }
  };

  // Use dynamic options if available and not empty, otherwise fall back to static options
  const countryOptions = (dynamicOptions?.countries && dynamicOptions.countries.length > 0)
    ? dynamicOptions.countries
    : [
        'United States', 'Canada', 'United Kingdom', 'Germany', 'France',
        'Australia', 'India', 'Singapore', 'Netherlands', 'Switzerland',
        'Japan', 'Brazil', 'Mexico', 'Spain', 'Italy', 'Sweden',
        'Norway', 'Denmark', 'Belgium', 'Austria', 'Ireland', 'Israel',
        'South Korea', 'China', 'Hong Kong', 'New Zealand', 'Finland',
        'Portugal', 'Czech Republic', 'Poland', 'Russia', 'Ukraine',
        'South Africa', 'Argentina', 'Chile', 'Colombia'
      ];

  const handleApplyFilters = () => {
    onFiltersChange(tempFilters);
    setIsOpen(false);
  };

  const handleClearAll = () => {
    setTempFilters({});
    // Don't automatically trigger search when clearing - let user apply manually
    // onClearFilters();
    // Don't close the modal - let user continue filtering
  };

  const setOpenToWork = (value: boolean | undefined) => {
    setTempFilters({
      ...tempFilters,
      open_to_work: value
    });
  };

  const setCountry = (value: string | undefined) => {
    setTempFilters({
      ...tempFilters,
      country: value
    });
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (filters.open_to_work) count++;
    if (filters.country) count++;
    return count;
  };

  const activeCount = getActiveFiltersCount();

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="relative">
          <Filter className="w-4 h-4 mr-2" />
          Filters
          {activeCount > 0 && (
            <Badge className="ml-2 bg-blue-600 text-white text-xs px-1.5 py-0.5 min-w-[20px] h-5">
              {activeCount}
            </Badge>
          )}
        </Button>
      </DialogTrigger>
      
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between pr-8">
            <div className="flex items-center space-x-2">
              <span>Search Filters</span>
              {dynamicOptions && dynamicOptions.generated_from === 'streamlined_user_data' && dynamicOptions.total_connections > 0 && (
                <Badge variant="secondary" className="text-xs">
                  From {dynamicOptions.total_connections.toLocaleString()} connections
                </Badge>
              )}
            </div>
            <Button variant="ghost" size="sm" onClick={handleClearAll} className="mr-4" type="button">
              Clear All
            </Button>
          </DialogTitle>
        </DialogHeader>

        {loadingOptions ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-6 h-6 animate-spin mr-2" />
            <span className="text-sm text-gray-600">Loading filter options from your network...</span>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Open to Work Filter */}
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Briefcase className="w-5 h-5 text-gray-600" />
                <Label className="text-base font-semibold text-gray-800">Open to Work</Label>
              </div>
              <div className="space-y-2">
                <Button
                  variant={tempFilters.open_to_work === undefined ? "default" : "outline"}
                  size="sm"
                  onClick={() => setOpenToWork(undefined)}
                  className="justify-start w-full"
                >
                  All Connections
                </Button>
                <Button
                  variant={tempFilters.open_to_work === true ? "default" : "outline"}
                  size="sm"
                  onClick={() => setOpenToWork(tempFilters.open_to_work === true ? undefined : true)}
                  className="justify-start w-full"
                >
                  <Briefcase className="w-4 h-4 mr-2" />
                  Open to Work Only
                  {dynamicOptions?.open_to_work_count !== undefined && dynamicOptions.open_to_work_count > 0 && (
                    <Badge variant="secondary" className="ml-2 text-xs">
                      {dynamicOptions.open_to_work_count}
                    </Badge>
                  )}
                </Button>
              </div>
            </div>

            {/* Country Filter */}
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <MapPin className="w-5 h-5 text-gray-600" />
                <Label className="text-base font-semibold text-gray-800">Country</Label>
              </div>
              <Select
                value={tempFilters.country || ""}
                onValueChange={(value) => setCountry(value || undefined)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All countries" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All countries</SelectItem>
                  {countryOptions.map((country) => (
                    <SelectItem key={country} value={country}>
                      {country}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="flex justify-end space-x-3 pt-6 border-t">
          <Button variant="outline" onClick={() => setIsOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleApplyFilters}>
            Apply Filters
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}