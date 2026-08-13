'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Cpu, GitBranch, PlayCircle, GitPullRequest, AlertTriangle, Activity, Server, Layers } from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Device Lab', href: '/devices', icon: Cpu },
    { name: 'Farm Manager', href: '/farm', icon: Server },
    { name: 'Builds', href: '/builds', icon: GitBranch },
    { name: 'Test Catalog', href: '/test-cases', icon: PlayCircle },
    { name: 'Test Runs', href: '/test-runs', icon: Activity },
    { name: 'Distributed Queue', href: '/scheduler', icon: Layers },
    { name: 'Observability', href: '/observability', icon: Activity },
    { name: 'TIA Engine', href: '/tia', icon: GitPullRequest },
    { name: 'Defect Triage', href: '/defects', icon: AlertTriangle },
    { name: 'Performance Lab', href: '/benchmarks', icon: Activity },
    { name: 'System Health', href: '/health', icon: Activity },
  ];

  return (
    <header className="border-b border-gray-800 bg-gray-900/90 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-white shadow-lg shadow-blue-500/20">
              Q
            </div>
            <div>
              <span className="font-extrabold text-lg tracking-tight text-white">Q-VALIDATE</span>
              <span className="ml-2 text-xs font-semibold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                v2.0 CONTROL PLANE
              </span>
            </div>
          </div>

          <nav className="flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/60'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
}
