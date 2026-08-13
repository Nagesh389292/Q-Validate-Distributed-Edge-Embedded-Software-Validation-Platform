'use client';

import React, { useState } from 'react';
import { GitPullRequest, FileText, ArrowRight, Play, CheckCircle2, Shield } from 'lucide-react';
import { motion } from 'framer-motion';

export default function TIAStudioPage() {
  const [changedFile, setChangedFile] = useState<string>('MemoryManager.cpp');
  const [analyzed, setAnalyzed] = useState<boolean>(true);

  return (
    <div className="space-y-6 font-sans">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-800 pb-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white font-mono flex items-center gap-3">
            <GitPullRequest className="text-purple-400" size={24} /> TEST IMPACT ANALYSIS (TIA) STUDIO
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Analyze code commits to dynamically map affected software components and select minimal targeted regression suites.
          </p>
        </div>
      </div>

      <div className="bg-[#0f172a] border border-gray-800 rounded-xl p-6 shadow-2xl space-y-6">
        <div>
          <label className="text-xs font-mono font-bold text-gray-300 block mb-2">
            ENTER CHANGED SOURCE FILES (COMMITTED DIFF)
          </label>
          <div className="flex gap-3">
            <input
              type="text"
              value={changedFile}
              onChange={(e) => setChangedFile(e.target.value)}
              className="flex-1 bg-gray-900 border border-gray-800 rounded-lg px-4 py-2.5 text-xs font-mono text-gray-200 outline-none focus:border-blue-500"
              placeholder="e.g. MemoryManager.cpp, Firmware.hpp"
            />
            <button
              onClick={() => setAnalyzed(true)}
              className="px-5 py-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded-lg font-mono text-xs font-bold transition-all"
            >
              Analyze Impact
            </button>
          </div>
        </div>

        {analyzed && (
          <div className="space-y-6 pt-4 border-t border-gray-800">
            <h3 className="text-xs font-mono font-bold text-gray-400 uppercase tracking-wider">
              DYNAMIC CODE IMPACT MAP
            </h3>

            {/* Topology Map */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center font-mono">
              <div className="bg-gray-900 border border-blue-500/30 p-4 rounded-lg">
                <div className="text-[10px] text-blue-400 font-bold mb-1">SOURCE FILE</div>
                <div className="text-xs font-bold text-white">{changedFile}</div>
              </div>

              <div className="bg-gray-900 border border-purple-500/30 p-4 rounded-lg">
                <div className="text-[10px] text-purple-400 font-bold mb-1">AFFECTED COMPONENT</div>
                <div className="text-xs font-bold text-white">COMP-MEMORY</div>
              </div>

              <div className="bg-gray-900 border border-amber-500/30 p-4 rounded-lg">
                <div className="text-[10px] text-amber-400 font-bold mb-1">IMPACT SCORE</div>
                <div className="text-xs font-bold text-white">HIGH (3 Tests Selected)</div>
              </div>

              <div className="bg-gray-900 border border-emerald-500/30 p-4 rounded-lg">
                <div className="text-[10px] text-emerald-400 font-bold mb-1">EXECUTION SAVINGS</div>
                <div className="text-xs font-bold text-white">91.6% Time Reduction</div>
              </div>
            </div>

            {/* Targeted Regression Suite Box */}
            <div className="bg-gray-900/80 border border-gray-800 p-5 rounded-xl space-y-3 font-mono">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-gray-200">TARGETED REGRESSION SUITE (3 SELECTED / 36 TOTAL)</span>
                <button className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-bold flex items-center gap-2">
                  <Play size={14} /> Run Targeted Regression
                </button>
              </div>

              <div className="space-y-2 text-xs">
                <div className="p-2.5 bg-[#0f172a] border border-gray-800 rounded flex justify-between">
                  <span className="font-bold text-white">MEM-003 — Dynamic Memory Allocation</span>
                  <span className="text-emerald-400">Directly Impacts MemoryManager.cpp</span>
                </div>
                <div className="p-2.5 bg-[#0f172a] border border-gray-800 rounded flex justify-between">
                  <span className="font-bold text-white">MEM-007 — Heap Contention Under Parallel Threads</span>
                  <span className="text-emerald-400">Impacted Dependency</span>
                </div>
                <div className="p-2.5 bg-[#0f172a] border border-gray-800 rounded flex justify-between">
                  <span className="font-bold text-white">PERF-021 — Memory Bandwidth Stress</span>
                  <span className="text-emerald-400">Performance Regression Target</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
