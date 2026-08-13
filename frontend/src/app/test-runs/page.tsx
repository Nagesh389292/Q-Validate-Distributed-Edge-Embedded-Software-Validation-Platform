'use client';

import React, { useState } from 'react';
import { Activity, Play, CheckCircle2, AlertTriangle, Clock, Server, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

export default function TestRunsPage() {
  const [runs] = useState([
    { run_id: 'RUN-DIST-0697B7', suite_id: 'SUITE-DISTRIBUTED', build_id: 'BUILD-1042', mode: 'PARALLEL', total: 50, passed: 50, failed: 0, status: 'PASSED', duration: '1.246s', tps: '40.13 TPS' },
    { run_id: 'RUN-DIST-06B693', suite_id: 'SUITE-STRESS-50', build_id: 'BUILD-1042', mode: 'PARALLEL', total: 50, passed: 50, failed: 0, status: 'PASSED', duration: '1.760s', tps: '28.41 TPS' },
    { run_id: 'RUN-DIST-045A91', suite_id: 'SUITE-SANITY', build_id: 'BUILD-1041', mode: 'PARALLEL', total: 36, passed: 35, failed: 1, status: 'FAILED', duration: '2.118s', tps: '17.00 TPS' },
  ]);

  return (
    <div className="space-y-6 font-sans">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-800 pb-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white font-mono flex items-center gap-3">
            <Activity className="text-blue-400" size={24} /> VALIDATION TEST RUN MONITOR
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Real-time parallel execution monitor for distributed worker pool test runs.
          </p>
        </div>

        <button className="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg font-mono text-xs font-bold flex items-center gap-2 shadow-lg shadow-blue-500/20">
          <Play size={15} /> Execute Test Run
        </button>
      </div>

      <div className="space-y-4">
        {runs.map(r => (
          <div key={r.run_id} className="bg-[#0f172a] border border-gray-800 rounded-xl p-5 shadow-xl space-y-4 font-mono">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-gray-800/80 pb-3">
              <div className="flex items-center gap-3">
                <span className="text-base font-bold text-white">{r.run_id}</span>
                <span className="text-xs text-blue-400 bg-blue-500/10 px-2.5 py-0.5 rounded border border-blue-500/20">{r.suite_id}</span>
                <span className="text-xs text-gray-400">Build: {r.build_id}</span>
              </div>

              <span className={`px-3 py-1 rounded text-xs font-bold ${
                r.status === 'PASSED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'
              }`}>
                {r.status}
              </span>
            </div>

            {/* Pipeline Stage Bar */}
            <div className="flex items-center gap-2 text-xs font-mono">
              <span className="text-gray-400">Pipeline Stages:</span>
              <div className="flex-1 grid grid-cols-5 gap-1.5 text-[10px] text-center">
                <div className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 p-1.5 rounded font-bold">QUEUED ✓</div>
                <div className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 p-1.5 rounded font-bold">ALLOCATED ✓</div>
                <div className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 p-1.5 rounded font-bold">RUNNING ✓</div>
                <div className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 p-1.5 rounded font-bold">VALIDATED ✓</div>
                <div className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 p-1.5 rounded font-bold">PASSED ✓</div>
              </div>
            </div>

            <div className="flex items-center justify-between text-xs text-gray-400 pt-2 border-t border-gray-800/60">
              <span>Execution: <strong>{r.duration}</strong> ({r.tps})</span>
              <span className="text-emerald-400 font-bold">{r.passed} / {r.total} Passed</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
