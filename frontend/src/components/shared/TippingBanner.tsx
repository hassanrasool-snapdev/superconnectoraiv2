'use client';

import { Heart } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface TippingBannerProps {
  onSupportClick: () => void;
}

export const TippingBanner: React.FC<TippingBannerProps> = ({ onSupportClick }) => {
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
      <div className="flex justify-center mb-4">
        <Heart className="w-10 h-10 text-red-500" />
      </div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        Help keep Superconnect AI alive.
      </h2>
      <p className="text-gray-600 mb-6">
        Most people choose to contribute $20. It helps keep the lights on and the warm intros coming.
      </p>
      <Button onClick={onSupportClick} className="bg-green-500 hover:bg-green-600 text-white px-8 py-3 rounded-full">
        Support Superconnect AI
      </Button>
    </div>
  );
};