'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Heart } from 'lucide-react';
import { TippingModal } from '@/components/shared/TippingModal';

export default function DonatePage() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleOpenModal = () => {
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-4">
            <Heart className="h-16 w-16 text-pink-500" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Help Keep Superconnector AI Alive
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Your support helps us maintain and improve our warm introduction service, 
            connecting professionals and fostering meaningful relationships.
          </p>
        </div>

        {/* CTA Button */}
        <div className="text-center mb-12">
          <Button
            onClick={handleOpenModal}
            size="lg"
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-8 py-4 text-lg font-semibold rounded-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
          >
            <Heart className="mr-2 h-5 w-5" />
            Support Superconnector AI
          </Button>
        </div>

        {/* Why Donate */}
        <Card>
          <CardHeader>
            <CardTitle>Why Your Support Matters</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">🚀 Platform Development</h4>
                <p className="text-gray-600">
                  Your donations help us continuously improve our AI algorithms and user experience.
                </p>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">💡 Infrastructure Costs</h4>
                <p className="text-gray-600">
                  We need to cover server costs, email services, and other operational expenses.
                </p>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">🤝 Community Growth</h4>
                <p className="text-gray-600">
                  Support helps us expand our network and create more valuable connections.
                </p>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">🔒 Privacy & Security</h4>
                <p className="text-gray-600">
                  Maintaining high security standards and protecting user data requires investment.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-12 text-gray-500">
          <p className="text-sm">
            Superconnector AI is committed to transparency and responsible use of donations.
          </p>
        </div>
      </div>

      {/* Tipping Modal */}
      <TippingModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        connection={null}
      />
    </div>
  );
}