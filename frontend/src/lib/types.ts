export interface Device {
  device_id: string;
  name: string;
  platform_type: string;
  status: 'ONLINE' | 'OFFLINE' | 'POWERED_OFF' | 'BOOTING' | 'READY' | 'DEGRADED' | 'ERROR';
  firmware_version: string;
  cpu_usage_pct: number;
  memory_used_mb: number;
  temperature_celsius: number;
  created_at?: string;
  updated_at?: string;
  active_fault?: string;
}

export interface Build {
  build_id: string;
  version: string;
  git_commit: string;
  branch: string;
  status: 'CREATED' | 'VALIDATING' | 'PASSED' | 'FAILED' | 'RELEASED';
  created_at: string;
}

export interface ComponentItem {
  component_id: string;
  name: string;
  description: string;
}

export interface TestCase {
  test_id: string;
  name: string;
  category: string;
  component_id: string;
  description: string;
  preconditions: string;
  expected_result: string;
}

export interface TestSuite {
  suite_id: string;
  name: string;
  description: string;
}

export interface TestCaseResult {
  result_id: string;
  run_id: string;
  test_id: string;
  status: 'PASS' | 'FAIL' | 'SKIP' | 'ERROR';
  duration_sec: number;
  actual_result: string;
  expected_result: string;
  error_log?: string;
  metrics_json?: string;
}

export interface TestRun {
  run_id: string;
  build_id: string;
  device_id: string;
  suite_id: string;
  status: 'QUEUED' | 'RUNNING' | 'PASSED' | 'FAILED' | 'CANCELLED' | 'TIMEOUT';
  start_time?: string;
  end_time?: string;
  duration_sec?: number;
  total_tests?: number;
  passed_tests?: number;
  failed_tests?: number;
  skipped_tests?: number;
  results?: TestCaseResult[];
}

export interface Defect {
  defect_id: string;
  title: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'OPEN' | 'TRIAGED' | 'RESOLVED';
  component_name: string;
  first_failing_build: string;
  affected_tests: string;
  root_cause?: string;
  created_at: string;
}

export interface TIAResponse {
  changed_files: string[];
  impacted_component_ids: string[];
  selected_test_count: number;
  selected_tests: Array<{
    test_id: string;
    name: string;
    category: string;
    component_id: string;
    component_name: string;
  }>;
}
