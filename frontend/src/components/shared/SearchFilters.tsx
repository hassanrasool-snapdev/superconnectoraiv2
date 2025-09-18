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
  industries?: string[];
  company_sizes?: string[];
  locations?: string[];
  hiring_status?: 'hiring' | 'open_to_work';
  is_company_owner?: boolean;
  has_pe_vc_role?: boolean;
  geo_location?: string;
  employment_status?: string;
}

interface SearchFiltersProps {
  filters: SearchFilters;
  onFiltersChange: (filters: SearchFilters) => void;
  onClearFilters: () => void;
}

const INDUSTRY_OPTIONS = [
  'Technology',
  'Finance',
  'Healthcare',
  'Education',
  'Retail',
  'Manufacturing',
  'Real Estate',
  'Consulting',
  'Media & Entertainment',
  'Non-profit',
  'Government',
  'Energy',
  'Transportation',
  'Food & Beverage',
  'Fashion',
  'Sports',
  'Travel & Tourism'
];

const COMPANY_SIZE_OPTIONS = [
  '1-10 employees',
  '11-50 employees',
  '51-200 employees',
  '201-500 employees',
  '501-1000 employees',
  '1001-5000 employees',
  '5001-10000 employees',
  '10000+ employees'
];

const LOCATION_OPTIONS = [
  'San Francisco Bay Area',
  'New York City',
  'Los Angeles',
  'Chicago',
  'Boston',
  'Seattle',
  'Austin',
  'Denver',
  'Miami',
  'Atlanta',
  'London',
  'Paris',
  'Berlin',
  'Toronto',
  'Sydney',
  'Singapore',
  'Tokyo',
  'Remote'
];

export default function SearchFiltersComponent({ filters, onFiltersChange, onClearFilters }: SearchFiltersProps) {
  const { token } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [tempFilters, setTempFilters] = useState<SearchFilters>(filters);
  const [dynamicOptions, setDynamicOptions] = useState<{
    industries: string[];
    company_sizes: string[];
    locations: string[];
    professional_status_counts: Record<string, number>;
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
  const industryOptions = (dynamicOptions?.industries && dynamicOptions.industries.length > 0)
    ? dynamicOptions.industries
    : INDUSTRY_OPTIONS;
  const companySizeOptions = (dynamicOptions?.company_sizes && dynamicOptions.company_sizes.length > 0)
    ? dynamicOptions.company_sizes
    : COMPANY_SIZE_OPTIONS;
  const locationOptions = (dynamicOptions?.locations && dynamicOptions.locations.length > 0)
    ? dynamicOptions.locations
    : LOCATION_OPTIONS;

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

  const addToArrayFilter = (key: keyof SearchFilters, value: string) => {
    const currentArray = (tempFilters[key] as string[]) || [];
    if (!currentArray.includes(value)) {
      setTempFilters({
        ...tempFilters,
        [key]: [...currentArray, value]
      });
    }
  };

  const removeFromArrayFilter = (key: keyof SearchFilters, value: string) => {
    const currentArray = (tempFilters[key] as string[]) || [];
    setTempFilters({
      ...tempFilters,
      [key]: currentArray.filter(item => item !== value)
    });
  };

  const setHiringStatus = (status: 'hiring' | 'open_to_work' | null) => {
    setTempFilters({
      ...tempFilters,
      hiring_status: status || undefined
    });
  };

  const toggleBooleanFilter = (key: keyof SearchFilters) => {
    setTempFilters({
      ...tempFilters,
      [key]: tempFilters[key] ? undefined : true
    });
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (filters.industries?.length) count++;
    if (filters.company_sizes?.length) count++;
    if (filters.locations?.length) count++;
    if (filters.hiring_status) count++;
    if (filters.is_company_owner) count++;
    if (filters.has_pe_vc_role) count++;
    if (filters.geo_location) count++;
    if (filters.employment_status) count++;
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
      
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between pr-8">
            <div className="flex items-center space-x-2">
              <span>Search Filters</span>
              {dynamicOptions && dynamicOptions.generated_from === 'user_network_data' && dynamicOptions.total_connections > 0 && (
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
            {/* Industries */}
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Building2 className="w-5 h-5 text-gray-600" />
                <Label className="text-base font-semibold text-gray-800">Industries</Label>
              </div>
              <div className="flex flex-wrap gap-2">
                {industryOptions.map((industry) => (
                  <Button
                    key={industry}
                    variant={tempFilters.industries?.includes(industry) ? "default" : "outline"}
                    size="sm"
                    onClick={() =>
                      tempFilters.industries?.includes(industry)
                        ? removeFromArrayFilter('industries', industry)
                        : addToArrayFilter('industries', industry)
                    }
                    className="text-xs"
                  >
                    {industry}
                  </Button>
                ))}
              </div>
            </div>

            {/* Company Sizes */}
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Users className="w-5 h-5 text-gray-600" />
                <Label className="text-base font-semibold text-gray-800">Company Size</Label>
              </div>
              <div className="flex flex-wrap gap-2">
                {companySizeOptions.map((size) => (
                  <Button
                    key={size}
                    variant={tempFilters.company_sizes?.includes(size) ? "default" : "outline"}
                    size="sm"
                    onClick={() =>
                      tempFilters.company_sizes?.includes(size)
                        ? removeFromArrayFilter('company_sizes', size)
                        : addToArrayFilter('company_sizes', size)
                    }
                    className="text-xs"
                  >
                    {size}
                  </Button>
                ))}
              </div>
            </div>

            {/* Locations */}
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <MapPin className="w-5 h-5 text-gray-600" />
                <Label className="text-base font-semibold text-gray-800">Locations</Label>
              </div>
              <div className="flex flex-wrap gap-2">
                {locationOptions.map((location) => (
                  <Button
                    key={location}
                    variant={tempFilters.locations?.includes(location) ? "default" : "outline"}
                    size="sm"
                    onClick={() =>
                      tempFilters.locations?.includes(location)
                        ? removeFromArrayFilter('locations', location)
                        : addToArrayFilter('locations', location)
                    }
                    className="text-xs"
                  >
                    {location}
                  </Button>
                ))}
              </div>
            </div>

            {/* Employment Status */}
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <UserCheck className="w-5 h-5 text-gray-600" />
                <Label className="text-base font-semibold text-gray-800">Employment Status</Label>
                <span className="text-xs text-gray-500">(Choose one or neither)</span>
              </div>
              <div className="space-y-2">
                {/* Clear selection option */}
                <Button
                  variant={!tempFilters.hiring_status ? "default" : "outline"}
                  size="sm"
                  onClick={() => setHiringStatus(null)}
                  className="justify-start w-full"
                >
                  Any Employment Status
                </Button>
                
                {/* Mutually exclusive hiring status */}
                <div className="grid grid-cols-2 gap-3">
                  <Button
                    variant={tempFilters.hiring_status === 'hiring' ? "default" : "outline"}
                    size="sm"
                    onClick={() => setHiringStatus(tempFilters.hiring_status === 'hiring' ? null : 'hiring')}
                    className="justify-start"
                  >
                    <UserCheck className="w-4 h-4 mr-2" />
                    Actively Hiring
                    {dynamicOptions?.professional_status_counts?.hiring_count && (
                      <Badge variant="secondary" className="ml-2 text-xs">
                        {dynamicOptions.professional_status_counts.hiring_count}
                      </Badge>
                    )}
                  </Button>
                  <Button
                    variant={tempFilters.hiring_status === 'open_to_work' ? "default" : "outline"}
                    size="sm"
                    onClick={() => setHiringStatus(tempFilters.hiring_status === 'open_to_work' ? null : 'open_to_work')}
                    className="justify-start"
                  >
                    <Briefcase className="w-4 h-4 mr-2" />
                    Open to Work
                    {dynamicOptions?.professional_status_counts?.open_to_work_count && (
                      <Badge variant="secondary" className="ml-2 text-xs">
                        {dynamicOptions.professional_status_counts.open_to_work_count}
                      </Badge>
                    )}
                  </Button>
                </div>
              </div>
            </div>

            {/* Role Type */}
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Building2 className="w-5 h-5 text-gray-600" />
                <Label className="text-base font-semibold text-gray-800">Role Type</Label>
                <span className="text-xs text-gray-500">(Can combine with employment status)</span>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <Button
                  variant={tempFilters.is_company_owner ? "default" : "outline"}
                  size="sm"
                  onClick={() => toggleBooleanFilter('is_company_owner')}
                  className="justify-start"
                >
                  <Building2 className="w-4 h-4 mr-2" />
                  Company Owner
                  {dynamicOptions?.professional_status_counts?.company_owner_count && (
                    <Badge variant="secondary" className="ml-2 text-xs">
                      {dynamicOptions.professional_status_counts.company_owner_count}
                    </Badge>
                  )}
                </Button>
                <Button
                  variant={tempFilters.has_pe_vc_role ? "default" : "outline"}
                  size="sm"
                  onClick={() => toggleBooleanFilter('has_pe_vc_role')}
                  className="justify-start"
                >
                  <TrendingUp className="w-4 h-4 mr-2" />
                  PE/VC Role
                  {dynamicOptions?.professional_status_counts?.pe_vc_count && (
                    <Badge variant="secondary" className="ml-2 text-xs">
                      {dynamicOptions.professional_status_counts.pe_vc_count}
                    </Badge>
                  )}
                </Button>
              </div>
            </div>

            {/* Company Relationship */}
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Briefcase className="w-5 h-5 text-gray-600" />
                <Label className="text-base font-semibold text-gray-800">Company Relationship</Label>
              </div>
              <Select
                value={tempFilters.employment_status || ""}
                onValueChange={(value) =>
                  setTempFilters({
                    ...tempFilters,
                    employment_status: value || undefined
                  })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Filter by company relationship" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All connections</SelectItem>
                  <SelectItem value="current">Currently works at company</SelectItem>
                  <SelectItem value="past">Previously worked at company</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-gray-500 mt-1">
                Only applies when searching for people at specific companies
              </p>
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