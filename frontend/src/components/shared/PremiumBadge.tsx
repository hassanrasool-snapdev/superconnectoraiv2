import React from 'react';
import { Badge } from '../ui/badge';
import { Crown } from 'lucide-react';

interface PremiumBadgeProps {
  isPremium: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'compact';
}

export const PremiumBadge: React.FC<PremiumBadgeProps> = ({ 
  isPremium, 
  size = 'sm',
  variant = 'default'
}) => {
  if (!isPremium) return null;

  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-2'
  };

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4', 
    lg: 'w-5 h-5'
  };

  if (variant === 'compact') {
    return (
      <Badge className={`bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white border-0 ${sizeClasses[size]}`}>
        <Crown className={`${iconSizes[size]} mr-1`} />
        Premium
      </Badge>
    );
  }

  return (
    <Badge className={`bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white border-0 ${sizeClasses[size]}`}>
      <Crown className={`${iconSizes[size]} mr-1`} />
      Premium Member
    </Badge>
  );
};

export default PremiumBadge;