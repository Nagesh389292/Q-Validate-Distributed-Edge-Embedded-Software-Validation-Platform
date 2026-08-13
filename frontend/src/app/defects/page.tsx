'use client';

import React from 'react';
import { AlertTriangle, Radio, CheckCircle2, ArrowRight, ShieldAlert, Cpu } from 'lucide-react';

export default function DefectTriagePage() {
  const defects = [
    {
      id: 'DEF-1FBD6D',
      severity: 'CRITICAL',
      failed_test: 'AI-045 (ResNet-50 Inference)',
      device_id: 'DEVICE-003',
      trace_id: 'trace-a2277c0bb973',
      root_cause: 'Capability Mismatch — Hardware profile lacks NPU tensor core driver.',
      status: 'OPEN_TRIAGE',
      created_at: '2026-08-13 19:15'
    }
  ];

  return (
    <div className="space-y-6 font-sans">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-800 pb-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white font-mono flex items-center gap-3">
            <AlertTriangle className="text-amber-400" size={24} /> AUTOMATED DEFECT & DIAGNOSTIC TRIAGE
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Automated failure analysis linking test execution crashes directly to OpenTelemetry traces, telemetry logs, and root causes.
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {defects.map(d => (
          <div key={d.id} className="bg-[#0f172a] border border-amber-500/30 rounded-xl p-6 shadow-2xl space-y-5 font-mono">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3">
              <div className="flex items-center gap-3">
                <span className="text-lg font-bold text-white">{d.id}</span>
                <span className="px-2.5 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/20 text-xs font-bold">
                  {d.severity}
                </span>
              </div>
              <span className="text-xs text-amber-400 bg-amber-500/10 px-3 py-1 rounded border border-amber-500/20 font-bold">
                {d.status}
              </span>
            </div>

            {/* Interactive Timeline */}
            <div className="bg-gray-900 border border-gray-800 p-4 rounded-lg">
              <div className="text-[10px] text-gray-400 font-bold mb-3 uppercase">DIAGNOSTIC EVENT CORRELATION TIMELINE</div>
              <div className="grid grid-cols-1 sm:grid-cols-5 gap-2 text-center text-xs">
                <div className="p-2 rounded bg-red-500/10 text-red-400 border border-red-500/20">1. TEST FAILURE ({d.failed_test})</div>
                <div className="p-2 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">2. DEVICE ({d.device_id})</div>
                <div className="p-2 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">3. TRACE ({d.trace_id.slice(0, 10)})</div>
                <div className="p-2 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">4. LOG EXTRACTED</div>
                <div className="p-2 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">5. DEFECT GENERATED</div>
              </div>
            </div>

            <div className="bg-gray-900/60 p-4 rounded-lg border border-gray-800 text-xs space-y-1">
              <span className="text-gray-400 font-bold">AUTOMATED ROOT CAUSE DIAGNOSIS:</span>
              <p className="text-gray-200">{d.root_cause}</p>
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button className="px-4 py-2 bg-gray-900 hover:bg-gray-800 border border-gray-800 text-gray-300 text-xs font-bold rounded-lg">
                View Full Trace Logs
              </button>
              <button className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg shadow-md">
                Resolve & Re-run Validation
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
