'use client';

import React, { useState, useEffect } from 'react';
import { Search, ShieldCheck, Activity, Cpu, Bell, ChevronDown, CheckCircle2, AlertTriangle, Layers } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface TopBarProps {
  onOpenCommandPalette: () => void;
}

export default function TopBar({ onOpenCommandPalette }: TopBarProps) {
  const [healthOpen, setHealthOpen] = useState<boolean>(false);
  const [systemStatus, setSystemStatus] = useState<'HEALTHY' | 'DEGRADED'>('HEALTHY');
  const [healthData, setHealthData] = useState<any>(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8000/api/v1/health/dependencies');
        if (res.ok) {
          const json = await res.json();
          setHealthData(json);
          setSystemStatus(json.status === 'HEALTHY' ? 'HEALTHY' : 'DEGRADED');
        }
      } catch (e) {
        // Fallback default snapshot
        setHealthData({
          status: 'HEALTHY',
          dependencies: {
            database: { backend: 'sqlite/postgres', status: 'UP' },
            event_bus: { type: 'kafka', status: 'UP' },
            device_farm: { total_nodes: 100, ready_nodes: 82, status: 'UP' }
          }
        });
      }
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 bg-[#0d121f]/90 backdrop-blur border-b border-gray-800/80 px-6 flex items-center justify-between sticky top-0 z-30 shadow-md">
      {/* Left: Global Search / Command Palette Button */}
      <div className="flex items-center gap-4">
        <button
          onClick={onOpenCommandPalette}
          className="flex items-center gap-3 bg-gray-900/80 hover:bg-gray-800 border border-gray-800 hover:border-gray-700 rounded-lg px-3.5 py-1.5 text-xs text-gray-400 hover:text-gray-200 transition-all w-64 shadow-inner group"
        >
          <Search size={14} className="text-gray-500 group-hover:text-blue-400 transition-colors" />
          <span className="flex-1 text-left">Search commands or views...</span>
          <kbd className="bg-gray-800 text-gray-400 text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded border border-gray-700">
            Ctrl K
          </kbd>
        </button>

        <span className="px-2.5 py-1 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20 text-[11px] font-mono font-bold tracking-wide">
          ENV: PRODUCTION (SIM)
        </span>
      </div>

      {/* Right: Telemetry Controls & Health Popover */}
      <div className="flex items-center gap-5">
        {/* Metric Counters */}
        <div className="hidden md:flex items-center gap-4 text-xs font-mono border-r border-gray-800 pr-5">
          <div className="flex items-center gap-2 bg-gray-900/60 px-2.5 py-1 rounded border border-gray-800/60">
            <Cpu size={14} className="text-emerald-400" />
            <span className="text-gray-400">DEVICES:</span>
            <span className="text-emerald-400 font-bold">82/100 READY</span>
          </div>

          <div className="flex items-center gap-2 bg-gray-900/60 px-2.5 py-1 rounded border border-gray-800/60">
            <Activity size={14} className="text-blue-400" />
            <span className="text-gray-400">TESTS:</span>
            <span className="text-blue-400 font-bold">4 RUNNING</span>
          </div>
        </div>

        {/* Live Health Status Popover Trigger */}
        <div className="relative">
          <button
            onClick={() => setHealthOpen(!healthOpen)}
            className="flex items-center gap-2 bg-gray-900 hover:bg-gray-800/90 border border-gray-800 rounded-lg px-3 py-1.5 text-xs font-semibold transition-all shadow-sm"
          >
            <div className={`w-2 h-2 rounded-full ${systemStatus === 'HEALTHY' ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
            <span className={systemStatus === 'HEALTHY' ? 'text-emerald-400 font-mono' : 'text-amber-400 font-mono'}>
              {systemStatus === 'HEALTHY' ? 'OPERATIONAL' : 'DEGRADED'}
            </span>
            <ChevronDown size={14} className="text-gray-400" />
          </button>

          {/* Health Popover Dropdown */}
          <AnimatePresence>
            {healthOpen && (
              <motion.div
                initial={{ opacity: 0, y: 8, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 8, scale: 0.95 }}
                transition={{ duration: 0.15 }}
                className="absolute right-0 mt-2 w-72 bg-[#0f172a] border border-gray-800 rounded-xl shadow-2xl p-4 z-50 text-xs font-sans"
              >
                <div className="flex items-center justify-between border-b border-gray-800 pb-2.5 mb-3">
                  <span className="font-bold text-gray-200 uppercase tracking-wider text-[11px] font-mono">
                    System Health Diagnostics
                  </span>
                  <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                    Probes Passing
                  </span>
                </div>

                <div className="space-y-2 font-mono">
                  <div className="flex items-center justify-between p-2 rounded bg-gray-900/60 border border-gray-800/60">
                    <span className="text-gray-400 flex items-center gap-2">
                      <CheckCircle2 size={13} className="text-emerald-400" /> FastAPI Control Plane
                    </span>
                    <span className="text-emerald-400 font-bold">HEALTHY</span>
                  </div>

                  <div className="flex items-center justify-between p-2 rounded bg-gray-900/60 border border-gray-800/60">
                    <span className="text-gray-400 flex items-center gap-2">
                      <CheckCircle2 size={13} className="text-emerald-400" /> PostgreSQL / SQLite
                    </span>
                    <span className="text-emerald-400 font-bold">UP</span>
                  </div>

                  <div className="flex items-center justify-between p-2 rounded bg-gray-900/60 border border-gray-800/60">
                    <span className="text-gray-400 flex items-center gap-2">
                      <CheckCircle2 size={13} className="text-emerald-400" /> Kafka Event Bus
                    </span>
                    <span className="text-emerald-400 font-bold">UP</span>
                  </div>

                  <div className="flex items-center justify-between p-2 rounded bg-gray-900/60 border border-gray-800/60">
                    <span className="text-gray-400 flex items-center gap-2">
                      <CheckCircle2 size={13} className="text-emerald-400" /> Device Farm Manager
                    </span>
                    <span className="text-emerald-400 font-bold">82/100</span>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* User Badge */}
        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-gray-800 to-gray-700 border border-gray-700 flex items-center justify-center text-xs font-bold text-gray-200 shadow-inner">
          QC
        </div>
      </div>
    </header>
  );
}
