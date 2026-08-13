'use client';

import React, { useState } from 'react';
import { GitBranch, Plus, CheckCircle2, AlertTriangle, Clock } from 'lucide-react';

export default function BuildsPage() {
  const [builds] = useState([
    { build_id: 'BUILD-1042', git_sha: 'a8f3b9c', branch: 'main', registered_at: '2026-08-13 18:30', status: 'STABLE', test_count: 36, pass_rate: '100%' },
    { build_id: 'BUILD-1041', git_sha: '7c2d1e0', branch: 'feature/npu-optimization', registered_at: '2026-08-12 14:15', status: 'DEGRADED', test_count: 36, pass_rate: '97.2%' },
    { build_id: 'BUILD-1040', git_sha: '5b9a8f2', branch: 'main', registered_at: '2026-08-11 09:45', status: 'STABLE', test_count: 36, pass_rate: '100%' },
  ]);

  return (
    <div className="space-y-6 font-sans">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-800 pb-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white font-mono flex items-center gap-3">
            <GitBranch className="text-blue-400" size={24} /> BUILD & FIRMWARE CATALOG
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Registered software artifacts, firmware images, and targeted build validation history.
          </p>
        </div>

        <button className="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg font-mono text-xs font-bold flex items-center gap-2 shadow-lg shadow-blue-500/20">
          <Plus size={16} /> Register Firmware Build
        </button>
      </div>

      <div className="bg-[#0f172a] border border-gray-800 rounded-xl overflow-hidden shadow-2xl">
        <table className="w-full text-left font-mono text-xs">
          <thead className="bg-[#090d16] text-gray-400 border-b border-gray-800">
            <tr>
              <th className="p-4">BUILD ID</th>
              <th className="p-4">GIT SHA</th>
              <th className="p-4">BRANCH</th>
              <th className="p-4">REGISTERED</th>
              <th className="p-4">TEST SUITES</th>
              <th className="p-4">PASS RATE</th>
              <th className="p-4">STATUS</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/60">
            {builds.map((b) => (
              <tr key={b.build_id} className="hover:bg-gray-900/60 transition-colors">
                <td className="p-4 font-bold text-white">{b.build_id}</td>
                <td className="p-4 text-blue-400 font-bold">{b.git_sha}</td>
                <td className="p-4 text-gray-300">{b.branch}</td>
                <td className="p-4 text-gray-400">{b.registered_at}</td>
                <td className="p-4 text-gray-300">{b.test_count} Tests</td>
                <td className="p-4 text-emerald-400 font-bold">{b.pass_rate}</td>
                <td className="p-4">
                  <span className={`px-2.5 py-1 rounded text-[11px] font-bold ${
                    b.status === 'STABLE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                  }`}>
                    {b.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
