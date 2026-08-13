'use client';

import React, { useState } from 'react';
import { Radio, Activity, CheckCircle2, AlertTriangle, Layers, Server, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

export default function ObservabilityPage() {
  const [selectedService, setSelectedService] = useState<string>('qvalidate-control-plane');

  const topology = [
    { name: 'Next.js Portal', role: 'Frontend UI', latency: '1ms', status: 'HEALTHY' },
    { name: 'FastAPI Control Plane', role: 'REST API & TIA', latency: '2ms', status: 'HEALTHY' },
    { name: 'Kafka Event Bus', role: 'Event Broker', latency: '1ms', status: 'HEALTHY' },
    { name: 'Go Scheduler', role: 'Priority Allocator', latency: '1ms', status: 'HEALTHY' },
    { name: 'Worker Pool', role: 'Task Runner', latency: '331ms', status: 'HEALTHY' },
    { name: 'C++20 Runtime', role: 'gRPC Hardware Sim', latency: '320ms', status: 'HEALTHY' },
  ];

  const spans = [
    { span_id: 'span-cp-001', service: 'qvalidate-control-plane', name: 'POST /api/v1/test-runs/execute', duration: '1246ms', status: 'OK' },
    { span_id: 'span-wk-001', service: 'qvalidate-worker-pool', name: 'worker_dispatch_task', duration: '331ms', status: 'OK' },
    { span_id: 'span-cx-001', service: 'qvalidate-cxx-runtime', name: 'gRPC ExecuteValidationSuite', duration: '320ms', status: 'OK' },
    { span_id: 'span-wk-002', service: 'qvalidate-worker-pool', name: 'worker_dispatch_task (ResNet-50)', duration: '871ms', status: 'ERROR' },
    { span_id: 'span-cx-002', service: 'qvalidate-cxx-runtime', name: 'gRPC ExecuteValidationSuite (ResNet-50)', duration: '870ms', status: 'ERROR' },
  ];

  return (
    <div className="space-y-6 font-sans">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-800 pb-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white font-mono flex items-center gap-3">
            <Radio className="text-indigo-400" size={24} /> OPENTELEMETRY TRACE & TOPOLOGY INSPECTOR
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Official OpenTelemetry Python SDK distributed trace hierarchy (`opentelemetry.sdk.trace`) and service topology.
          </p>
        </div>

        <span className="px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-mono font-bold rounded-lg">
          OTel SDK Active
        </span>
      </div>

      {/* Service Topology Map */}
      <div className="bg-[#0f172a] border border-gray-800 rounded-xl p-6 shadow-2xl space-y-4">
        <h3 className="text-xs font-mono font-bold text-gray-400 uppercase tracking-wider">
          MULTI-TIER SERVICE TOPOLOGY & DEPENDENCY GRAPH
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-6 gap-3 text-center font-mono text-xs">
          {topology.map((t, i) => (
            <motion.div
              key={i}
              whileHover={{ scale: 1.05 }}
              onClick={() => setSelectedService(t.name)}
              className="bg-gray-900 border border-gray-800 hover:border-indigo-500/50 p-3 rounded-xl shadow-lg cursor-pointer transition-all"
            >
              <div className="text-[10px] text-indigo-400 font-bold uppercase">{t.role}</div>
              <div className="text-xs font-bold text-white mt-1">{t.name}</div>
              <div className="text-[10px] text-emerald-400 mt-1">● {t.latency}</div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* 9-Span Execution Tree */}
      <div className="bg-[#0f172a] border border-gray-800 rounded-xl p-6 shadow-2xl space-y-4 font-mono">
        <div className="flex items-center justify-between border-b border-gray-800 pb-3">
          <span className="text-xs font-bold text-white">TRACE ID: trace-a2277c0bb973 (RUN-DIST-0697B7)</span>
          <span className="text-xs text-emerald-400 font-bold">5 SPANS CAPTURED</span>
        </div>

        <div className="space-y-2">
          {spans.map((s, idx) => (
            <div
              key={s.span_id}
              style={{ marginLeft: `${idx * 16}px` }}
              className={`p-3 rounded-lg border text-xs flex items-center justify-between transition-all ${
                s.status === 'OK' ? 'bg-gray-900 border-gray-800 text-gray-200' : 'bg-red-500/10 border-red-500/30 text-red-400'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className="text-[10px] text-gray-500">{s.span_id}</span>
                <span className="font-bold text-blue-400">{s.service}</span>
                <span className="text-gray-300">{s.name}</span>
              </div>

              <div className="flex items-center gap-4">
                <span className="font-bold">{s.duration}</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  s.status === 'OK' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'
                }`}>{s.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
