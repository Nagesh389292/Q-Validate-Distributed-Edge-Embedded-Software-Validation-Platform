'use client';

import React from 'react';
import { Layers, Server, Cpu, Activity, Clock, CheckCircle2, ArrowRight } from 'lucide-react';

export default function SchedulerPage() {
  return (
    <div className="space-y-6 font-sans">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-800 pb-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white font-mono flex items-center gap-3">
            <Layers className="text-cyan-400" size={24} /> GO DISTRIBUTED SCHEDULER & QUEUE MONITOR
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Priority-based, capability-aware test task scheduler microservice written in Go with Kafka event integration.
          </p>
        </div>

        <span className="px-3 py-1 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-mono font-bold rounded-lg flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" /> Go Microservice Active
        </span>
      </div>

      {/* Execution Pipeline Topology Box */}
      <div className="bg-[#0f172a] border border-gray-800 rounded-xl p-6 shadow-2xl space-y-4">
        <h3 className="text-xs font-mono font-bold text-gray-400 uppercase tracking-wider">
          SCHEDULING PIPELINE ARCHITECTURE
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-6 gap-3 text-center font-mono text-xs">
          <div className="bg-gray-900 border border-blue-500/30 p-3 rounded-lg">
            <div className="text-[10px] text-blue-400 font-bold">1. KAFKA QUEUE</div>
            <div className="text-white font-bold mt-1">Depth: 0 Jobs</div>
          </div>

          <div className="bg-gray-900 border border-purple-500/30 p-3 rounded-lg">
            <div className="text-[10px] text-purple-400 font-bold">2. GO SCHEDULER</div>
            <div className="text-white font-bold mt-1">Priority Rank</div>
          </div>

          <div className="bg-gray-900 border border-cyan-500/30 p-3 rounded-lg">
            <div className="text-[10px] text-cyan-400 font-bold">3. CAPABILITY MATCH</div>
            <div className="text-white font-bold mt-1">ARM / DSP / NPU</div>
          </div>

          <div className="bg-gray-900 border border-emerald-500/30 p-3 rounded-lg">
            <div className="text-[10px] text-emerald-400 font-bold">4. ATOMIC LOCK</div>
            <div className="text-white font-bold mt-1">UPDATE Reserved=1</div>
          </div>

          <div className="bg-gray-900 border border-indigo-500/30 p-3 rounded-lg">
            <div className="text-[10px] text-indigo-400 font-bold">5. WORKER POOL</div>
            <div className="text-white font-bold mt-1">10 Parallel Threads</div>
          </div>

          <div className="bg-gray-900 border border-emerald-500/30 p-3 rounded-lg">
            <div className="text-[10px] text-emerald-400 font-bold">6. C++ RUNTIME</div>
            <div className="text-white font-bold mt-1">gRPC Execution</div>
          </div>
        </div>
      </div>

      {/* Queue Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono">
        <div className="bg-[#0f172a] border border-gray-800 p-5 rounded-xl">
          <div className="text-xs text-gray-400">ACTIVE WORKER UTILIZATION</div>
          <div className="text-3xl font-extrabold text-emerald-400 mt-2">10 / 10 Workers</div>
          <div className="text-[11px] text-emerald-500 mt-1">100% Operational Capacity</div>
        </div>

        <div className="bg-[#0f172a] border border-gray-800 p-5 rounded-xl">
          <div className="text-xs text-gray-400">AVERAGE SCHEDULING LATENCY</div>
          <div className="text-3xl font-extrabold text-blue-400 mt-2">0.42 ms</div>
          <div className="text-[11px] text-blue-500 mt-1">Go Parallel Lock Time</div>
        </div>

        <div className="bg-[#0f172a] border border-gray-800 p-5 rounded-xl">
          <div className="text-xs text-gray-400">TASK DEDUPLICATION / IDEMPOTENCY</div>
          <div className="text-3xl font-extrabold text-purple-400 mt-2">100% Active</div>
          <div className="text-[11px] text-purple-500 mt-1">Kafka Payload Guard Enabled</div>
        </div>
      </div>
    </div>
  );
}
