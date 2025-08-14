'use client';

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { createTip } from '@/lib/api';
import { Connection } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';

interface TippingModalProps {
  isOpen: boolean;
  onClose: () => void;
  connection: Connection | null;
}

export function TippingModal({ isOpen, onClose, connection }: TippingModalProps) {
  const [amount, setAmount] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const { token } = useAuth();

  const handleSendTip = async () => {
    if (!token || !connection || !amount) {
      setError('Amount is required.');
      return;
    }

    try {
      await createTip(connection.id, parseFloat(amount), message, token);
      alert('Tip sent successfully!');
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send tip');
    }
  };

  if (!isOpen) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Send a Tip to {connection?.first_name} {connection?.last_name}</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <Label htmlFor="amount">Amount ($)</Label>
            <Input id="amount" type="number" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="e.g., 5.00" />
          </div>
          <div>
            <Label htmlFor="message">Message (Optional)</Label>
            <Input id="message" type="text" value={message} onChange={(e) => setMessage(e.target.value)} placeholder="For coffee!" />
          </div>
        </div>
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <DialogFooter>
          <Button onClick={handleSendTip}>Send Tip via Venmo</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}