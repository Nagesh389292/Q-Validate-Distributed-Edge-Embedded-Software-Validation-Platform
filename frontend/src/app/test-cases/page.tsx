'use client';

import React from 'react';
import { PlayCircle, Cpu, HardDrive, Zap, ShieldCheck } from 'lucide-react';

export default function TestCasesPage() {
  const tests = [
    { id: 'BOOT-001', name: 'Cold Boot Sanity Check', capability: 'CPU', category: 'Sanity', duration: '200ms', priority: 'P0' },
    { id: 'MEM-003', name: 'Dynamic Memory Allocation', capability: 'MEMORY', category: 'Stress', duration: '331ms', priority: 'P0' },
    { id: 'CPU-007', name: 'Multicore Load Stress', capability: 'CPU', category: 'Performance', duration: '145ms', priority: 'P1' },
    { id: 'DSP-012', name: 'Hexagon DSP FFT Processing', capability: 'DSP', category: 'Functional', duration: '321ms', priority: 'P1' },
    { id: 'AI-045', name: 'ResNet-50 Neural Inference', capability: 'AI_ACCELERATOR', category: 'ML Inference', duration: '871ms', priority: 'P0' },
    { id: 'NET-202', name: 'gRPC IPC Bandwidth Sanity', capability: 'NETWORK', category: 'Integration', duration: '256ms', priority: 'P2' },
  ];

  return (
    <div className="space-y-6 font-sans">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-800 pb-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white font-mono flex items-center gap-3">
            <PlayCircle className="text-blue-400" size={24} /> TEST CASE & SUITE CATALOG
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Automated validation test cases with hardware capability requirements and target execution criteria.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {tests.map(t => (
          <div key={t.id} className="bg-[#0f172a] border border-gray-800 rounded-xl p-5 shadow-xl space-y-3 font-mono">
            <div className="flex items-center justify-between">
              <span className="text-sm font-bold text-white">{t.id}</span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                {t.priority}
              </span>
            </div>

            <div className="text-xs font-semibold text-gray-200">{t.name}</div>

            <div className="pt-3 border-t border-gray-800/60 flex items-center justify-between text-[11px] text-gray-400">
              <span>Capability: <strong className="text-gray-200">{t.capability}</strong></span>
              <span className="text-emerald-400">{t.duration}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
