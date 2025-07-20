'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Users, Settings } from 'lucide-react';

const navLinks = [
  { href: '/', label: 'Dashboard', icon: Home },
  { href: '/clients', label: 'Clients', icon: Users },
  { href: '/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-slate-800 text-white flex flex-col">
      <div className="p-6">
        <h1 className="text-2xl font-bold">Trading Co.</h1>
      </div>
      <nav className="flex-1 px-4">
        <ul>
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <li key={link.href}>
                <Link href={link.href} className={`flex items-center space-x-3 p-3 rounded-lg transition-colors ${
                    isActive ? 'bg-slate-700' : 'hover:bg-slate-700/50'
                  }`}>
                  
                    <link.icon className="h-5 w-5" />
                    <span>{link.label}</span>
                  
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
      <div className="p-4 border-t border-slate-700">
        {/* User profile section can go here */}
      </div>
    </aside>
  );
}
