'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Search, 
  Users, 
  MessageCircle, 
  Zap, 
  Shield, 
  Star,
  ArrowRight,
  CheckCircle,
  Network,
  Brain,
  Target
} from 'lucide-react';

export default function LandingPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const handleGetStarted = async () => {
    setIsLoading(true);
    // Add a small delay for better UX
    setTimeout(() => {
      router.push('/login');
    }, 500);
  };

  const features = [
    {
      icon: <Brain className="h-6 w-6" />,
      title: "AI-Powered Search",
      description: "Use natural language to find exactly who you're looking for in Ha's extensive network"
    },
    {
      icon: <Target className="h-6 w-6" />,
      title: "Smart Matching",
      description: "Get relevance scores and detailed analysis of why each connection might be perfect"
    },
    {
      icon: <MessageCircle className="h-6 w-6" />,
      title: "Warm Introductions",
      description: "Request personalized introductions with context that increases your success rate"
    },
    {
      icon: <Network className="h-6 w-6" />,
      title: "Extensive Network",
      description: "Access to thousands of first-degree LinkedIn connections across industries and roles"
    }
  ];

  const benefits = [
    "Find VCs, advisors, and industry experts instantly",
    "Get warm introductions that can actually help you",
    "Access Ha's curated professional network",
    "Connect with professionals who are hiring or open to work"
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <Network className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">Superconnect AI</span>
            </div>
            <Button
              variant="outline"
              onClick={() => router.push('/login')}
              className="border-blue-200 text-blue-700 hover:bg-blue-50 cursor-pointer"
            >
              Sign In
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-20 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <Badge className="mb-4 bg-blue-100 text-blue-800 hover:bg-blue-100">
              <Zap className="h-3 w-3 mr-1" />
              AI-Powered Professional Networking
            </Badge>
            
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
              Unlock the Power of
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
                {" "}Ha's Network
              </span>
            </h1>
            
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
              Search thousands of professional connections using natural language. 
              Get AI-powered match analysis and request warm introductions that can actually help you.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <Button
                size="lg"
                onClick={handleGetStarted}
                disabled={isLoading}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-8 py-3 text-lg cursor-pointer disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Loading...
                  </>
                ) : (
                  <>
                    Get Started
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </>
                )}
              </Button>
              
              <div className="flex items-center text-sm text-gray-500">
                <Shield className="h-4 w-4 mr-1" />
                Invitation-only access
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-2xl mx-auto">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-1">15K+</div>
                <div className="text-sm text-gray-600">Professional Connections</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-indigo-600 mb-1">95%</div>
                <div className="text-sm text-gray-600">Introduction Success Rate</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600 mb-1">24h</div>
                <div className="text-sm text-gray-600">Average Response Time</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              How Superconnect AI Works
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Intelligent networking powered by AI, designed to make meaningful connections effortless
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
                <CardHeader className="text-center pb-4">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-100 to-indigo-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <div className="text-blue-600">
                      {feature.icon}
                    </div>
                  </div>
                  <CardTitle className="text-lg font-semibold text-gray-900">
                    {feature.title}
                  </CardTitle>
                </CardHeader>
                <CardContent className="text-center">
                  <CardDescription className="text-gray-600 leading-relaxed">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6">
                Why Choose Superconnect AI?
              </h2>
              <p className="text-lg text-gray-600 mb-8">
                Stop wasting time on cold outreach. Get warm introductions to the right people 
                at the right time with AI-powered precision.
              </p>
              
              <div className="space-y-4">
                {benefits.map((benefit, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <CheckCircle className="h-6 w-6 text-green-500 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700 font-medium">{benefit}</span>
                  </div>
                ))}
              </div>

              <Button
                size="lg"
                onClick={handleGetStarted}
                disabled={isLoading}
                className="mt-8 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white cursor-pointer disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Loading...
                  </>
                ) : (
                  <>
                    Start Networking Smarter
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </div>

            <div className="relative">
              <div className="bg-white rounded-2xl shadow-2xl p-8">
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <Search className="h-5 w-5 text-blue-600" />
                    <span className="text-sm font-medium text-gray-900">Search Query</span>
                  </div>
                  <div className="bg-blue-50 border-2 border-dashed border-blue-200 rounded-lg p-4 relative">
                    <div className="absolute -top-2 left-3 bg-blue-100 px-2 py-0.5 rounded text-xs text-blue-700 font-medium">
                      Example Query
                    </div>
                    <p className="text-sm text-blue-800 italic font-medium">
                      "Find me a VC who invests in seed stage consumer startups"
                    </p>
                  </div>
                  
                  <div className="flex items-center space-x-3 pt-4">
                    <Users className="h-5 w-5 text-green-600" />
                    <span className="text-sm font-medium text-gray-900">AI Match Results</span>
                  </div>
                  <div className="space-y-3">
                    <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium text-gray-900">Sarah Chen</span>
                        <Badge className="bg-green-100 text-green-800">
                          <Star className="h-3 w-3 mr-1" />
                          Top Match
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-600 mt-1">Partner at Accel, focuses on consumer startups</p>
                    </div>
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium text-gray-900">Mike Rodriguez</span>
                        <Badge variant="secondary">Score: 8.5</Badge>
                      </div>
                      <p className="text-xs text-gray-600 mt-1">Seed investor at Bessemer Ventures</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-indigo-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
            Ready to Supercharge Your Network?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Join the exclusive community of professionals who are networking smarter, not harder.
          </p>
          
          <Button
            size="lg"
            onClick={handleGetStarted}
            disabled={isLoading}
            className="bg-white text-blue-600 hover:bg-blue-50 hover:text-blue-700 hover:shadow-lg hover:scale-105 px-8 py-3 text-lg font-semibold cursor-pointer disabled:cursor-not-allowed transition-all duration-200 transform"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                Loading...
              </>
            ) : (
              <>
                Get Started Today
                <ArrowRight className="ml-2 h-5 w-5" />
              </>
            )}
          </Button>
          
          <p className="text-sm text-blue-200 mt-4">
            Invitation-only access • Powered by Ha's professional network
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <div className="w-6 h-6 bg-gradient-to-r from-blue-400 to-indigo-400 rounded-md flex items-center justify-center">
                <Network className="h-4 w-4 text-white" />
              </div>
              <span className="text-lg font-bold">Superconnect AI</span>
            </div>
            <p className="text-gray-400 text-sm">
              © 2025 Superconnect AI. Intelligently connecting professionals worldwide.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}