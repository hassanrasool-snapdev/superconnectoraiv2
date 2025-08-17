'use client';

import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { TippingControl } from './TippingControl';
import { Connection } from '@/lib/types';

interface TippingModalProps {
  isOpen: boolean;
  onClose: () => void;
  connection: Connection | null;
}

export function TippingModal({ isOpen, onClose, connection }: TippingModalProps) {
  if (!isOpen) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Support Superconnect AI</DialogTitle>
        </DialogHeader>
        <TippingControl
          venmoId="pokergirlha"
          paypalId="pokergirlha"
          amount={20}
        />
      </DialogContent>
    </Dialog>
  );
}