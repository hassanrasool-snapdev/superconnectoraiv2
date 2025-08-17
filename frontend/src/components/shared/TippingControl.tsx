'use client';

import { useState, useEffect } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { Button } from '@/components/ui/button';

interface TippingControlProps {
  venmoId: string;
  paypalId: string;
  amount: number;
  venmoCopy?: string;
  paypalCopy?: string;
}

export const TippingControl: React.FC<TippingControlProps> = ({
  venmoId,
  paypalId,
  amount,
  venmoCopy = 'Pay with Venmo',
  paypalCopy = 'Pay with PayPal',
}) => {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const userAgent = navigator.userAgent || navigator.vendor || (window as any).opera;
    setIsMobile(/android|iphone|ipad|ipod/i.test(userAgent));
  }, []);

  const venmoUrl = `https://venmo.com/${venmoId}?txn=pay&amount=${amount}`;
  const venmoAppUrl = `venmo://paycharge?txn=pay&recipients=${venmoId}&amount=${amount}&note=Superconnect%20AI%20Tip`;
  const paypalUrl = `https://www.paypal.com/paypalme/${paypalId}/${amount}`;

  const handleVenmoClick = () => {
    if (isMobile) {
      window.location.href = venmoAppUrl;
      // Fallback to web profile if app is not installed
      setTimeout(() => {
        window.location.href = venmoUrl;
      }, 250);
    } else {
      window.open(venmoUrl, '_blank');
    }
  };

  return (
    <div className="flex flex-col items-center space-y-4">
      <div className="flex space-x-4">
        <Button onClick={handleVenmoClick} className="bg-[#008CFF] hover:bg-[#0073cc] text-white">
          {venmoCopy}
        </Button>
        <Button onClick={() => window.open(paypalUrl, '_blank')} className="bg-[#003087] hover:bg-[#002464] text-white">
          {paypalCopy}
        </Button>
      </div>
      {!isMobile && (
        <div className="p-4 bg-white rounded-lg shadow-md">
          <p className="text-center mb-2">Scan to pay with Venmo</p>
          <QRCodeSVG value={venmoUrl} size={128} />
        </div>
      )}
    </div>
  );
};