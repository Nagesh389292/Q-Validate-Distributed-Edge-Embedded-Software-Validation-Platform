'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Cpu,
  Server,
  GitBranch,
  PlayCircle,
  Activity,
  Layers,
  GitPullRequest,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Zap,
  Radio,
  FileText,
  Skull
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
  badge?: string;
}

interface NavGroup {
  group: string;
  items: NavItem[];
}

const navGroups: NavGroup[] = [
  {
    group: 'COMMAND CENTER',
    items: [
      { name: 'Overview', href: '/', icon: LayoutDashboard }
    ]
  },
  {
    group: 'DEVICE ENGINEERING',
    items: [
      { name: 'Device Lab', href: '/devices', icon: Cpu },
      { name: 'Device Farm', href: '/farm', icon: Server, badge: '100 Nodes' }
    ]
  },
  {
    group: 'VALIDATION',
    items: [
      { name: 'Builds', href: '/builds', icon: GitBranch },
      { name: 'Test Catalog', href: '/test-cases', icon: PlayCircle },
      { name: 'Test Runs', href: '/test-runs', icon: Activity },
      { name: 'Regression / TIA', href: '/tia', icon: GitPullRequest }
    ]
  },
  {
    group: 'DISTRIBUTED SYSTEM',
    items: [
      { name: 'Go Scheduler', href: '/scheduler', icon: Layers },
      { name: 'Performance Lab', href: '/benchmarks', icon: Zap, badge: '42.3 TPS' }
    ]
  },
  {
    group: 'DIAGNOSTICS & OBS',
    items: [
      { name: 'Defect Triage', href: '/defects', icon: AlertTriangle, badge: '1 Open' },
      { name: 'OTel Traces', href: '/observability', icon: Radio },
      { name: 'System Health', href: '/health', icon: ShieldCheck },
      { name: 'Resilience Lab', href: '/resilience', icon: Skull, badge: 'CHAOS' }
    ]
  }
];

export default function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState<boolean>(false);

  useEffect(() => {
    const savedState = localStorage.getItem('qvalidate_sidebar_collapsed');
    if (savedState !== null) {
      setCollapsed(JSON.parse(savedState));
    }
  }, []);

  const toggleSidebar = () => {
    const nextState = !collapsed;
    setCollapsed(nextState);
    localStorage.setItem('qvalidate_sidebar_collapsed', JSON.stringify(nextState));
  };

  return (
    <motion.aside
      animate={{ width: collapsed ? 76 : 260 }}
      transition={{ duration: 0.2, ease: 'easeInOut' }}
      className="h-screen sticky top-0 z-40 bg-[#0d121f] border-r border-gray-800/80 flex flex-col justify-between select-none shadow-2xl"
    >
      {/* Brand Header */}
      <div>
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-800/60">
          <Link href="/" className="flex items-center gap-3 overflow-hidden">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white font-extrabold text-lg shadow-lg shadow-blue-500/20 shrink-0">
              Q
            </div>
            <AnimatePresence>
              {!collapsed && (
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -10 }}
                  className="flex flex-col whitespace-nowrap"
                >
                  <span className="font-extrabold text-base tracking-wider bg-gradient-to-r from-white via-gray-200 to-blue-400 bg-clip-text text-transparent">
                    Q-VALIDATE
                  </span>
                  <span className="text-[10px] font-mono text-blue-400/80 tracking-widest uppercase">
                    Command Center
                  </span>
                </motion.div>
              )}
            </AnimatePresence>
          </Link>
          <button
            onClick={toggleSidebar}
            className="p-1.5 rounded-md hover:bg-gray-800/80 text-gray-400 hover:text-white transition-colors"
            title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          </button>
        </div>

        {/* Navigation Group Items */}
        <div className="py-4 px-2 space-y-6 overflow-y-auto max-h-[calc(100vh-140px)] custom-scrollbar">
          {navGroups.map((group, gIdx) => (
            <div key={gIdx} className="space-y-1">
              {!collapsed && (
                <div className="px-3 text-[10px] font-bold font-mono text-gray-500 tracking-wider uppercase mb-2">
                  {group.group}
                </div>
              )}
              {group.items.map((item) => {
                const isActive = pathname === item.href;
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center justify-between px-3 py-2 rounded-lg transition-all text-sm font-medium group relative ${
                      isActive
                        ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-inner'
                        : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
                    }`}
                  >
                    <div className="flex items-center gap-3 overflow-hidden">
                      <Icon
                        size={20}
                        className={`shrink-0 transition-transform ${
                          isActive ? 'text-blue-400 scale-110' : 'text-gray-400 group-hover:text-gray-200'
                        }`}
                      />
                      <AnimatePresence>
                        {!collapsed && (
                          <motion.span
                            initial={{ opacity: 0, x: -5 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -5 }}
                            className="whitespace-nowrap truncate"
                          >
                            {item.name}
                          </motion.span>
                        )}
                      </AnimatePresence>
                    </div>

                    {!collapsed && item.badge && (
                      <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-gray-800 text-blue-300 border border-gray-700">
                        {item.badge}
                      </span>
                    )}

                    {/* Tooltip for collapsed mode */}
                    {collapsed && (
                      <div className="absolute left-full ml-2 px-2.5 py-1 bg-gray-900 text-gray-200 text-xs font-semibold rounded-md shadow-xl whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50 border border-gray-800">
                        {item.name}
                      </div>
                    )}
                  </Link>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Footer Profile / Version Indicator */}
      <div className="p-3 border-t border-gray-800/60 bg-[#090d16]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shrink-0" />
            {!collapsed && (
              <div className="flex flex-col whitespace-nowrap overflow-hidden">
                <span className="text-xs font-semibold text-gray-300">System v2.4.0</span>
                <span className="text-[10px] font-mono text-gray-500">Qualcomm Edition</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.aside>
  );
}
