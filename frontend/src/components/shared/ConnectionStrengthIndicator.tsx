'use client';

import React from 'react';
import { Badge } from '@/components/ui/badge';
import { 
  Building2, 
  GraduationCap, 
  Calendar, 
  Users, 
  MessageCircle, 
  Award,
  Clock,
  MapPin
} from 'lucide-react';

interface ConnectionStrengthProps {
  connection: {
    connected_on?: string;
    company_name?: string;
    city?: string;
    state?: string;
    country?: string;
    // Additional fields that might indicate connection strength
    mutual_connections?: number;
    shared_companies?: string[];
    shared_schools?: string[];
    endorsements?: number;
    recommendations?: number;
    last_interaction?: string;
    interaction_frequency?: 'high' | 'medium' | 'low';
  };
  facilitatorProfile?: {
    companies?: string[];
    schools?: string[];
    location?: string;
  };
}

export default function ConnectionStrengthIndicator({ connection, facilitatorProfile }: ConnectionStrengthProps) {
  const getConnectionDuration = () => {
    if (!connection.connected_on) return null;
    
    try {
      const connectedDate = new Date(connection.connected_on);
      const now = new Date();
      const diffTime = Math.abs(now.getTime() - connectedDate.getTime());
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      const diffYears = Math.floor(diffDays / 365);
      const diffMonths = Math.floor((diffDays % 365) / 30);
      
      if (diffYears > 0) {
        return `${diffYears} year${diffYears > 1 ? 's' : ''}`;
      } else if (diffMonths > 0) {
        return `${diffMonths} month${diffMonths > 1 ? 's' : ''}`;
      } else {
        return `${diffDays} day${diffDays > 1 ? 's' : ''}`;
      }
    } catch {
      return null;
    }
  };

  const getSharedCompanies = () => {
    if (!facilitatorProfile?.companies || !connection.shared_companies) return [];
    return connection.shared_companies.filter(company => 
      facilitatorProfile.companies?.some(facCompany => 
        facCompany.toLowerCase().includes(company.toLowerCase()) ||
        company.toLowerCase().includes(facCompany.toLowerCase())
      )
    );
  };

  const getSharedSchools = () => {
    if (!facilitatorProfile?.schools || !connection.shared_schools) return [];
    return connection.shared_schools.filter(school => 
      facilitatorProfile.schools?.some(facSchool => 
        facSchool.toLowerCase().includes(school.toLowerCase()) ||
        school.toLowerCase().includes(facSchool.toLowerCase())
      )
    );
  };

  const getLocationProximity = () => {
    if (!facilitatorProfile?.location) return null;
    
    const connectionLocation = [connection.city, connection.state, connection.country]
      .filter(Boolean)
      .join(', ');
    
    if (!connectionLocation) return null;
    
    // Simple proximity check - in a real app, you'd use proper geolocation
    const facLocation = facilitatorProfile.location.toLowerCase();
    const connLocation = connectionLocation.toLowerCase();
    
    if (facLocation === connLocation) return 'Same location';
    if (connection.city && facLocation.includes(connection.city.toLowerCase())) return 'Same city';
    if (connection.state && facLocation.includes(connection.state.toLowerCase())) return 'Same state';
    if (connection.country && facLocation.includes(connection.country.toLowerCase())) return 'Same country';
    
    return null;
  };

  const getConnectionStrength = () => {
    let strength = 0;
    const factors = [];

    // Duration factor
    const duration = getConnectionDuration();
    if (duration) {
      if (duration.includes('year')) {
        const years = parseInt(duration);
        if (years >= 5) {
          strength += 3;
          factors.push('Long-term connection');
        } else if (years >= 2) {
          strength += 2;
          factors.push('Established connection');
        } else {
          strength += 1;
          factors.push('Recent connection');
        }
      }
    }

    // Shared companies
    const sharedCompanies = getSharedCompanies();
    if (sharedCompanies.length > 0) {
      strength += 2;
      factors.push('Shared work history');
    }

    // Shared schools
    const sharedSchools = getSharedSchools();
    if (sharedSchools.length > 0) {
      strength += 2;
      factors.push('Shared education');
    }

    // Location proximity
    const locationProximity = getLocationProximity();
    if (locationProximity) {
      strength += 1;
      factors.push(locationProximity);
    }

    // Mutual connections
    if (connection.mutual_connections && connection.mutual_connections > 0) {
      if (connection.mutual_connections >= 10) {
        strength += 2;
        factors.push('Many mutual connections');
      } else if (connection.mutual_connections >= 5) {
        strength += 1;
        factors.push('Several mutual connections');
      }
    }

    // Endorsements and recommendations
    if (connection.endorsements && connection.endorsements > 0) {
      strength += 1;
      factors.push('Professional endorsements');
    }

    if (connection.recommendations && connection.recommendations > 0) {
      strength += 1;
      factors.push('LinkedIn recommendations');
    }

    // Interaction frequency
    if (connection.interaction_frequency) {
      switch (connection.interaction_frequency) {
        case 'high':
          strength += 3;
          factors.push('Frequent interactions');
          break;
        case 'medium':
          strength += 2;
          factors.push('Regular interactions');
          break;
        case 'low':
          strength += 1;
          factors.push('Occasional interactions');
          break;
      }
    }

    return { strength, factors };
  };

  const { strength, factors } = getConnectionStrength();
  const duration = getConnectionDuration();
  const sharedCompanies = getSharedCompanies();
  const sharedSchools = getSharedSchools();
  const locationProximity = getLocationProximity();

  const getStrengthLevel = () => {
    if (strength >= 8) return { level: 'Very Strong', color: 'bg-green-600', textColor: 'text-green-800' };
    if (strength >= 6) return { level: 'Strong', color: 'bg-green-500', textColor: 'text-green-700' };
    if (strength >= 4) return { level: 'Moderate', color: 'bg-yellow-500', textColor: 'text-yellow-700' };
    if (strength >= 2) return { level: 'Weak', color: 'bg-orange-500', textColor: 'text-orange-700' };
    return { level: 'Unknown', color: 'bg-gray-400', textColor: 'text-gray-600' };
  };

  const strengthLevel = getStrengthLevel();

  if (factors.length === 0 && !duration) {
    return null; // Don't show if no connection data available
  }

  return (
    <div className="bg-gray-50 rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium text-gray-900 flex items-center">
          <Users className="w-4 h-4 mr-2 text-gray-500" />
          Connection Strength
        </h4>
        <Badge className={`${strengthLevel.color} text-white text-xs`}>
          {strengthLevel.level}
        </Badge>
      </div>

      <div className="space-y-2">
        {/* Connection Duration */}
        {duration && (
          <div className="flex items-center text-sm text-gray-600">
            <Clock className="w-3 h-3 mr-2 text-gray-400" />
            Connected for {duration}
          </div>
        )}

        {/* Shared Companies */}
        {sharedCompanies.length > 0 && (
          <div className="flex items-start text-sm text-gray-600">
            <Building2 className="w-3 h-3 mr-2 mt-0.5 text-gray-400 flex-shrink-0" />
            <span>Shared companies: {sharedCompanies.join(', ')}</span>
          </div>
        )}

        {/* Shared Schools */}
        {sharedSchools.length > 0 && (
          <div className="flex items-start text-sm text-gray-600">
            <GraduationCap className="w-3 h-3 mr-2 mt-0.5 text-gray-400 flex-shrink-0" />
            <span>Shared schools: {sharedSchools.join(', ')}</span>
          </div>
        )}

        {/* Location Proximity */}
        {locationProximity && (
          <div className="flex items-center text-sm text-gray-600">
            <MapPin className="w-3 h-3 mr-2 text-gray-400" />
            {locationProximity}
          </div>
        )}

        {/* Mutual Connections */}
        {connection.mutual_connections && connection.mutual_connections > 0 && (
          <div className="flex items-center text-sm text-gray-600">
            <Users className="w-3 h-3 mr-2 text-gray-400" />
            {connection.mutual_connections} mutual connections
          </div>
        )}

        {/* Endorsements */}
        {connection.endorsements && connection.endorsements > 0 && (
          <div className="flex items-center text-sm text-gray-600">
            <Award className="w-3 h-3 mr-2 text-gray-400" />
            {connection.endorsements} endorsements
          </div>
        )}

        {/* Recommendations */}
        {connection.recommendations && connection.recommendations > 0 && (
          <div className="flex items-center text-sm text-gray-600">
            <MessageCircle className="w-3 h-3 mr-2 text-gray-400" />
            {connection.recommendations} recommendations
          </div>
        )}

        {/* Interaction Frequency */}
        {connection.interaction_frequency && (
          <div className="flex items-center text-sm text-gray-600">
            <MessageCircle className="w-3 h-3 mr-2 text-gray-400" />
            {connection.interaction_frequency === 'high' && 'Frequent interactions'}
            {connection.interaction_frequency === 'medium' && 'Regular interactions'}
            {connection.interaction_frequency === 'low' && 'Occasional interactions'}
          </div>
        )}

        {/* Last Interaction */}
        {connection.last_interaction && (
          <div className="flex items-center text-sm text-gray-600">
            <Calendar className="w-3 h-3 mr-2 text-gray-400" />
            Last interaction: {new Date(connection.last_interaction).toLocaleDateString()}
          </div>
        )}
      </div>

      {/* Connection Tips */}
      {factors.length > 0 && (
        <div className="pt-2 border-t border-gray-200">
          <p className="text-xs text-gray-500">
            <strong>Connection context:</strong> {factors.join(', ').toLowerCase()}
          </p>
        </div>
      )}
    </div>
  );
}