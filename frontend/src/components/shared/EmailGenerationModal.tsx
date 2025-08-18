import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Connection } from '@/lib/types';
import { useAuth } from '@/context/AuthContext';
import { generateEmail } from '@/lib/api';

interface EmailGenerationModalProps {
  isOpen: boolean;
  onClose: () => void;
  connection: Connection | null;
}

export function EmailGenerationModal({ isOpen, onClose, connection }: EmailGenerationModalProps) {
  const { token } = useAuth();
  const [reason, setReason] = useState('');
  const [generatedEmail, setGeneratedEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleGenerateEmail = async () => {
    if (!connection || !token) return;
    setIsLoading(true);
    try {
      const email = await generateEmail(connection.id, reason, token);
      setGeneratedEmail(email.body);
    } catch (error) {
      console.error('Failed to generate email', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Generate Email</DialogTitle>
          <DialogDescription>
            Generate a personalized email to connect with {connection?.first_name} {connection?.last_name}.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="reason" className="text-right">
              Reason
            </Label>
            <Input
              id="reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="col-span-3"
            />
          </div>
          {generatedEmail && (
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="email-content" className="text-right">
                Email
              </Label>
              <Textarea
                id="email-content"
                value={generatedEmail}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setGeneratedEmail(e.target.value)}
                className="col-span-3 h-48"
              />
            </div>
          )}
        </div>
        <DialogFooter>
          <Button onClick={handleGenerateEmail} disabled={isLoading}>
            {isLoading ? 'Generating...' : 'Generate'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}