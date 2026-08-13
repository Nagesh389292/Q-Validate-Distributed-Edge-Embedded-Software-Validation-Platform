-- Q-Validate Database Schema (PostgreSQL & SQLite compatible)

CREATE TABLE IF NOT EXISTS devices (
    device_id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    platform_type VARCHAR(64) NOT NULL, -- e.g., CPU, DSP, AI_EDGE
    status VARCHAR(32) NOT NULL DEFAULT 'OFFLINE',
    firmware_version VARCHAR(64) DEFAULT '1.0.0',
    capabilities_json TEXT DEFAULT '["CPU","MEMORY"]',
    cpu_usage_pct REAL DEFAULT 0.0,
    memory_used_mb REAL DEFAULT 0.0,
    temperature_celsius REAL DEFAULT 40.0,
    is_reserved INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS builds (
    build_id VARCHAR(64) PRIMARY KEY,
    component_name VARCHAR(128) NOT NULL DEFAULT 'firmware-core',
    version VARCHAR(64) NOT NULL,
    git_commit VARCHAR(64) NOT NULL,
    branch VARCHAR(64) DEFAULT 'main',
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS components (
    component_id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS test_cases (
    test_id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    category VARCHAR(64) NOT NULL,
    component_id VARCHAR(64),
    required_capability VARCHAR(64) DEFAULT 'CPU',
    description TEXT,
    expected_result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS test_suites (
    suite_id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS test_runs (
    run_id VARCHAR(64) PRIMARY KEY,
    build_id VARCHAR(64) NOT NULL,
    device_id VARCHAR(64),
    suite_id VARCHAR(64),
    status VARCHAR(32) NOT NULL DEFAULT 'CREATED',
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_tests INT DEFAULT 0,
    passed_tests INT DEFAULT 0,
    failed_tests INT DEFAULT 0,
    skipped_tests INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY(build_id) REFERENCES builds(build_id)
);

CREATE TABLE IF NOT EXISTS test_results (
    result_id VARCHAR(64) PRIMARY KEY,
    run_id VARCHAR(64) NOT NULL,
    test_name VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL, -- PASSED, FAILED, SKIPPED
    execution_time_ms REAL DEFAULT 0.0,
    device_id VARCHAR(64),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(run_id) REFERENCES test_runs(run_id)
);

CREATE TABLE IF NOT EXISTS defects (
    defect_id VARCHAR(64) PRIMARY KEY,
    run_id VARCHAR(64) NOT NULL,
    test_name VARCHAR(128) NOT NULL,
    severity VARCHAR(32) NOT NULL DEFAULT 'HIGH',
    status VARCHAR(32) NOT NULL DEFAULT 'OPEN',
    stack_trace TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(run_id) REFERENCES test_runs(run_id)
);

CREATE TABLE IF NOT EXISTS test_impact_analysis (
    commit_id VARCHAR(64) PRIMARY KEY,
    modified_files TEXT NOT NULL,
    impacted_tests TEXT NOT NULL,
    confidence_score REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
