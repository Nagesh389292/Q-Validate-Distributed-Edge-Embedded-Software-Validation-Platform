'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Server, Cpu, ShieldCheck, Activity, AlertTriangle, RefreshCw, X,
  Filter, Zap, Clock, Layers, ChevronUp, ChevronDown, GitBranch
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { DataOriginLegend } from '@/components/DataOriginLegend';


// ─── Types ────────────────────────────────────────────────────────────────────

interface FarmNode {
  id: string;
  arch: 'ARM64_SIM' | 'HEXAGON_DSP_SIM' | 'NPU_SIM' | 'X86_64_SIM';
  status: 'READY' | 'TESTING' | 'ALLOCATED' | 'DEGRADED' | 'ERROR';
  health_score: number;
  cpu_usage: number;
  memory_usage: number;
  temperature_c: number;
  firmware: string;
  active_test?: string;
}

interface K8sDeploymentInfo {
  ready_replicas: number;
  desired_replicas: number;
  available_replicas: number;
}

type ScaleTarget = 10 | 25 | 50 | 100;
type ScaleState = 'idle' | 'scaling' | 'done' | 'error';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

// ─── Kubernetes Scaling Panel ──────────────────────────────────────────────────

function K8sScalingPanel() {
  const [deployInfo, setDeployInfo] = useState<K8sDeploymentInfo | null>(null);
  const [scaleState, setScaleState] = useState<ScaleState>('idle');
  const [scaleTarget, setScaleTarget] = useState<ScaleTarget | null>(null);
  const [scaleProgress, setScaleProgress] = useState(0);
  const [scaleMsg, setScaleMsg] = useState('');
  const [liveData, setLiveData] = useState(false);

  const fetchFarmDeployment = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/kubernetes/deployments`);
      const data = await res.json();
      const farm = data.deployments?.find((d: { name: string }) => d.name === 'qvalidate-cxx-device-farm');
      if (farm) {
        setDeployInfo(farm);
        setLiveData(true);
      }
    } catch {
      setLiveData(false);
    }
  }, []);

  useEffect(() => { fetchFarmDeployment(); }, [fetchFarmDeployment]);

  // Poll while scaling
  useEffect(() => {
    if (scaleState !== 'scaling') return;
    const interval = setInterval(fetchFarmDeployment, 2000);
    return () => clearInterval(interval);
  }, [scaleState, fetchFarmDeployment]);

  // Detect scale completion
  useEffect(() => {
    if (scaleState === 'scaling' && scaleTarget && deployInfo) {
      const pct = Math.min(100, Math.round((deployInfo.ready_replicas / scaleTarget) * 100));
      setScaleProgress(pct);
      if (deployInfo.ready_replicas >= scaleTarget) {
        setScaleProgress(100);
        setScaleMsg(`✓ ${scaleTarget}/${scaleTarget} READY`);
        setScaleState('done');
      }
    }
  }, [deployInfo, scaleState, scaleTarget]);

  const handleScale = async (target: ScaleTarget) => {
    if (scaleState === 'scaling') return;
    setScaleTarget(target);
    setScaleState('scaling');
    setScaleProgress(0);
    setScaleMsg(`Scaling to ${target} replicas…`);
    try {
      const res = await fetch(`${API_BASE}/api/v1/kubernetes/scale/qvalidate-cxx-device-farm?replicas=${target}`, {
        method: 'POST',
      });
      if (!res.ok) throw new Error(await res.text());
      setScaleMsg(`Kubernetes creating pods… (${deployInfo?.ready_replicas ?? '?'} → ${target})`);
    } catch (e) {
      setScaleState('error');
      setScaleMsg(`Scale failed: ${String(e)}`);
    }
  };

  const current = deployInfo?.ready_replicas ?? 0;
  const desired = deployInfo?.desired_replicas ?? 0;

  return (
    <div className="bg-gradient-to-br from-[#0d1527] to-[#0f172a] border border-blue-500/25 rounded-2xl p-6 shadow-2xl space-y-5 font-mono">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-blue-400 uppercase tracking-wider mb-1">
            <Layers size={13} /> KUBERNETES REPLICA CONTROL — C++ DEVICE FARM
          </div>
          <div className="text-xs text-gray-500">Live scaling of qvalidate-cxx-device-farm deployment</div>
        </div>
        <div className="flex items-center gap-2">
          {liveData ? (
            <span className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-500/10 border border-emerald-500/30 rounded text-emerald-400 text-[10px] font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              🟢 LIVE K8S DATA
            </span>
          ) : (
            <span className="px-2.5 py-1 bg-amber-500/10 border border-amber-500/30 rounded text-amber-400 text-[10px] font-bold">
              ⚠ K8S OFFLINE
            </span>
          )}
          <button onClick={fetchFarmDeployment} className="p-1.5 rounded text-gray-500 hover:text-gray-300 transition-colors">
            <RefreshCw size={12} />
          </button>
        </div>
      </div>

      {/* Current replica display */}
      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
          <div className="text-3xl font-black text-white">{current}</div>
          <div className="text-[10px] text-gray-400 mt-1">READY PODS</div>
        </div>
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
          <div className="text-3xl font-black text-blue-400">{desired}</div>
          <div className="text-[10px] text-gray-400 mt-1">DESIRED</div>
        </div>
        <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
          <div className={`text-3xl font-black ${current === desired ? 'text-emerald-400' : 'text-amber-400'}`}>
            {desired > 0 ? Math.round((current / desired) * 100) : 0}%
          </div>
          <div className="text-[10px] text-gray-400 mt-1">READY</div>
        </div>
      </div>

      {/* Scale buttons */}
      <div className="space-y-2">
        <div className="text-[10px] text-gray-500 uppercase tracking-wider">SCALE DEVICE FARM TO:</div>
        <div className="grid grid-cols-4 gap-2">
          {([10, 25, 50, 100] as ScaleTarget[]).map(n => (
            <button
              key={n}
              onClick={() => handleScale(n)}
              disabled={scaleState === 'scaling'}
              className={`py-3 rounded-xl border text-sm font-black transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed ${
                scaleTarget === n && scaleState === 'scaling'
                  ? 'bg-blue-600/30 border-blue-500 text-blue-300 animate-pulse'
                  : scaleTarget === n && scaleState === 'done'
                    ? 'bg-emerald-600/20 border-emerald-500 text-emerald-300'
                    : desired === n && scaleState === 'idle'
                      ? 'bg-blue-600/20 border-blue-500/50 text-blue-300'
                      : 'bg-gray-900 border-gray-700 text-gray-300 hover:border-blue-500/50 hover:text-blue-300'
              }`}
            >
              {n}
            </button>
          ))}
        </div>
      </div>

      {/* Progress bar */}
      <AnimatePresence>
        {(scaleState === 'scaling' || scaleState === 'done') && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-2"
          >
            <div className="flex items-center justify-between text-xs">
              <span className={`font-bold ${scaleState === 'done' ? 'text-emerald-400' : 'text-blue-400'}`}>
                {scaleState === 'done' ? '✓ SCALE COMPLETE' : 'SCALING IN PROGRESS'}
              </span>
              <span className="text-gray-400">{scaleProgress}%</span>
            </div>
            <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
              <motion.div
                className={`h-full rounded-full ${scaleState === 'done' ? 'bg-emerald-500' : 'bg-blue-500'}`}
                animate={{ width: `${scaleProgress}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
            <div className="text-[11px] text-gray-400">{scaleMsg}</div>
          </motion.div>
        )}
        {scaleState === 'error' && (
          <div className="text-xs text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg p-3">
            ⚠ {scaleMsg}
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function DeviceFarmPage() {
  const [filterArch, setFilterArch] = useState<string>('ALL');
  const [selectedNode, setSelectedNode] = useState<FarmNode | null>(null);

  const nodes: FarmNode[] = Array.from({ length: 100 }, (_, i) => {
    const idNum = String(i + 1).padStart(3, '0');
    let arch: FarmNode['arch'] = 'ARM64_SIM';
    if (i >= 40 && i < 65) arch = 'HEXAGON_DSP_SIM';
    else if (i >= 65 && i < 85) arch = 'NPU_SIM';
    else if (i >= 85) arch = 'X86_64_SIM';

    let status: FarmNode['status'] = 'READY';
    if (i === 2 || i === 44 || i === 70) status = 'DEGRADED';
    else if (i % 8 === 0 && i < 50) status = 'TESTING';
    else if (i === 15 || i === 25) status = 'ALLOCATED';

    const health = status === 'DEGRADED' ? 42.0 : status === 'TESTING' ? 91.0 : 99.0;
    const cpu = status === 'TESTING' ? 82.5 : status === 'DEGRADED' ? 98.0 : 14.2;

    return {
      id: `DEVICE-${idNum}`,
      arch, status,
      health_score: health, cpu_usage: cpu,
      memory_usage: status === 'TESTING' ? 68.4 : 32.1,
      temperature_c: status === 'DEGRADED' ? 84.5 : 42.0,
      firmware: 'v2.1.0-release',
      active_test: status === 'TESTING' ? `TEST-SUITE-${(i % 5) + 1}` : undefined,
    };
  });

  const filteredNodes = nodes.filter(n => {
    if (filterArch === 'ALL') return true;
    if (filterArch === 'DEGRADED') return n.status === 'DEGRADED';
    return n.arch === filterArch;
  });

  const readyCount = nodes.filter(n => n.status === 'READY').length;
  const testingCount = nodes.filter(n => n.status === 'TESTING').length;
  const degradedCount = nodes.filter(n => n.status === 'DEGRADED').length;

  return (
    <div className="space-y-6 font-sans">

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-800 pb-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-extrabold text-white font-mono flex items-center gap-3">
              <Server className="text-blue-400" size={24} /> DEVICE FARM — KUBERNETES + SIMULATION
            </h1>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Live Kubernetes replica control · Heterogeneous ARM64 / Hexagon DSP / NPU / x86 simulation topology
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2 font-mono text-xs">
          {['ALL', 'ARM64_SIM', 'HEXAGON_DSP_SIM', 'NPU_SIM', 'X86_64_SIM', 'DEGRADED'].map(f => (
            <button
              key={f}
              onClick={() => setFilterArch(f)}
              className={`px-3 py-1.5 rounded-lg border transition-all ${
                filterArch === f
                  ? 'bg-blue-600/20 border-blue-500/50 text-blue-400 font-bold'
                  : 'bg-[#0f172a] border-gray-800 text-gray-400 hover:text-gray-200'
              }`}
            >
              {f.replace('_SIM', '')}
            </button>
          ))}
        </div>
      </div>

      {/* ── Data Origin Legend ── */}
      <DataOriginLegend items={['live', 'simulated', 'defined']} />

      {/* ── Kubernetes Scaling Panel ── */}
      <K8sScalingPanel />

      {/* ── Simulated Farm Stats ── */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 font-mono">
        <div className="bg-[#0f172a] border border-gray-800 rounded-xl p-4 flex items-center justify-between">
          <div>
            <div className="text-xs text-gray-400">SIMULATION NODES</div>
            <div className="text-2xl font-bold text-white mt-1">100</div>
          </div>
          <Server size={20} className="text-gray-500" />
        </div>
        <div className="bg-[#0f172a] border border-gray-800 rounded-xl p-4 flex items-center justify-between">
          <div>
            <div className="text-xs text-gray-400">READY NODES</div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">{readyCount}</div>
          </div>
          <ShieldCheck size={20} className="text-emerald-400" />
        </div>
        <div className="bg-[#0f172a] border border-gray-800 rounded-xl p-4 flex items-center justify-between">
          <div>
            <div className="text-xs text-gray-400">TESTING WORKERS</div>
            <div className="text-2xl font-bold text-blue-400 mt-1">{testingCount} Active</div>
          </div>
          <Activity size={20} className="text-blue-400" />
        </div>
        <div className="bg-[#0f172a] border border-gray-800 rounded-xl p-4 flex items-center justify-between">
          <div>
            <div className="text-xs text-gray-400">DEGRADED</div>
            <div className="text-2xl font-bold text-amber-400 mt-1">{degradedCount} Isolated</div>
          </div>
          <AlertTriangle size={20} className="text-amber-400" />
        </div>
      </div>

      {/* ── 100-Node Simulation Grid ── */}
      <div className="bg-[#0f172a] border border-gray-800 rounded-xl p-6 shadow-2xl space-y-4 font-mono">
        <div className="flex items-center justify-between text-xs text-gray-400 border-b border-gray-800/80 pb-3">
          <span>HETEROGENEOUS SIMULATION MATRIX ({filteredNodes.length} NODES)</span>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Ready</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-blue-500 animate-pulse" /> Testing</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> Degraded</span>
          </div>
        </div>

        <div className="grid grid-cols-5 sm:grid-cols-10 md:grid-cols-20 gap-2.5 pt-2">
          {filteredNodes.map(n => (
            <motion.button
              key={n.id}
              whileHover={{ scale: 1.15 }}
              onClick={() => setSelectedNode(n)}
              title={`${n.id} (${n.arch}) - ${n.status}`}
              className={`h-9 rounded-lg border flex flex-col items-center justify-center transition-all ${
                n.status === 'READY' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20' :
                n.status === 'TESTING' ? 'bg-blue-500/20 border-blue-500/50 text-blue-400 animate-pulse' :
                'bg-amber-500/20 border-amber-500/50 text-amber-400'
              }`}
            >
              <span className="text-[10px] font-bold">{n.id.split('-')[1]}</span>
            </motion.button>
          ))}
        </div>
      </div>

      {/* ── Node Detail Drawer ── */}
      <AnimatePresence>
        {selectedNode && (
          <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex justify-end">
            <motion.div
              initial={{ x: 320, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: 320, opacity: 0 }}
              className="w-full max-w-md bg-[#0f172a] border-l border-gray-800 h-full p-6 shadow-2xl flex flex-col justify-between font-sans overflow-y-auto"
            >
              <div>
                <div className="flex items-center justify-between border-b border-gray-800 pb-4 mb-6">
                  <div>
                    <h3 className="text-xl font-mono font-bold text-white">{selectedNode.id}</h3>
                    <div className="text-xs font-mono text-blue-400 mt-1">{selectedNode.arch}</div>
                  </div>
                  <button onClick={() => setSelectedNode(null)} className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors">
                    <X size={20} />
                  </button>
                </div>
                <div className="space-y-4 font-mono text-xs">
                  {[
                    { label: 'STATE', value: selectedNode.status, color: selectedNode.status === 'READY' ? 'text-emerald-400' : selectedNode.status === 'TESTING' ? 'text-blue-400' : 'text-amber-400' },
                    { label: 'FIRMWARE', value: selectedNode.firmware, color: 'text-white' },
                    { label: 'HEALTH SCORE', value: `${selectedNode.health_score}/100`, color: 'text-white' },
                    { label: 'CPU UTILIZATION', value: `${selectedNode.cpu_usage}%`, color: 'text-white' },
                    { label: 'TEMPERATURE', value: `${selectedNode.temperature_c}°C`, color: 'text-amber-400' },
                  ].map(row => (
                    <div key={row.label} className="p-3 bg-gray-900 rounded-lg border border-gray-800 flex items-center justify-between">
                      <span className="text-gray-400">{row.label}</span>
                      <span className={`font-bold ${row.color}`}>{row.value}</span>
                    </div>
                  ))}
                  {selectedNode.active_test && (
                    <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg text-blue-400 space-y-1">
                      <div className="text-[10px] font-bold">ACTIVE TEST SUITE</div>
                      <div className="text-xs font-bold text-white">{selectedNode.active_test}</div>
                    </div>
                  )}
                </div>
              </div>
              <div className="pt-4 border-t border-gray-800">
                <button onClick={() => setSelectedNode(null)} className="w-full py-2.5 rounded-lg bg-gray-900 hover:bg-gray-800 border border-gray-800 text-gray-300 font-mono text-xs font-bold transition-colors">
                  Close Node Profile
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
