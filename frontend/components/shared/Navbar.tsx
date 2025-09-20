'use client';

import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { usePathname } from 'next/navigation';

const adminNavLinks = [
  { href: '/dashboard', label: 'Search Connections' },
  { href: '/data-management', label: 'Upload Connections' },
  { href: '/warm-intro-requests', label: 'Warm Intro Requests' },
  { href: '/admin/follow-ups', label: 'Follow-Up Emails' },
  { href: '/access-requests', label: 'Access Requests' },
];

const userNavLinks: { href: string; label: string }[] = [
  // End users see no navigation links - they only get the dashboard search functionality
];

export function Navbar() {
  const { logout, user } = useAuth();
  const pathname = usePathname();

  // Determine which navigation links to show based on user role
  const navLinks = user?.role === 'admin' ? adminNavLinks : userNavLinks;

  return (
    <nav className="bg-white border-b shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <Link href="/dashboard" className="font-bold text-xl">
              Superconnect AI
            </Link>
            {navLinks.length > 0 && (
              <div className="hidden md:flex items-center space-x-4">
                {navLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`px-3 py-2 rounded-md text-sm font-medium ${
                      pathname === link.href
                        ? 'bg-gray-100 text-gray-900'
                        : 'text-gray-500 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                  >
                    {link.label}
                  </Link>
                ))}
              </div>
            )}
          </div>
          <div className="flex items-center space-x-3">
            {user?.role && (
              <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                {user.role === 'admin' ? 'Admin' : 'User'}
              </span>
            )}
            <Button onClick={logout} variant="ghost" size="sm">
              Logout
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}