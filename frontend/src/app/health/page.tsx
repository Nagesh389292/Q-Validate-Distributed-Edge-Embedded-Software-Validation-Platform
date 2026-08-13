'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  ShieldCheck, Server, Database, Cpu, Activity, CheckCircle2,
  AlertTriangle, RefreshCw, Wifi, WifiOff, Clock, Box,
  GitBranch, Layers, Zap, ArrowRight, Circle
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { DataOriginLegend } from '@/components/DataOriginLegend';


// ─── Types ────────────────────────────────────────────────────────────────────

interface DeploymentData {
  name: string;
  desired_replicas: number;
  ready_replicas: number;
  available_replicas: number;
  images: string[];
  age: string;
}

interface PodData {
  name: string;
  node: string;
  pod_ip: string;
  phase: string;
  ready: string;
  restarts: number;
  age: string;
}

interface ClusterData {
  cluster_connected: boolean;
  kubernetes_version: string;
  namespace: string;
  nodes: Array<{ name: string; ready: boolean; kubernetes_version: string; os_image: string }>;
  pod_totals: { total: number; running: number };
  replica_totals: { desired: number; ready: number };
  deployment_summary: Array<{ name: string; desired: number; ready: number; available: number }>;
}

interface DeploymentListData {
  total_desired: number;
  total_ready: number;
  all_healthy: boolean;
  deployments: DeploymentData[];
}

interface PodListData {
  total: number;
  running: number;
  pods: PodData[];
}

// ─── Config ───────────────────────────────────────────────────────────────────

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

const DEPLOYMENT_META: Record<string, { label: string; icon: React.ElementType; color: string }> = {
  'qvalidate-control-plane': { label: 'FastAPI Control Plane', icon: Server, color: 'text-blue-400' },
  'qvalidate-go-scheduler': { label: 'Go Distributed Scheduler', icon: GitBranch, color: 'text-purple-400' },
  'postgres-db': { label: 'PostgreSQL Database', icon: Database, color: 'text-amber-400' },
  'qvalidate-frontend': { label: 'Next.js Engineering Portal', icon: Layers, color: 'text-cyan-400' },
  'qvalidate-cxx-device-farm': { label: 'C++ Device Farm', icon: Cpu, color: 'text-emerald-400' },
};

// ─── Utilities ────────────────────────────────────────────────────────────────

function shortName(name: string): string {
  return DEPLOYMENT_META[name]?.label ?? name;
}

function useInterval(callback: () => void, delay: number) {
  const savedCallback = React.useRef(callback);
  useEffect(() => { savedCallback.current = callback; }, [callback]);
  useEffect(() => {
    const tick = () => savedCallback.current();
    const id = setInterval(tick, delay);
    return () => clearInterval(id);
  }, [delay]);
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function LiveBadge({ connected, lastUpdated }: { connected: boolean; lastUpdated: Date | null }) {
  return (
    <div className="flex items-center gap-3">
      {connected ? (
        <span className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-400 text-xs font-mono font-bold">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-400" />
          </span>
          🟢 LIVE KUBERNETES DATA
        </span>
      ) : (
        <span className="flex items-center gap-2 px-3 py-1.5 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-xs font-mono font-bold">
          <WifiOff size={12} /> CLUSTER OFFLINE
        </span>
      )}
      {lastUpdated && (
        <span className="text-[10px] text-gray-500 font-mono flex items-center gap-1">
          <Clock size={10} /> {lastUpdated.toLocaleTimeString()}
        </span>
      )}
    </div>
  );
}

function ReplicaBar({ ready, desired }: { ready: number; desired: number }) {
  const pct = desired > 0 ? (ready / desired) * 100 : 0;
  const color = pct === 100 ? 'bg-emerald-500' : pct >= 50 ? 'bg-amber-500' : 'bg-red-500';
  return (
    <div className="flex items-center gap-2 w-full">
      <div className="flex-1 h-1.5 bg-gray-800 rounded-full overflow-hidden">
        <motion.div
          className={`h-full rounded-full ${color}`}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
      <span className={`text-xs font-mono font-bold ${pct === 100 ? 'text-emerald-400' : 'text-amber-400'}`}>
        {ready}/{desired}
      </span>
    </div>
  );
}

// ─── Architecture Flow ─────────────────────────────────────────────────────────

function ArchitectureFlow() {
  const [step, setStep] = useState(0);
  const steps = ['frontend', 'fastapi', 'split', 'postgres', 'scheduler', 'cxx'];

  useEffect(() => {
    const t = setInterval(() => setStep(s => (s + 1) % steps.length), 1200);
    return () => clearInterval(t);
  }, [steps.length]);

  const nodeClass = (id: string, activeIds: string[]) =>
    `transition-all duration-500 ${activeIds.includes(id) ? 'opacity-100' : 'opacity-30'}`;

  const activeIds = (() => {
    if (step === 0) return ['frontend'];
    if (step === 1) return ['frontend', 'arrow1', 'fastapi'];
    if (step === 2) return ['fastapi'];
    if (step === 3) return ['fastapi', 'arrow2', 'postgres'];
    if (step === 4) return ['fastapi', 'arrow3', 'scheduler'];
    return ['fastapi', 'arrow4', 'cxx'];
  })();

  return (
    <div className="bg-[#0a0f1e] border border-blue-500/20 rounded-xl p-6 font-mono">
      <div className="text-[10px] text-blue-400 font-bold uppercase tracking-wider mb-5 flex items-center gap-2">
        <Zap size={12} /> LIVE TRAFFIC FLOW ANIMATION
      </div>
      <div className="flex items-center justify-between gap-2 overflow-x-auto pb-2">

        {/* Frontend */}
        <div className={`flex flex-col items-center gap-1.5 min-w-[80px] ${nodeClass('frontend', activeIds)}`}>
          <div className="w-14 h-14 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
            <Layers size={24} className="text-cyan-400" />
          </div>
          <span className="text-[9px] text-cyan-400 text-center">Next.js<br/>Portal</span>
        </div>

        {/* Arrow 1 */}
        <motion.div className={nodeClass('arrow1', activeIds)} animate={{ x: activeIds.includes('arrow1') ? [0, 6, 0] : 0 }} transition={{ repeat: Infinity, duration: 0.5 }}>
          <ArrowRight size={16} className="text-blue-500" />
        </motion.div>

        {/* FastAPI */}
        <div className={`flex flex-col items-center gap-1.5 min-w-[80px] ${nodeClass('fastapi', activeIds)}`}>
          <div className="w-14 h-14 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center">
            <Server size={24} className="text-blue-400" />
          </div>
          <span className="text-[9px] text-blue-400 text-center">FastAPI<br/>3 Pods</span>
        </div>

        {/* Split arrows */}
        <div className="flex flex-col gap-3">
          <motion.div className={nodeClass('arrow2', activeIds)} animate={{ x: activeIds.includes('arrow2') ? [0, 6, 0] : 0 }} transition={{ repeat: Infinity, duration: 0.5 }}>
            <ArrowRight size={14} className="text-amber-500" />
          </motion.div>
          <motion.div className={nodeClass('arrow3', activeIds)} animate={{ x: activeIds.includes('arrow3') ? [0, 6, 0] : 0 }} transition={{ repeat: Infinity, duration: 0.5 }}>
            <ArrowRight size={14} className="text-purple-500" />
          </motion.div>
          <motion.div className={nodeClass('arrow4', activeIds)} animate={{ x: activeIds.includes('arrow4') ? [0, 6, 0] : 0 }} transition={{ repeat: Infinity, duration: 0.5 }}>
            <ArrowRight size={14} className="text-emerald-500" />
          </motion.div>
        </div>

        {/* Right services */}
        <div className="flex flex-col gap-3">
          <div className={`flex items-center gap-2 ${nodeClass('postgres', activeIds)}`}>
            <div className="w-11 h-11 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center">
              <Database size={18} className="text-amber-400" />
            </div>
            <span className="text-[9px] text-amber-400">PostgreSQL<br/>1 Pod</span>
          </div>
          <div className={`flex items-center gap-2 ${nodeClass('scheduler', activeIds)}`}>
            <div className="w-11 h-11 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center">
              <GitBranch size={18} className="text-purple-400" />
            </div>
            <span className="text-[9px] text-purple-400">Go Scheduler<br/>2 Pods</span>
          </div>
          <div className={`flex items-center gap-2 ${nodeClass('cxx', activeIds)}`}>
            <div className="w-11 h-11 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center">
              <Cpu size={18} className="text-emerald-400" />
            </div>
            <span className="text-[9px] text-emerald-400">C++ Farm<br/>25 Pods</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function KubernetesCommandCenter() {
  const [cluster, setCluster] = useState<ClusterData | null>(null);
  const [deployments, setDeployments] = useState<DeploymentListData | null>(null);
  const [pods, setPods] = useState<PodListData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [showPods, setShowPods] = useState(false);

  const fetchAll = useCallback(async () => {
    try {
      const [cRes, dRes, pRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1/kubernetes/cluster`),
        fetch(`${API_BASE}/api/v1/kubernetes/deployments`),
        fetch(`${API_BASE}/api/v1/kubernetes/pods`),
      ]);
      const [cData, dData, pData] = await Promise.all([cRes.json(), dRes.json(), pRes.json()]);
      setCluster(cData);
      setDeployments(dData);
      setPods(pData);
      setLastUpdated(new Date());
      setError(null);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);
  useInterval(fetchAll, 10_000); // Refresh every 10s

  const connected = !!cluster?.cluster_connected && !error;
  const totalDesired = deployments?.total_desired ?? 0;
  const totalReady = deployments?.total_ready ?? 0;

  return (
    <div className="space-y-6 font-sans">

      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-800 pb-4">
        <div>
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-2xl font-extrabold text-white font-mono flex items-center gap-3">
              <ShieldCheck className="text-emerald-400" size={24} />
              KUBERNETES COMMAND CENTER
            </h1>
          </div>
          {cluster && (
            <p className="text-xs text-gray-400 mt-1 font-mono">
              Node: <span className="text-white">{cluster.nodes[0]?.name ?? 'unknown'}</span> &nbsp;·&nbsp;
              Kubernetes <span className="text-blue-400">{cluster.kubernetes_version}</span> &nbsp;·&nbsp;
              Namespace: <span className="text-purple-400">{cluster.namespace}</span>
            </p>
          )}
        </div>
        <div className="flex items-center gap-3">
          <LiveBadge connected={connected} lastUpdated={lastUpdated} />
          <button
            onClick={fetchAll}
            className="p-2 rounded-lg bg-gray-900 border border-gray-800 text-gray-400 hover:text-white hover:bg-gray-800 transition-all"
            title="Refresh now"
          >
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      {/* ── Data Origin Legend ── */}
      <DataOriginLegend items={['live', 'defined']} />

      {/* ── Loading skeleton ── */}
      {loading && (

        <div className="flex items-center justify-center py-20 text-gray-500">
          <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>
            <RefreshCw size={24} />
          </motion.div>
          <span className="ml-3 font-mono text-sm">Connecting to Kubernetes API…</span>
        </div>
      )}

      {/* ── Error banner ── */}
      {error && !loading && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-400 text-sm font-mono flex items-center gap-3">
          <AlertTriangle size={16} />
          <span>Kubernetes API unreachable: {error}. Ensure the FastAPI pod has the qvalidate-api-sa ServiceAccount.</span>
        </div>
      )}

      {/* ── Live Cluster Banner ── */}
      {cluster && !loading && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-emerald-950/40 via-[#0d1527] to-blue-950/40 border border-emerald-500/25 rounded-2xl p-6 shadow-2xl"
        >
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="text-center space-y-1">
              <div className="text-3xl font-black font-mono text-white">{totalReady}<span className="text-gray-600">/{totalDesired}</span></div>
              <div className="text-[11px] text-gray-400 font-mono uppercase tracking-wider">Total Replicas Ready</div>
              <div className={`text-xs font-bold ${totalReady === totalDesired ? 'text-emerald-400' : 'text-amber-400'}`}>
                {totalReady === totalDesired ? '✓ ALL SYSTEMS GO' : '⚠ DEGRADED'}
              </div>
            </div>
            <div className="text-center space-y-1">
              <div className="text-3xl font-black font-mono text-white">{cluster.pod_totals.running}<span className="text-gray-600">/{cluster.pod_totals.total}</span></div>
              <div className="text-[11px] text-gray-400 font-mono uppercase tracking-wider">Pods Running</div>
              <div className="text-xs font-bold text-blue-400">● LIVE COUNT</div>
            </div>
            <div className="text-center space-y-1">
              <div className="text-3xl font-black font-mono text-cyan-400">{cluster.nodes.length}</div>
              <div className="text-[11px] text-gray-400 font-mono uppercase tracking-wider">Cluster Nodes</div>
              <div className="text-xs font-bold text-cyan-400">{cluster.nodes[0]?.name ?? '—'}</div>
            </div>
            <div className="text-center space-y-1">
              <div className="text-3xl font-black font-mono text-purple-400">{deployments?.deployments.length ?? 0}</div>
              <div className="text-[11px] text-gray-400 font-mono uppercase tracking-wider">Deployments</div>
              <div className="text-xs font-bold text-purple-400">{cluster.namespace}</div>
            </div>
          </div>
        </motion.div>
      )}

      {/* ── Deployment Health Grid ── */}
      {deployments && !loading && (
        <div className="bg-[#0f172a] border border-gray-800 rounded-xl overflow-hidden shadow-2xl">
          <div className="flex items-center justify-between px-5 py-4 border-b border-gray-800">
            <h3 className="text-xs font-bold text-gray-200 uppercase tracking-wider font-mono flex items-center gap-2">
              <Box size={14} className="text-blue-400" /> APPLICATION DEPLOYMENT STATUS
            </h3>
            <span className={`text-xs font-mono font-bold px-2 py-1 rounded border ${deployments.all_healthy ? 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10' : 'text-amber-400 border-amber-500/30 bg-amber-500/10'}`}>
              {deployments.all_healthy ? '✓ ALL HEALTHY' : '⚠ DEGRADED'}
            </span>
          </div>

          <div className="divide-y divide-gray-800/60">
            {deployments.deployments.map((dep, idx) => {
              const meta = DEPLOYMENT_META[dep.name];
              const Icon = meta?.icon ?? Server;
              const healthy = dep.ready_replicas === dep.desired_replicas;

              return (
                <motion.div
                  key={dep.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.07 }}
                  className="flex items-center gap-4 px-5 py-4 hover:bg-gray-900/40 transition-colors"
                >
                  <Icon size={18} className={meta?.color ?? 'text-gray-400'} />

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className="text-sm font-bold text-white font-mono truncate">{dep.name}</span>
                      <span className="text-[9px] text-gray-500 font-mono shrink-0">{dep.age}</span>
                    </div>
                    <ReplicaBar ready={dep.ready_replicas} desired={dep.desired_replicas} />
                  </div>

                  <div className="text-right shrink-0 space-y-1">
                    <div className={`text-sm font-black font-mono ${healthy ? 'text-emerald-400' : 'text-amber-400'}`}>
                      {dep.ready_replicas} / {dep.desired_replicas}
                    </div>
                    <div className={`text-[9px] font-mono px-2 py-0.5 rounded border ${healthy ? 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10' : 'text-amber-400 border-amber-500/30 bg-amber-500/10'}`}>
                      {healthy ? '● READY' : '⚠ PARTIAL'}
                    </div>
                  </div>

                  <div className="hidden lg:block text-right shrink-0">
                    <div className="text-[10px] text-gray-500 font-mono">{dep.images[0]}</div>
                  </div>
                </motion.div>
              );
            })}

            {/* Total Row */}
            <div className="flex items-center gap-4 px-5 py-4 bg-gray-900/60">
              <CheckCircle2 size={18} className="text-emerald-400" />
              <div className="flex-1">
                <span className="text-sm font-black text-white font-mono">TOTAL — ALL DEPLOYMENTS</span>
              </div>
              <div className="text-right">
                <div className={`text-lg font-black font-mono ${totalReady === totalDesired ? 'text-emerald-400' : 'text-amber-400'}`}>
                  {totalReady} / {totalDesired}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Architecture Flow ── */}
      <ArchitectureFlow />

      {/* ── Pod Table (expandable) ── */}
      {pods && !loading && (
        <div className="bg-[#0f172a] border border-gray-800 rounded-xl overflow-hidden shadow-2xl">
          <button
            onClick={() => setShowPods(v => !v)}
            className="w-full flex items-center justify-between px-5 py-4 border-b border-gray-800 hover:bg-gray-900/40 transition-colors"
          >
            <h3 className="text-xs font-bold text-gray-200 uppercase tracking-wider font-mono flex items-center gap-2">
              <Activity size={14} className="text-emerald-400" />
              LIVE POD INVENTORY ({pods.running} running / {pods.total} total)
            </h3>
            <span className="text-xs text-gray-500 font-mono">{showPods ? '▲ Collapse' : '▼ Expand'}</span>
          </button>

          <AnimatePresence>
            {showPods && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="overflow-hidden"
              >
                <div className="overflow-x-auto max-h-96 overflow-y-auto">
                  <table className="w-full text-[11px] font-mono">
                    <thead className="sticky top-0 bg-gray-900/95 text-gray-400 uppercase text-[9px] tracking-wider">
                      <tr>
                        <th className="text-left px-4 py-2">Pod Name</th>
                        <th className="text-left px-4 py-2">Status</th>
                        <th className="text-left px-4 py-2">Ready</th>
                        <th className="text-left px-4 py-2">IP</th>
                        <th className="text-left px-4 py-2">Restarts</th>
                        <th className="text-left px-4 py-2">Age</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800/40">
                      {pods.pods.map((pod) => (
                        <tr key={pod.name} className="hover:bg-gray-900/40 transition-colors">
                          <td className="px-4 py-2 text-gray-200 truncate max-w-[240px]">{pod.name}</td>
                          <td className="px-4 py-2">
                            <span className={`flex items-center gap-1.5 ${pod.phase === 'Running' ? 'text-emerald-400' : 'text-amber-400'}`}>
                              <span className={`w-1.5 h-1.5 rounded-full ${pod.phase === 'Running' ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
                              {pod.phase}
                            </span>
                          </td>
                          <td className="px-4 py-2 text-gray-300">{pod.ready}</td>
                          <td className="px-4 py-2 text-blue-400">{pod.pod_ip ?? '—'}</td>
                          <td className={`px-4 py-2 font-bold ${pod.restarts > 0 ? 'text-amber-400' : 'text-gray-500'}`}>{pod.restarts}</td>
                          <td className="px-4 py-2 text-gray-500">{pod.age}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}

      {/* ── Node Info ── */}
      {cluster && !loading && cluster.nodes.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono">
          {cluster.nodes.map((node) => (
            <div key={node.name} className="bg-[#0f172a] border border-gray-800 rounded-xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Control Plane Node</span>
                <span className={`text-[10px] px-2 py-0.5 rounded border font-bold ${node.ready ? 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10' : 'text-red-400 border-red-500/30 bg-red-500/10'}`}>
                  {node.ready ? '● READY' : '● NOT READY'}
                </span>
              </div>
              <div className="text-sm font-bold text-white">{node.name}</div>
              <div className="text-[10px] text-gray-500 space-y-1">
                <div>Version: <span className="text-blue-400">{node.kubernetes_version}</span></div>
                <div>OS: <span className="text-gray-300">{node.os_image}</span></div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
