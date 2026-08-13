'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Skull, RefreshCw, Zap, Server, Cpu, GitBranch, ShieldCheck,
  AlertTriangle, CheckCircle2, Activity, ChevronRight, Layers
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { DataOriginLegend } from '@/components/DataOriginLegend';


const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

// ─── Types ────────────────────────────────────────────────────────────────────

type ExperimentState = 'idle' | 'running' | 'healing' | 'done' | 'error';

interface ExperimentLog {
  ts: string;
  msg: string;
  type: 'info' | 'warn' | 'success' | 'error';
}

interface ChaosExperiment {
  id: string;
  title: string;
  description: string;
  icon: React.ElementType;
  iconColor: string;
  borderColor: string;
  action: () => Promise<void>;
}

interface HpaItem {
  name: string;
  target_deployment: string;
  min_replicas: number;
  max_replicas: number;
  current_replicas: number;
  desired_replicas: number;
  current_cpu_utilization: number | null;
  target_cpu_utilization: number;
}

function HpaStatusPanel() {
  const [hpas, setHpas] = useState<HpaItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchHpa = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/kubernetes/hpa`);
      const data = await res.json();
      if (data.hpas) setHpas(data.hpas);
    } catch {
      // fallback if offline
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchHpa(); }, [fetchHpa]);

  return (
    <div className="bg-[#0d1527] border border-purple-500/20 rounded-2xl p-5 shadow-2xl space-y-4 font-mono">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs font-bold text-purple-400 uppercase tracking-wider">
          <Activity size={14} /> KUBERNETES HORIZONTAL POD AUTOSCALER (HPA)
        </div>
        <div className="flex items-center gap-3">
          <a
            href="http://localhost:30090"
            target="_blank"
            rel="noreferrer"
            className="px-2.5 py-1 rounded bg-orange-500/10 border border-orange-500/30 text-orange-400 text-[10px] font-bold hover:bg-orange-500/20 transition-all"
          >
            PROMETHEUS :30090
          </a>
          <a
            href="http://localhost:30301"
            target="_blank"
            rel="noreferrer"
            className="px-2.5 py-1 rounded bg-amber-500/10 border border-amber-500/30 text-amber-400 text-[10px] font-bold hover:bg-amber-500/20 transition-all"
          >
            GRAFANA :30301
          </a>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {hpas.map(hpa => (
          <div key={hpa.name} className="bg-[#0a0f1e] border border-gray-800 rounded-xl p-4 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-white">{hpa.name}</span>
              <span className="text-purple-400 font-bold">{hpa.target_deployment}</span>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center text-[11px] pt-1">
              <div className="bg-gray-900 rounded p-2 border border-gray-800/80">
                <div className="text-gray-500 text-[9px]">MIN / MAX</div>
                <div className="font-bold text-white mt-0.5">{hpa.min_replicas} / {hpa.max_replicas}</div>
              </div>
              <div className="bg-gray-900 rounded p-2 border border-gray-800/80">
                <div className="text-gray-500 text-[9px]">CURRENT REPLICAS</div>
                <div className="font-bold text-emerald-400 mt-0.5">{hpa.current_replicas} Pods</div>
              </div>
              <div className="bg-gray-900 rounded p-2 border border-gray-800/80">
                <div className="text-gray-500 text-[9px]">TARGET CPU</div>
                <div className="font-bold text-blue-400 mt-0.5">{hpa.target_cpu_utilization}%</div>
              </div>
            </div>
          </div>
        ))}
        {hpas.length === 0 && !loading && (
          <div className="col-span-2 text-xs text-gray-500 text-center py-4 border border-gray-800 rounded-xl">
            HPA configured (qvalidate-cxx-device-farm-hpa: 25-100, qvalidate-fastapi-hpa: 3-10)
          </div>
        )}
      </div>
    </div>
  );
}


// ─── Helper to fetch a random cxx pod name ────────────────────────────────────

async function fetchRandomCxxPod(): Promise<string | null> {
  const res = await fetch(`${API_BASE}/api/v1/kubernetes/pods`);
  const data = await res.json();
  const cxxPods: Array<{ name: string }> = data.pods?.filter((p: { name: string; phase: string }) =>
    p.name.startsWith('qvalidate-cxx-device-farm') && p.phase === 'Running'
  ) ?? [];
  if (cxxPods.length === 0) return null;
  return cxxPods[Math.floor(Math.random() * cxxPods.length)].name;
}

// ─── Heal Monitor (watches replica counts until healed) ───────────────────────

async function waitForHeal(
  deployment: string,
  desiredReplicas: number,
  onProgress: (msg: string, ready: number, desired: number) => void,
  maxWaitMs = 60_000
): Promise<boolean> {
  const start = Date.now();
  while (Date.now() - start < maxWaitMs) {
    await new Promise(r => setTimeout(r, 2000));
    try {
      const res = await fetch(`${API_BASE}/api/v1/kubernetes/deployments`);
      const data = await res.json();
      const dep = data.deployments?.find((d: { name: string }) => d.name === deployment);
      if (dep) {
        onProgress(
          `Kubernetes reconciling… (${dep.ready_replicas}/${dep.desired_replicas} ready)`,
          dep.ready_replicas,
          dep.desired_replicas
        );
        if (dep.ready_replicas >= desiredReplicas) return true;
      }
    } catch { /* ignore transient */ }
  }
  return false;
}

// ─── Log Component ────────────────────────────────────────────────────────────

function EventLog({ logs }: { logs: ExperimentLog[] }) {
  return (
    <div className="bg-gray-950 border border-gray-800 rounded-xl p-4 font-mono text-xs space-y-1.5 max-h-56 overflow-y-auto">
      {logs.length === 0 && (
        <div className="text-gray-600">Waiting for experiment events…</div>
      )}
      {logs.map((log, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          className={`flex items-start gap-2 ${
            log.type === 'success' ? 'text-emerald-400' :
            log.type === 'warn' ? 'text-amber-400' :
            log.type === 'error' ? 'text-red-400' :
            'text-gray-400'
          }`}
        >
          <span className="text-gray-600 shrink-0">{log.ts}</span>
          <ChevronRight size={10} className="mt-0.5 shrink-0" />
          <span>{log.msg}</span>
        </motion.div>
      ))}
    </div>
  );
}

// ─── Self-Heal Visualizer ─────────────────────────────────────────────────────

function HealVisualizer({ state, ready, desired }: { state: ExperimentState; ready: number; desired: number }) {
  const steps = [
    { label: 'POD RUNNING', icon: '●', color: 'text-emerald-400' },
    { label: 'POD TERMINATED', icon: '✕', color: 'text-red-400' },
    { label: 'K8S RECONCILING', icon: '↻', color: 'text-blue-400' },
    { label: 'NEW POD CREATED', icon: '◆', color: 'text-purple-400' },
    { label: 'SELF-HEALED ✓', icon: '✓', color: 'text-emerald-400' },
  ];

  const activeStep =
    state === 'idle' ? -1 :
    state === 'running' ? 1 :
    state === 'healing' ? 2 :
    state === 'done' ? 4 : -1;

  return (
    <div className="flex items-center gap-1 flex-wrap justify-center py-2">
      {steps.map((s, i) => (
        <React.Fragment key={i}>
          <motion.div
            className={`text-center px-3 py-2 rounded-lg border text-xs font-mono font-bold transition-all duration-500 ${
              i <= activeStep
                ? 'border-gray-600 bg-gray-900/80 ' + s.color
                : 'border-gray-800/50 text-gray-700'
            }`}
            animate={i === activeStep && state === 'healing' ? { scale: [1, 1.05, 1] } : {}}
            transition={{ repeat: Infinity, duration: 1 }}
          >
            <div className="text-lg">{s.icon}</div>
            <div className="text-[9px] mt-0.5 whitespace-nowrap">{s.label}</div>
          </motion.div>
          {i < steps.length - 1 && (
            <ChevronRight size={14} className={i < activeStep ? 'text-gray-500' : 'text-gray-800'} />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}

// ─── Chaos Card ───────────────────────────────────────────────────────────────

function ChaosCard({
  experiment,
  state, setState,
  logs, setLogs,
  ready, desired,
}: {
  experiment: ChaosExperiment;
  state: ExperimentState;
  setState: (s: ExperimentState) => void;
  logs: ExperimentLog[];
  setLogs: React.Dispatch<React.SetStateAction<ExperimentLog[]>>;
  ready: number;
  desired: number;
}) {
  const addLog = useCallback((msg: string, type: ExperimentLog['type'] = 'info') => {
    setLogs(prev => [...prev, { ts: new Date().toLocaleTimeString(), msg, type }]);
  }, [setLogs]);

  const run = async () => {
    if (state === 'running' || state === 'healing') return;
    setState('running');
    setLogs([]);
    try {
      await experiment.action();
    } catch (e) {
      setState('error');
      addLog(`Error: ${String(e)}`, 'error');
    }
  };

  const Icon = experiment.icon;
  const isActive = state === 'running' || state === 'healing';

  return (
    <div className={`bg-[#0a0f1e] border ${experiment.borderColor} rounded-2xl p-5 space-y-4 shadow-2xl`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className={`w-10 h-10 rounded-xl bg-gray-900 border ${experiment.borderColor} flex items-center justify-center shrink-0`}>
            <Icon size={20} className={experiment.iconColor} />
          </div>
          <div>
            <div className="text-sm font-bold text-white font-mono">{experiment.title}</div>
            <div className="text-[11px] text-gray-400 mt-0.5">{experiment.description}</div>
          </div>
        </div>
        <span className={`text-[9px] font-mono font-bold px-2 py-1 rounded border whitespace-nowrap ${
          state === 'idle' ? 'text-gray-500 border-gray-700' :
          state === 'running' || state === 'healing' ? 'text-blue-400 border-blue-500/50 bg-blue-500/10 animate-pulse' :
          state === 'done' ? 'text-emerald-400 border-emerald-500/50 bg-emerald-500/10' :
          'text-red-400 border-red-500/50 bg-red-500/10'
        }`}>
          {state.toUpperCase()}
        </span>
      </div>

      {experiment.id === 'kill-pod' && (
        <HealVisualizer state={state} ready={ready} desired={desired} />
      )}

      {state !== 'idle' && (
        <EventLog logs={logs} />
      )}

      {state === 'done' || state === 'error' ? (
        <div className="flex gap-2">
          <button
            onClick={() => { setState('idle'); setLogs([]); }}
            className="flex-1 py-2.5 rounded-xl bg-gray-900 border border-gray-800 text-gray-300 text-xs font-mono font-bold hover:bg-gray-800 transition-colors"
          >
            Reset
          </button>
          <button
            onClick={run}
            className={`flex-1 py-2.5 rounded-xl border text-xs font-mono font-bold transition-colors ${experiment.borderColor} ${experiment.iconColor} hover:bg-gray-900`}
          >
            Run Again
          </button>
        </div>
      ) : (
        <button
          onClick={run}
          disabled={isActive}
          className={`w-full py-3 rounded-xl border text-sm font-mono font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed ${
            isActive
              ? 'bg-blue-600/20 border-blue-500 text-blue-300 animate-pulse'
              : `hover:bg-gray-900 ${experiment.borderColor} ${experiment.iconColor}`
          }`}
        >
          {isActive ? (
            <span className="flex items-center justify-center gap-2">
              <motion.span animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>
                <RefreshCw size={14} />
              </motion.span>
              RUNNING…
            </span>
          ) : '▶ EXECUTE'}
        </button>
      )}
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function ResiliencePage() {
  // Per-experiment state
  const [killState, setKillState] = useState<ExperimentState>('idle');
  const [killLogs, setKillLogs] = useState<ExperimentLog[]>([]);
  const [killReady, setKillReady] = useState(0);
  const [killDesired, setKillDesired] = useState(25);

  const [scaleState, setScaleState] = useState<ExperimentState>('idle');
  const [scaleLogs, setScaleLogs] = useState<ExperimentLog[]>([]);

  const [restartState, setRestartState] = useState<ExperimentState>('idle');
  const [restartLogs, setRestartLogs] = useState<ExperimentLog[]>([]);

  // Fetch current desired count for kill experiment
  useEffect(() => {
    fetch(`${API_BASE}/api/v1/kubernetes/deployments`)
      .then(r => r.json())
      .then(data => {
        const farm = data.deployments?.find((d: { name: string }) => d.name === 'qvalidate-cxx-device-farm');
        if (farm) { setKillReady(farm.ready_replicas); setKillDesired(farm.desired_replicas); }
      }).catch(() => {});
  }, [killState]);

  const killPodAction = async () => {
    const addLog = (msg: string, type: ExperimentLog['type'] = 'info') =>
      setKillLogs(prev => [...prev, { ts: new Date().toLocaleTimeString(), msg, type }]);

    addLog('Fetching running C++ device farm pods…');
    const podName = await fetchRandomCxxPod();
    if (!podName) { throw new Error('No running C++ pods found'); }

    addLog(`Selected target: ${podName}`, 'warn');
    addLog('Sending DELETE to Kubernetes API…', 'warn');
    const res = await fetch(`${API_BASE}/api/v1/kubernetes/pod/${encodeURIComponent(podName)}`, { method: 'DELETE' });
    if (!res.ok) throw new Error(await res.text());

    addLog(`✕ Pod ${podName} terminated (grace=0s)`, 'warn');
    addLog(`Desired replicas: ${killDesired} — waiting for Kubernetes self-heal…`, 'info');
    setKillState('healing');

    const healed = await waitForHeal(
      'qvalidate-cxx-device-farm',
      killDesired,
      (msg, ready, desired) => {
        setKillReady(ready);
        setKillDesired(desired);
        setKillLogs(prev => [...prev, { ts: new Date().toLocaleTimeString(), msg, type: 'info' }]);
      }
    );

    if (healed) {
      addLog(`✓ SELF-HEALED — ${killDesired}/${killDesired} replicas ready`, 'success');
      setKillState('done');
    } else {
      addLog('Timeout: cluster did not heal within 60s', 'error');
      setKillState('error');
    }
  };

  const scaleAction = async () => {
    const addLog = (msg: string, type: ExperimentLog['type'] = 'info') =>
      setScaleLogs(prev => [...prev, { ts: new Date().toLocaleTimeString(), msg, type }]);

    addLog('Fetching current replica count…');
    const depRes = await fetch(`${API_BASE}/api/v1/kubernetes/deployments`);
    const depData = await depRes.json();
    const farm = depData.deployments?.find((d: { name: string }) => d.name === 'qvalidate-cxx-device-farm');
    const currentCount = farm?.ready_replicas ?? 25;
    const targetCount = currentCount >= 50 ? 25 : 50;

    addLog(`Current: ${currentCount} replicas → Scaling to: ${targetCount}`, 'info');
    const res = await fetch(`${API_BASE}/api/v1/kubernetes/scale/qvalidate-cxx-device-farm?replicas=${targetCount}`, { method: 'POST' });
    if (!res.ok) throw new Error(await res.text());
    addLog(`Scale command issued (${currentCount} → ${targetCount})…`, 'warn');

    const healed = await waitForHeal(
      'qvalidate-cxx-device-farm',
      targetCount,
      (msg) => setScaleLogs(prev => [...prev, { ts: new Date().toLocaleTimeString(), msg, type: 'info' }])
    );

    if (healed) {
      addLog(`✓ Scale complete — ${targetCount}/${targetCount} pods ready`, 'success');
      setScaleState('done');
    } else {
      addLog('Timeout waiting for scale completion', 'error');
      setScaleState('error');
    }
  };

  const rolloutAction = async () => {
    const addLog = (msg: string, type: ExperimentLog['type'] = 'info') =>
      setRestartLogs(prev => [...prev, { ts: new Date().toLocaleTimeString(), msg, type }]);

    const deployment = 'qvalidate-go-scheduler';
    addLog(`Triggering rolling restart: ${deployment}…`);
    const res = await fetch(`${API_BASE}/api/v1/kubernetes/rollout-restart/${deployment}`, { method: 'POST' });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    addLog(`Rolling restart initiated at ${data.restarted_at}`, 'warn');
    addLog('Kubernetes will terminate old pods, create new ones (zero-downtime)…', 'info');

    setRestartState('healing');
    await new Promise(r => setTimeout(r, 3000));

    const healed = await waitForHeal(
      deployment,
      2, // go-scheduler has 2 replicas
      (msg) => setRestartLogs(prev => [...prev, { ts: new Date().toLocaleTimeString(), msg, type: 'info' }])
    );

    if (healed) {
      addLog('✓ Rolling restart complete — all pods running new revision', 'success');
      setRestartState('done');
    } else {
      addLog('Timeout waiting for rollout completion', 'error');
      setRestartState('error');
    }
  };

  const experiments: ChaosExperiment[] = [
    {
      id: 'kill-pod',
      title: 'Kill Random Device Pod',
      description: 'Terminates a random qvalidate-cxx-device-farm pod. Kubernetes self-heals by creating a replacement.',
      icon: Skull,
      iconColor: 'text-red-400',
      borderColor: 'border-red-500/30',
      action: killPodAction,
    },
    {
      id: 'scale-farm',
      title: 'Scale Farm 25 ↔ 50',
      description: 'Toggles the C++ device farm between 25 and 50 replicas via Kubernetes scale API. Watches reconciliation.',
      icon: Cpu,
      iconColor: 'text-blue-400',
      borderColor: 'border-blue-500/30',
      action: scaleAction,
    },
    {
      id: 'rollout-restart',
      title: 'Rolling Restart Scheduler',
      description: 'Triggers zero-downtime rolling restart of the Go Scheduler deployment (2 replicas). Old pods replaced one-by-one.',
      icon: RefreshCw,
      iconColor: 'text-purple-400',
      borderColor: 'border-purple-500/30',
      action: rolloutAction,
    },
  ];

  return (
    <div className="space-y-6 font-sans">

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-800 pb-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-extrabold text-white font-mono flex items-center gap-3">
              <Zap className="text-red-400" size={24} />
              KUBERNETES RESILIENCE LAB
            </h1>
            <span className="px-2.5 py-1 rounded bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-mono font-bold">
              CHAOS ENGINEERING
            </span>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Execute real Kubernetes operations: pod termination, live scaling, rolling restarts. Watch self-healing in real time.
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-2 bg-amber-500/10 border border-amber-500/20 rounded-xl text-amber-400 text-xs font-mono">
          <AlertTriangle size={13} />
          <span>AFFECTS LIVE CLUSTER</span>
        </div>
      </div>

      {/* ── Data Origin Legend ── */}
      <DataOriginLegend items={['live', 'defined']} />

      {/* ── HPA Status Panel ── */}
      <HpaStatusPanel />

      {/* Architecture map */}

      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 font-mono text-xs">
        {[
          { name: 'FastAPI', pods: '3', icon: Server, color: 'text-blue-400', border: 'border-blue-500/20' },
          { name: 'Go Scheduler', pods: '2', icon: GitBranch, color: 'text-purple-400', border: 'border-purple-500/20' },
          { name: 'PostgreSQL', pods: '1', icon: Server, color: 'text-amber-400', border: 'border-amber-500/20' },
          { name: 'Frontend', pods: '1', icon: Layers, color: 'text-cyan-400', border: 'border-cyan-500/20' },
          { name: 'C++ Farm', pods: '25+', icon: Cpu, color: 'text-emerald-400', border: 'border-emerald-500/20' },
        ].map(svc => {
          const Icon = svc.icon;
          return (
            <div key={svc.name} className={`bg-[#0f172a] border ${svc.border} rounded-xl p-3 text-center space-y-1`}>
              <Icon size={18} className={`${svc.color} mx-auto`} />
              <div className={`font-bold text-[11px] ${svc.color}`}>{svc.name}</div>
              <div className="text-gray-500 text-[10px]">{svc.pods} pods</div>
            </div>
          );
        })}
      </div>

      {/* Experiment cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <ChaosCard
          experiment={experiments[0]}
          state={killState} setState={setKillState}
          logs={killLogs} setLogs={setKillLogs}
          ready={killReady} desired={killDesired}
        />
        <ChaosCard
          experiment={experiments[1]}
          state={scaleState} setState={setScaleState}
          logs={scaleLogs} setLogs={setScaleLogs}
          ready={0} desired={0}
        />
        <ChaosCard
          experiment={experiments[2]}
          state={restartState} setState={setRestartState}
          logs={restartLogs} setLogs={setRestartLogs}
          ready={0} desired={0}
        />
      </div>

      {/* Theory section */}
      <div className="bg-[#0d1527] border border-gray-800 rounded-xl p-5 font-mono text-xs space-y-3">
        <div className="text-blue-400 font-bold uppercase tracking-wider">KUBERNETES SELF-HEALING MECHANISM</div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-gray-400">
          <div className="space-y-1">
            <div className="text-emerald-400 font-bold">1. Pod Deletion</div>
            <div>kubectl delete / API call terminates a pod with grace_period=0. ReplicaSet detects count drop.</div>
          </div>
          <div className="space-y-1">
            <div className="text-blue-400 font-bold">2. Reconciliation Loop</div>
            <div>kube-controller-manager continuously compares desired vs actual replicas and creates a replacement.</div>
          </div>
          <div className="space-y-1">
            <div className="text-emerald-400 font-bold">3. Self-Heal Complete</div>
            <div>New pod is scheduled, image pulled from containerd cache, container starts, readiness probe passes.</div>
          </div>
        </div>
      </div>
    </div>
  );
}
