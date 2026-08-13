'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Search,
  LayoutDashboard,
  Cpu,
  Server,
  Zap,
  GitBranch,
  PlayCircle,
  Activity,
  Layers,
  GitPullRequest,
  AlertTriangle,
  Radio,
  ShieldCheck,
  ArrowRight,
  X
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const router = useRouter();
  const [query, setQuery] = useState<string>('');

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
        else {
          // Open triggered
        }
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const items = [
    { title: 'Overview Dashboard', category: 'Navigation', href: '/', icon: LayoutDashboard },
    { title: 'Device Lab & Fault Injection', category: 'Navigation', href: '/devices', icon: Cpu },
    { title: 'Device Farm Manager (100 Nodes)', category: 'Navigation', href: '/farm', icon: Server },
    { title: 'Performance Lab & Scalability Benchmarks', category: 'Navigation', href: '/benchmarks', icon: Zap },
    { title: 'Builds & Firmware Catalog', category: 'Navigation', href: '/builds', icon: GitBranch },
    { title: 'Test Cases & Suite Catalog', category: 'Navigation', href: '/test-cases', icon: PlayCircle },
    { title: 'Test Runs & Monitor', category: 'Navigation', href: '/test-runs', icon: Activity },
    { title: 'Distributed Go Scheduler Queue', category: 'Navigation', href: '/scheduler', icon: Layers },
    { title: 'Test Impact Analysis (TIA)', category: 'Navigation', href: '/tia', icon: GitPullRequest },
    { title: 'Defect Triage Studio', category: 'Navigation', href: '/defects', icon: AlertTriangle },
    { title: 'OpenTelemetry Trace Inspector', category: 'Navigation', href: '/observability', icon: Radio },
    { title: 'Infrastructure & System Health', category: 'Navigation', href: '/health', icon: ShieldCheck },
  ];

  const filtered = items.filter(item =>
    item.title.toLowerCase().includes(query.toLowerCase()) ||
    item.category.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelect = (href: string) => {
    router.push(href);
    onClose();
    setQuery('');
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-start justify-center pt-24 px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: -10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: -10 }}
          transition={{ duration: 0.15 }}
          className="w-full max-w-2xl bg-[#0f172a] border border-gray-800 rounded-xl shadow-2xl overflow-hidden font-sans"
        >
          {/* Input Header */}
          <div className="flex items-center px-4 py-3 border-b border-gray-800 bg-[#090d16]">
            <Search size={18} className="text-gray-400 mr-3 shrink-0" />
            <input
              type="text"
              autoFocus
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type a command or search view..."
              className="flex-1 bg-transparent border-none outline-none text-sm text-gray-200 placeholder-gray-500 font-medium"
            />
            <button
              onClick={onClose}
              className="p-1 rounded text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
            >
              <X size={16} />
            </button>
          </div>

          {/* List Results */}
          <div className="max-h-96 overflow-y-auto p-2 space-y-1 custom-scrollbar">
            {filtered.length === 0 ? (
              <div className="p-8 text-center text-xs text-gray-500 font-mono">
                No matching views or commands found for "{query}"
              </div>
            ) : (
              filtered.map((item, idx) => {
                const Icon = item.icon;
                return (
                  <button
                    key={idx}
                    onClick={() => handleSelect(item.href)}
                    className="w-full flex items-center justify-between px-3 py-2.5 rounded-lg hover:bg-blue-600/15 hover:border-blue-500/30 border border-transparent text-left transition-all group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-md bg-gray-900 border border-gray-800 text-gray-400 group-hover:text-blue-400 group-hover:border-blue-500/40 transition-colors">
                        <Icon size={16} />
                      </div>
                      <div>
                        <div className="text-xs font-semibold text-gray-200 group-hover:text-white">
                          {item.title}
                        </div>
                        <div className="text-[10px] font-mono text-gray-500">
                          {item.category} • {item.href}
                        </div>
                      </div>
                    </div>

                    <ArrowRight size={14} className="text-gray-600 group-hover:text-blue-400 transition-colors" />
                  </button>
                );
              })
            )}
          </div>

          {/* Footer Shortcuts */}
          <div className="px-4 py-2 bg-[#090d16] border-t border-gray-800 flex items-center justify-between text-[11px] font-mono text-gray-500">
            <span>Navigation Command Palette</span>
            <div className="flex items-center gap-3">
              <span><kbd className="bg-gray-800 px-1 rounded">↑↓</kbd> Navigate</span>
              <span><kbd className="bg-gray-800 px-1 rounded">Enter</kbd> Select</span>
              <span><kbd className="bg-gray-800 px-1 rounded">Esc</kbd> Close</span>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
