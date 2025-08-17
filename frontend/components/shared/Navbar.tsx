'use client';

import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { usePathname } from 'next/navigation';

const navLinks = [
  { href: '/dashboard', label: 'Search Connections' },
  { href: '/data-management', label: 'Upload Connections' },
];

export function Navbar() {
  const { logout } = useAuth();
  const pathname = usePathname();

  return (
    <nav className="bg-white border-b shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <Link href="/dashboard" className="font-bold text-xl">
              Superconnect AI
            </Link>
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
          </div>
          <div className="flex items-center">
            <Button onClick={logout} variant="ghost" size="sm">
              Logout
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}