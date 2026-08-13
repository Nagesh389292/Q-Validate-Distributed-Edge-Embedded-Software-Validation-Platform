'use client';

import React, { useState } from 'react';
import {
  AreaChart,
  Area,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip
} from 'recharts';
import { Cpu, AlertTriangle, RefreshCw, Zap, ShieldCheck, Thermometer, HardDrive, CheckCircle2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface DeviceTelemetry {
  device_id: string;
  hardware_arch: string;
  state: 'READY' | 'TESTING' | 'DEGRADED' | 'FAULT_INJECTED';
  cpu_percent: number;
  memory_percent: number;
  temperature_c: number;
  firmware_version: string;
  health_score: number;
  active_fault?: string;
}

export default function DeviceLabPage() {
  const [devices, setDevices] = useState<DeviceTelemetry[]>([
    { device_id: 'DEVICE-001', hardware_arch: 'ARM64_SIM', state: 'READY', cpu_percent: 18.4, memory_percent: 32.1, temperature_c: 42.5, firmware_version: 'v2.1.0-release', health_score: 98.0 },
    { device_id: 'DEVICE-002', hardware_arch: 'HEXAGON_DSP_SIM', state: 'TESTING', cpu_percent: 78.9, memory_percent: 64.2, temperature_c: 68.2, firmware_version: 'v2.1.0-release', health_score: 92.5 },
    { device_id: 'DEVICE-003', hardware_arch: 'NPU_SIM', state: 'DEGRADED', cpu_percent: 98.2, memory_percent: 89.5, temperature_c: 84.1, firmware_version: 'v2.0.9-patch', health_score: 45.0, active_fault: 'CPU_OVERLOAD' },
    { device_id: 'DEVICE-004', hardware_arch: 'X86_64_SIM', state: 'READY', cpu_percent: 12.0, memory_percent: 24.5, temperature_c: 38.0, firmware_version: 'v2.1.0-release', health_score: 100.0 },
  ]);

  const [selectedDeviceId, setSelectedDeviceId] = useState<string>('DEVICE-003');
  const [faultConfirm, setFaultConfirm] = useState<string | null>(null);
  const [injecting, setInjecting] = useState<boolean>(false);

  const selectedDevice = devices.find(d => d.device_id === selectedDeviceId) || devices[0];

  // Mock historical sensor telemetry data for Recharts
  const telemetryHistory = [
    { time: '19:10', cpu: selectedDevice.cpu_percent * 0.7, memory: selectedDevice.memory_percent * 0.8, temp: selectedDevice.temperature_c * 0.9 },
    { time: '19:11', cpu: selectedDevice.cpu_percent * 0.85, memory: selectedDevice.memory_percent * 0.9, temp: selectedDevice.temperature_c * 0.95 },
    { time: '19:12', cpu: selectedDevice.cpu_percent, memory: selectedDevice.memory_percent, temp: selectedDevice.temperature_c },
  ];

  const handleInjectFault = (faultType: string) => {
    setInjecting(true);
    setTimeout(() => {
      setDevices(prev => prev.map(d => {
        if (d.device_id === selectedDeviceId) {
          return {
            ...d,
            state: 'DEGRADED',
            active_fault: faultType,
            health_score: 40.0,
            cpu_percent: faultType === 'CPU_OVERLOAD' ? 99.5 : d.cpu_percent,
            memory_percent: faultType === 'MEMORY_PRESSURE' ? 95.0 : d.memory_percent,
            temperature_c: 88.5
          };
        }
        return d;
      }));
      setInjecting(false);
      setFaultConfirm(null);
    }, 600);
  };

  const handleClearFault = () => {
    setDevices(prev => prev.map(d => {
      if (d.device_id === selectedDeviceId) {
        return {
          ...d,
          state: 'READY',
          active_fault: undefined,
          health_score: 96.0,
          cpu_percent: 22.0,
          memory_percent: 34.0,
          temperature_c: 44.0
        };
      }
      return d;
    }));
  };

  return (
    <div className="space-y-6 font-sans">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-800 pb-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white font-mono flex items-center gap-3">
            <Cpu className="text-blue-400" size={24} /> HARDWARE VALIDATION CONSOLE & FAULT STUDIO
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            Real-time sensor telemetry monitoring and hardware fault injection for simulated edge device nodes.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono font-bold rounded-lg flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" /> gRPC IPC Active
          </span>
        </div>
      </div>

      {/* Main Console Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Device Selection Column */}
        <div className="space-y-3">
          <h2 className="text-xs font-bold font-mono text-gray-400 uppercase tracking-wider">
            Simulated Hardware Nodes
          </h2>

          <div className="space-y-2 font-mono">
            {devices.map(d => {
              const isSelected = d.device_id === selectedDeviceId;
              return (
                <button
                  key={d.device_id}
                  onClick={() => setSelectedDeviceId(d.device_id)}
                  className={`w-full text-left p-4 rounded-xl border transition-all ${
                    isSelected
                      ? 'bg-blue-600/15 border-blue-500/50 shadow-lg shadow-blue-500/10'
                      : 'bg-[#0f172a] border-gray-800 hover:border-gray-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-sm text-white">{d.device_id}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      d.state === 'READY' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                      d.state === 'TESTING' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' :
                      'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {d.state}
                    </span>
                  </div>

                  <div className="text-xs text-gray-400 flex items-center justify-between">
                    <span>{d.hardware_arch}</span>
                    <span className="text-gray-300 font-bold">Health: {d.health_score}/100</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Selected Device Telemetry & Control Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Telemetry Dashboard Box */}
          <div className="bg-[#0f172a] border border-gray-800 rounded-xl p-6 shadow-2xl space-y-6">
            <div className="flex items-center justify-between border-b border-gray-800 pb-4">
              <div>
                <div className="flex items-center gap-3 font-mono">
                  <h3 className="text-xl font-bold text-white">{selectedDevice.device_id}</h3>
                  <span className="text-xs text-blue-400 bg-blue-500/10 px-2.5 py-0.5 rounded border border-blue-500/20">
                    {selectedDevice.hardware_arch}
                  </span>
                </div>
                <div className="text-xs text-gray-400 mt-1 font-mono">Firmware: {selectedDevice.firmware_version}</div>
              </div>

              {selectedDevice.active_fault && (
                <div className="px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-mono font-bold flex items-center gap-2">
                  <AlertTriangle size={14} /> Fault: {selectedDevice.active_fault}
                </div>
              )}
            </div>

            {/* Recharts Sensor History Graph */}
            <div className="bg-gray-900/80 border border-gray-800 p-4 rounded-xl space-y-2">
              <div className="text-xs font-mono text-gray-400 font-bold flex items-center justify-between">
                <span>LIVE SENSOR TELEMETRY HISTORY (CPU / RAM / TEMP)</span>
                <span className="text-emerald-400 font-normal">Auto-streaming</span>
              </div>
              <div className="h-40 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={telemetryHistory} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                    <XAxis dataKey="time" stroke="#9ca3af" fontSize={10} fontFamily="monospace" />
                    <YAxis stroke="#9ca3af" fontSize={10} fontFamily="monospace" />
                    <Tooltip contentStyle={{ backgroundColor: '#090d16', borderColor: '#374151', borderRadius: '8px', fontSize: '11px', fontFamily: 'monospace' }} />
                    <Area type="monotone" dataKey="cpu" name="CPU Utilization (%)" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.2} />
                    <Area type="monotone" dataKey="temp" name="Temperature (°C)" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.2} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Metrics Gauges Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono">
              <div className="bg-gray-900/80 border border-gray-800 p-4 rounded-lg">
                <div className="text-xs text-gray-400 flex items-center justify-between">
                  <span>CPU UTILIZATION</span>
                  <Cpu size={14} className="text-blue-400" />
                </div>
                <div className="text-2xl font-bold text-white mt-2">{selectedDevice.cpu_percent}%</div>
                <div className="w-full bg-gray-800 h-2 rounded-full mt-3 overflow-hidden">
                  <div className="bg-blue-500 h-full rounded-full transition-all duration-500" style={{ width: `${selectedDevice.cpu_percent}%` }} />
                </div>
              </div>

              <div className="bg-gray-900/80 border border-gray-800 p-4 rounded-lg">
                <div className="text-xs text-gray-400 flex items-center justify-between">
                  <span>RAM USAGE</span>
                  <HardDrive size={14} className="text-purple-400" />
                </div>
                <div className="text-2xl font-bold text-white mt-2">{selectedDevice.memory_percent}%</div>
                <div className="w-full bg-gray-800 h-2 rounded-full mt-3 overflow-hidden">
                  <div className="bg-purple-500 h-full rounded-full transition-all duration-500" style={{ width: `${selectedDevice.memory_percent}%` }} />
                </div>
              </div>

              <div className="bg-gray-900/80 border border-gray-800 p-4 rounded-lg">
                <div className="text-xs text-gray-400 flex items-center justify-between">
                  <span>TEMPERATURE</span>
                  <Thermometer size={14} className="text-amber-400" />
                </div>
                <div className="text-2xl font-bold text-white mt-2">{selectedDevice.temperature_c}°C</div>
                <div className="w-full bg-gray-800 h-2 rounded-full mt-3 overflow-hidden">
                  <div className="bg-amber-500 h-full rounded-full transition-all duration-500" style={{ width: `${(selectedDevice.temperature_c / 100) * 100}%` }} />
                </div>
              </div>
            </div>
          </div>

          {/* Fault Injection Control Box */}
          <div className="bg-[#0f172a] border border-gray-800 rounded-xl p-6 shadow-2xl space-y-4">
            <h3 className="text-xs font-bold font-mono text-gray-200 uppercase tracking-wider flex items-center gap-2">
              <Zap size={16} className="text-amber-400" /> Hardware Fault Injection Control Panel
            </h3>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
              <button
                onClick={() => setFaultConfirm('CPU_OVERLOAD')}
                className="p-3 rounded-lg bg-gray-900 hover:bg-amber-500/10 border border-gray-800 hover:border-amber-500/40 font-bold text-gray-300 hover:text-amber-400 transition-all text-center"
              >
                CPU OVERLOAD
              </button>

              <button
                onClick={() => setFaultConfirm('MEMORY_PRESSURE')}
                className="p-3 rounded-lg bg-gray-900 hover:bg-purple-500/10 border border-gray-800 hover:border-purple-500/40 font-bold text-gray-300 hover:text-purple-400 transition-all text-center"
              >
                MEMORY PRESSURE
              </button>

              <button
                onClick={() => setFaultConfirm('CORRUPTED_FIRMWARE')}
                className="p-3 rounded-lg bg-gray-900 hover:bg-red-500/10 border border-gray-800 hover:border-red-500/40 font-bold text-gray-300 hover:text-red-400 transition-all text-center"
              >
                FIRMWARE CORRUPTED
              </button>

              <button
                onClick={() => setFaultConfirm('PROCESS_CRASH')}
                className="p-3 rounded-lg bg-gray-900 hover:bg-red-500/10 border border-gray-800 hover:border-red-500/40 font-bold text-gray-300 hover:text-red-400 transition-all text-center"
              >
                PROCESS CRASH
              </button>
            </div>

            {selectedDevice.active_fault && (
              <div className="pt-4 border-t border-gray-800 flex items-center justify-between font-mono">
                <span className="text-xs text-amber-400">Fault active on {selectedDevice.device_id}</span>
                <button
                  onClick={handleClearFault}
                  className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-all shadow-md"
                >
                  Clear Fault & Recover Node
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Confirmation Dialog */}
      <AnimatePresence>
        {faultConfirm && (
          <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-[#0f172a] border border-amber-500/40 rounded-xl p-6 max-w-md w-full shadow-2xl font-sans"
            >
              <div className="flex items-center gap-3 text-amber-400 mb-3">
                <AlertTriangle size={24} />
                <h4 className="text-lg font-bold">Confirm Hardware Fault Injection</h4>
              </div>

              <p className="text-xs text-gray-300 leading-relaxed font-mono">
                You are about to inject fault <strong>{faultConfirm}</strong> into node <strong>{selectedDeviceId}</strong>. This will transition node state to DEGRADED.
              </p>

              <div className="flex justify-end gap-3 mt-6">
                <button
                  onClick={() => setFaultConfirm(null)}
                  className="px-4 py-2 rounded-lg bg-gray-900 border border-gray-800 text-gray-300 hover:text-white text-xs font-bold font-mono"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleInjectFault(faultConfirm)}
                  disabled={injecting}
                  className="px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold font-mono transition-all shadow-lg"
                >
                  {injecting ? 'Injecting Fault...' : 'Confirm Injection'}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
