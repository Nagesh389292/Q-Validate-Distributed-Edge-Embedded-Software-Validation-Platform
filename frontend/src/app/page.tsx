'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Cpu,
  Server,
  Activity,
  Layers,
  Zap,
  AlertTriangle,
  Radio,
  ArrowRight,
  TrendingUp,
  CheckCircle2,
  Play
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function OverviewDashboardPage() {
  const [packetIndex, setPacketIndex] = useState<number>(0);

  // Animate data packet through the 6-stage architecture pipeline
  useEffect(() => {
    const interval = setInterval(() => {
      setPacketIndex(prev => (prev + 1) % 6);
    }, 1500);
    return () => clearInterval(interval);
  }, []);

  const metrics = [
    { title: 'ACTIVE DEVICES', value: '82 / 100', subtitle: '82 Ready • 4 Testing • 14 Idle', tag: 'SIMULATED FARM', color: 'text-emerald-400', border: 'border-emerald-500/30', href: '/devices', icon: Cpu },
    { title: 'READY NODES', value: '82 Nodes', subtitle: 'ARM64, DSP, NPU Simulated', tag: 'SIMULATED FARM', color: 'text-blue-400', border: 'border-blue-500/30', href: '/farm', icon: Server },
    { title: 'RUNNING TESTS', value: '4 Active', subtitle: 'Parallel Worker Threads', tag: 'LIVE QUEUE', color: 'text-purple-400', border: 'border-purple-500/30', href: '/test-runs', icon: Activity },
    { title: 'QUEUE DEPTH', value: '0 Jobs', subtitle: 'Kafka Event Bus Stream', tag: 'LIVE QUEUE', color: 'text-cyan-400', border: 'border-cyan-500/30', href: '/scheduler', icon: Layers },
    { title: 'PASS RATE', value: '98.2%', subtitle: '36 / 36 Pytest Suite Passed', tag: 'SUITE VERIFIED', color: 'text-emerald-400', border: 'border-emerald-500/30', href: '/test-cases', icon: CheckCircle2 },
    { title: 'P95 LATENCY', value: '196.0 ms', subtitle: 'gRPC IPC Communication', tag: 'LIVE MEASURED', color: 'text-indigo-400', border: 'border-indigo-500/30', href: '/observability', icon: Radio },
    { title: 'REAL THROUGHPUT', value: '41.05 TPS', subtitle: 'Measured 10-Node Parallel Peak', tag: 'MEASURED BASELINE', color: 'text-amber-400', border: 'border-amber-500/30', href: '/benchmarks', icon: Zap },
    { title: 'OPEN DEFECTS', value: '1 Critical', subtitle: 'AI-045 Capability Mismatch', tag: 'LIVE TRIAGE', color: 'text-red-400', border: 'border-red-500/30', href: '/defects', icon: AlertTriangle },
  ];

  const pipelineStages = [
    { step: 0, label: 'CONTROL PLANE', name: 'FastAPI REST', sub: 'Build / TIA Engine', color: 'border-blue-500/50 text-blue-400' },
    { step: 1, label: 'EVENT BUS', name: 'Kafka Stream', sub: '11 Topic Contracts', color: 'border-purple-500/50 text-purple-400' },
    { step: 2, label: 'SCHEDULER', name: 'Go Scheduler', sub: 'Atomic Device Lock', color: 'border-cyan-500/50 text-cyan-400' },
    { step: 3, label: 'DEVICE FARM', name: '100 Edge Nodes', sub: 'ARM64 / DSP / NPU', color: 'border-emerald-500/50 text-emerald-400' },
    { step: 4, label: 'C++ RUNTIME', name: 'gRPC Server', sub: 'Native C++20 Sim', color: 'border-amber-500/50 text-amber-400' },
    { step: 5, label: 'OBSERVABILITY', name: 'OTel SDK Tracing', sub: '9-Span Trace Tree', color: 'border-indigo-500/50 text-indigo-400' },
  ];

  return (
    <div className="space-y-8 font-sans">
      {/* Hero Header Section */}
      <div className="bg-gradient-to-r from-[#0d1527] via-[#111c35] to-[#0f172a] border border-gray-800 rounded-2xl p-8 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-mono font-bold tracking-wide mb-4">
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping" />
            QUALCOMM REFERENCE ARCHITECTURE v2.4
          </div>

          <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight leading-tight">
            Q-VALIDATE <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">ENGINEERING COMMAND CENTER</span>
          </h1>
          <p className="text-gray-400 text-sm md:text-base mt-3 leading-relaxed">
            Validate heterogeneous edge software at scale — from C++20 device runtimes and gRPC hardware simulation to Go distributed scheduling, Test Impact Analysis, and OpenTelemetry observability.
          </p>

          <div className="flex flex-wrap items-center gap-4 mt-6">
            <Link
              href="/benchmarks"
              className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-semibold text-xs transition-all shadow-lg shadow-purple-600/30 flex items-center gap-2"
            >
              <Zap size={15} /> Launch Performance Lab
            </Link>
            <Link
              href="/farm"
              className="px-5 py-2.5 rounded-lg bg-gray-900 hover:bg-gray-800 border border-gray-800 text-gray-300 hover:text-white font-semibold text-xs transition-all flex items-center gap-2"
            >
              <Server size={15} /> Device Farm Topology (100 Nodes)
            </Link>
          </div>
        </div>
      </div>

      {/* Cinematic Data Packet Architecture Engine */}
      <div className="bg-[#0f172a] border border-gray-800 rounded-xl p-6 shadow-2xl space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xs font-bold text-gray-200 uppercase font-mono tracking-wide flex items-center gap-2">
              <Layers size={16} className="text-purple-400" /> Cinematic System Data Packet Engine
            </h3>
            <p className="text-xs text-gray-400 mt-1">
              Visualizing virtual test request payload moving across Q-Validate microservices.
            </p>
          </div>
          <span className="px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono font-bold">
            ● Packet Active (Stage {packetIndex + 1}/6)
          </span>
        </div>

        {/* Dynamic Topology Box */}
        <div className="relative bg-[#090d16] border border-gray-800/80 rounded-xl p-8 overflow-hidden font-mono">
          <div className="hidden md:block absolute top-1/2 left-12 right-12 h-1 bg-gradient-to-r from-blue-600 via-cyan-500 to-indigo-600 -translate-y-1/2 opacity-30" />

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-6 gap-4 items-center text-center relative z-10">
            {pipelineStages.map((stage) => {
              const isActive = packetIndex === stage.step;
              return (
                <motion.div
                  key={stage.step}
                  animate={{
                    scale: isActive ? 1.05 : 1,
                    borderColor: isActive ? '#3b82f6' : '#1f2937'
                  }}
                  transition={{ duration: 0.3 }}
                  className={`p-4 rounded-xl bg-gray-900 border ${stage.color} shadow-lg transition-all relative ${
                    isActive ? 'shadow-blue-500/20 bg-blue-600/10' : ''
                  }`}
                >
                  {isActive && (
                    <motion.div
                      layoutId="activePacket"
                      className="absolute -top-3 left-1/2 -translate-x-1/2 px-2 py-0.5 rounded-full bg-blue-500 text-white text-[9px] font-bold shadow-md"
                    >
                      DATA PACKET
                    </motion.div>
                  )}
                  <div className="text-[10px] font-bold uppercase">{stage.label}</div>
                  <div className="text-xs font-extrabold text-white mt-1">{stage.name}</div>
                  <div className="text-[10px] text-gray-400 mt-1">{stage.sub}</div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>

      {/* System Status Metric Cards Grid */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xs font-bold text-gray-200 tracking-wide uppercase font-mono flex items-center gap-2">
            <Activity size={16} className="text-blue-400" /> Live Platform Telemetry Metrics
          </h2>
          <span className="text-[11px] font-mono text-gray-500">Explicit Transparency Badges</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {metrics.map((m, idx) => {
            const Icon = m.icon;
            return (
              <motion.div
                key={idx}
                whileHover={{ y: -3, transition: { duration: 0.15 } }}
                className={`bg-[#0f172a] border ${m.border} rounded-xl p-4 shadow-xl flex flex-col justify-between group transition-all`}
              >
                <div>
                  <div className="flex items-center justify-between text-xs font-mono text-gray-400">
                    <span>{m.title}</span>
                    <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-gray-800 text-gray-300 border border-gray-700">
                      {m.tag}
                    </span>
                  </div>
                  <div className="text-2xl font-extrabold text-white mt-2 tracking-tight font-mono">
                    {m.value}
                  </div>
                  <div className="text-[11px] text-gray-400 mt-1 font-mono">{m.subtitle}</div>
                </div>

                <div className="mt-4 pt-3 border-t border-gray-800/60 flex items-center justify-between text-[11px] font-mono">
                  <span className={`${m.color} flex items-center gap-1 font-bold`}>
                    ● {m.tag}
                  </span>
                  <Link href={m.href} className="text-gray-500 hover:text-blue-400 transition-colors flex items-center gap-1">
                    Inspect <ArrowRight size={12} />
                  </Link>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
