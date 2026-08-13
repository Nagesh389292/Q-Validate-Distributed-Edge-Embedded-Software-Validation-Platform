import axios from 'axios';
import { Device, Build, ComponentItem, TestCase, TestSuite, TestRun, Defect, TIAResponse } from './types';

const API_BASE_URL = typeof window !== 'undefined' ? '/api/v1' : 'http://127.0.0.1:8000/api/v1';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Devices
  getDevices: async (): Promise<Device[]> => (await client.get('/devices')).data,
  getDevice: async (id: string): Promise<Device> => (await client.get(`/devices/${id}`)).data,
  powerOnDevice: async (id: string) => (await client.post(`/devices/${id}/power-on`)).data,
  resetDevice: async (id: string, hardReset: boolean = false) => (await client.post(`/devices/${id}/reset`, null, { params: { hard_reset: hardReset } })).data,
  injectFault: async (id: string, faultType: string, intensity: number = 95.0) => (await client.post(`/devices/${id}/inject-fault`, { fault_type: faultType, intensity })).data,
  clearFault: async (id: string) => (await client.post(`/devices/${id}/clear-fault`)).data,

  // Builds
  getBuilds: async (): Promise<Build[]> => (await client.get('/builds')).data,
  createBuild: async (data: { build_id: string; version: string; git_commit: string; branch: string }): Promise<Build> => (await client.post('/builds', data)).data,
  getBuild: async (id: string): Promise<Build> => (await client.get(`/builds/${id}`)).data,

  // Catalogs
  getComponents: async (): Promise<ComponentItem[]> => (await client.get('/components')).data,
  getTestCases: async (): Promise<TestCase[]> => (await client.get('/test-cases')).data,
  getTestSuites: async (): Promise<TestSuite[]> => (await client.get('/test-suites')).data,

  // Test Runs
  getTestRuns: async (): Promise<TestRun[]> => (await client.get('/test-runs')).data,
  getTestRun: async (id: string): Promise<TestRun> => (await client.get(`/test-runs/${id}`)).data,
  triggerTestRun: async (data: { build_id: string; device_id: string; suite_id: string; max_retries?: number }): Promise<TestRun> => (await client.post('/test-runs', data)).data,
  cancelTestRun: async (id: string) => (await client.post(`/test-runs/${id}/cancel`)).data,

  // TIA
  analyzeImpact: async (changedFiles: string[]): Promise<TIAResponse> => (await client.post('/regressions/impact-analysis', { changed_files: changedFiles })).data,

  // Defects
  getDefects: async (): Promise<Defect[]> => (await client.get('/defects')).data,
  patchDefect: async (id: string, data: { status: string; root_cause?: string }): Promise<Defect> => (await client.patch(`/defects/${id}`, data)).data,

  // Diagnostics
  triggerTriage: async (runId: string) => (await client.post(`/diagnostics/triage/${runId}`)).data,

  // Health
  getHealth: async () => (await axios.get('http://127.0.0.1:8000/health')).data,
};
