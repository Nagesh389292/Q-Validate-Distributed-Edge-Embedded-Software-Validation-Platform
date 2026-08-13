import sqlite3
import os
import json
import time
import uuid
from typing import List, Optional, Dict

try:
    import psycopg2
    from psycopg2 import pool, extras
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

from qvalidate.models import TestRunSummary, TestCaseResult, DefectTicket, DeviceStatus
from qvalidate.capabilities import DEVICE_FARM_CAPABILITIES

class DatabaseManager:
    """
    Enterprise Dual-Backend Database Manager.
    Supports local SQLite and production PostgreSQL with connection pooling,
    atomic device reservation invariants (successful_reservations <= 1),
    transaction rollback, and stale reservation auto-recovery.
    """
    _pg_pool = None

    def __init__(self, db_path: str = None, backend: str = None):
        self.backend = (backend or os.environ.get("DATABASE_BACKEND", "sqlite")).lower()
        if db_path is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            db_path = os.path.join(base_dir, "database", "qvalidate.db")
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        if self.backend == "postgres" and HAS_POSTGRES and DatabaseManager._pg_pool is None:
            try:
                pg_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL", "postgresql://postgres:postgres@localhost:5432/qvalidate")
                DatabaseManager._pg_pool = psycopg2.pool.ThreadedConnectionPool(1, 20, dsn=pg_url)
            except Exception as e:
                print(f"[DatabaseManager] PostgreSQL pool init fallback to SQLite: {e}")
                self.backend = "sqlite"

        self.init_db()

    def get_connection(self):
        if self.backend == "postgres" and DatabaseManager._pg_pool:
            conn = DatabaseManager._pg_pool.getconn()
            conn.autocommit = False
            return conn
        else:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row
            return conn

    def release_connection(self, conn):
        if self.backend == "postgres" and DatabaseManager._pg_pool:
            DatabaseManager._pg_pool.putconn(conn)
        else:
            conn.close()

    def _cursor(self, conn):
        if self.backend == "postgres" and HAS_POSTGRES:
            return conn.cursor(cursor_factory=extras.RealDictCursor)
        return conn.cursor()

    def _execute(self, cur, sql: str, params=None):
        if self.backend == "postgres":
            sql = sql.replace("?", "%s")
        if params is not None:
            cur.execute(sql, params)
        else:
            cur.execute(sql)

    def upsert_device(self, device_id: str, name: str, status: str = "READY", capabilities: List[str] = None):
        caps_json = json.dumps(capabilities or ["CPU", "MEMORY"])
        platform_type = "CPU_AI" if "AI_ACCELERATOR" in (capabilities or []) else "STANDARD_EDGE"
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            if self.backend == "postgres":
                cur.execute("""
                    INSERT INTO devices (device_id, name, platform_type, status, firmware_version, capabilities_json, cpu_usage_pct, memory_used_mb, temperature_celsius, is_reserved)
                    VALUES (%s, %s, %s, %s, '4.2.1', %s, 12.5, 1024.0, 42.0, 0)
                    ON CONFLICT(device_id) DO UPDATE SET
                        status=EXCLUDED.status,
                        capabilities_json=EXCLUDED.capabilities_json,
                        is_reserved=0
                """, (device_id, name, platform_type, status, caps_json))
            else:
                cur.execute("""
                    INSERT INTO devices (device_id, name, platform_type, status, firmware_version, capabilities_json, cpu_usage_pct, memory_used_mb, temperature_celsius, is_reserved)
                    VALUES (?, ?, ?, ?, '4.2.1', ?, 12.5, 1024.0, 42.0, 0)
                    ON CONFLICT(device_id) DO UPDATE SET
                        status=excluded.status,
                        capabilities_json=excluded.capabilities_json,
                        is_reserved=0
                """, (device_id, name, platform_type, status, caps_json))
            conn.commit()
        finally:
            self.release_connection(conn)

    def init_db(self):
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "schema.sql"),
            os.path.join(os.path.dirname(__file__), "..", "schema.sql"),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "database", "schema.sql")),
        ]
        schema_path = None
        for p in possible_paths:
            if os.path.exists(p):
                schema_path = p
                break
        if not schema_path:
            schema_path = possible_paths[0]
        
        with open(schema_path, "r") as f:
            sql_script = f.read()

        sqlite_script = sql_script.replace("REAL", "NUMERIC").replace("TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "TEXT DEFAULT (datetime('now'))")

        conn = self.get_connection()
        try:
            if self.backend == "postgres":
                cur = conn.cursor()
                try:
                    cur.execute(sql_script)
                    conn.commit()
                except Exception:
                    conn.rollback()
                try:
                    cur.execute("ALTER TABLE builds ADD COLUMN branch VARCHAR(64) DEFAULT 'main'")
                    conn.commit()
                except Exception:
                    conn.rollback()
            else:
                conn.executescript(sqlite_script)
                cur = conn.cursor()
                cur.execute("PRAGMA table_info(devices)")
                cols = [r[1] for r in cur.fetchall()]
                if "capabilities_json" not in cols:
                    conn.execute("ALTER TABLE devices ADD COLUMN capabilities_json TEXT DEFAULT '[\"CPU\",\"MEMORY\"]'")
                if "is_reserved" not in cols:
                    conn.execute("ALTER TABLE devices ADD COLUMN is_reserved INT DEFAULT 0")
                if "reserved_at" not in cols:
                    conn.execute("ALTER TABLE devices ADD COLUMN reserved_at REAL DEFAULT 0.0")
                try:
                    conn.execute("ALTER TABLE builds ADD COLUMN branch TEXT DEFAULT 'main'")
                except Exception:
                    pass
                conn.commit()
        finally:
            self.release_connection(conn)

        self.seed_defaults()

    def seed_defaults(self):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            try:
                cur.execute("SELECT COUNT(*) FROM devices")
                count = cur.fetchone()[0]
            except Exception:
                if self.backend == "postgres":
                    conn.rollback()
                count = 0

            if count == 0:
                for dev_id, caps in DEVICE_FARM_CAPABILITIES.items():
                    platform_type = "CPU_AI" if "AI_ACCELERATOR" in caps else ("DSP_WORKLOAD" if "DSP" in caps else "NET_ROUTER")
                    caps_json = json.dumps(caps)
                    if self.backend == "postgres":
                        try:
                            cur.execute("""
                                INSERT INTO devices (device_id, name, platform_type, status, firmware_version, capabilities_json, cpu_usage_pct, memory_used_mb, temperature_celsius)
                                VALUES (%s, %s, %s, 'READY', '4.2.1', %s, 12.5, 1024.0, 42.0)
                            """, (dev_id, f"Qualcomm Edge Node {dev_id.split('-')[-1]}", platform_type, caps_json))
                        except Exception:
                            conn.rollback()
                    else:
                        cur.execute("""
                            INSERT INTO devices (device_id, name, platform_type, status, firmware_version, capabilities_json, cpu_usage_pct, memory_used_mb, temperature_celsius)
                            VALUES (?, ?, ?, 'READY', '4.2.1', ?, 12.5, 1024.0, 42.0)
                        """, (dev_id, f"Qualcomm Edge Node {dev_id.split('-')[-1]}", platform_type, caps_json))
                
                try:
                    cur.execute("""
                        INSERT INTO builds (build_id, version, git_commit, branch, status)
                        VALUES ('BUILD-1042', '4.2.1', 'a82f9c1b4e3f', 'release/4.2', 'RELEASED'),
                               ('BUILD-1041', '4.2.0', '9c7e4a2d1f00', 'release/4.2', 'PASSED')
                    """)
                except Exception:
                    if self.backend == "postgres":
                        conn.rollback()
                    try:
                        cur.execute("""
                            INSERT INTO builds (build_id, version, git_commit, status)
                            VALUES ('BUILD-1042', '4.2.1', 'a82f9c1b4e3f', 'RELEASED'),
                                   ('BUILD-1041', '4.2.0', '9c7e4a2d1f00', 'PASSED')
                        """)
                    except Exception:
                        if self.backend == "postgres":
                            conn.rollback()
                try:
                    cur.execute("""
                        INSERT INTO components (component_id, name, description)
                        VALUES ('COMP-BOOT', 'Bootloader Subsystem', 'Platform power-on, initialization, hardware sanity check'),
                               ('COMP-MEM', 'Memory Manager', 'Dynamic heap allocation, paging, leak detection'),
                               ('COMP-CPU', 'CPU Scheduler', 'Core utilization, thread priority management'),
                               ('COMP-PERF', 'Performance Benchmarks', 'Latency and throughput measurements'),
                               ('COMP-DSP', 'Hexagon DSP Coprocessor', 'Signal processing & audio stream processing'),
                               ('COMP-AI', 'AI Edge Accelerator', 'Tensor flow inference workload engine')
                    """)
                except Exception:
                    if self.backend == "postgres":
                        conn.rollback()

                try:
                    cur.execute("""
                        INSERT INTO test_cases (test_id, name, category, component_id, required_capability, description, expected_result)
                        VALUES ('BOOT-001', 'Device Boot Sequence Verification', 'BOOT', 'COMP-BOOT', 'CPU', 'Verify device cold boot into READY state', 'Boot time < 5.0s, State == READY'),
                               ('MEM-003', 'Memory Stress Allocation Test', 'MEMORY', 'COMP-MEM', 'MEMORY', 'Allocate 500MB RAM blocks and verify no OOM', 'Memory allocated successfully'),
                               ('CPU-007', 'CPU Load Balancing Under Stress', 'CPU', 'COMP-CPU', 'CPU', 'Run 8-core benchmark at 85% capacity', 'CPU temp < 85C, Health > 70'),
                               ('PERF-021', 'API Latency Threshold Test', 'PERF', 'COMP-PERF', 'CPU', 'Measure execution latency across 100 requests', 'Latency < 10.0ms'),
                               ('FAULT-005', 'CPU Overload Recovery Verification', 'FAULT', 'COMP-CPU', 'CPU', 'Inject CPU fault and verify graceful degraded handling', 'State == DEGRADED during fault, READY after clear'),
                               ('DSP-012', 'Hexagon DSP Audio FFT Processing Test', 'DSP', 'COMP-DSP', 'DSP', 'Execute 1024-point FFT transform on DSP co-processor', 'DSP execution latency < 2.5ms'),
                               ('AI-045', 'Qualcomm Neural Processing Engine Inference Test', 'AI', 'COMP-AI', 'AI_ACCELERATOR', 'Run ResNet-50 INT8 inference benchmark', 'Throughput > 450 FPS')
                    """)
                except Exception:
                    if self.backend == "postgres":
                        conn.rollback()

                try:
                    cur.execute("""
                        INSERT INTO test_suites (suite_id, name, description)
                        VALUES ('SUITE-SANITY', 'Sanity & Smoke Test Suite', 'Basic platform stability test suite'),
                               ('SUITE-REGRESSION', 'Full Regression Test Suite', 'Comprehensive test suite for release verification'),
                               ('SUITE-DISTRIBUTED', 'Distributed Hardware Farm Benchmark', 'Full 50-test multi-node parallel workload')
                    """)
                except Exception:
                    if self.backend == "postgres":
                        conn.rollback()

                conn.commit()
        finally:
            self.release_connection(conn)

    # Device Operations
    def get_all_devices(self) -> List[Dict]:
        conn = self.get_connection()
        try:
            cur = self._cursor(conn)
            self._execute(cur, "SELECT * FROM devices")
            rows = [dict(r) for r in cur.fetchall()]
            for r in rows:
                dev_id = r["device_id"]
                if dev_id in DEVICE_FARM_CAPABILITIES:
                    r["capabilities"] = DEVICE_FARM_CAPABILITIES[dev_id]
                elif "capabilities_json" in r and r["capabilities_json"]:
                    try: r["capabilities"] = json.loads(r["capabilities_json"])
                    except: r["capabilities"] = ["CPU", "MEMORY"]
                else:
                    r["capabilities"] = ["CPU", "MEMORY"]
            return rows
        finally:
            self.release_connection(conn)

    def get_device(self, device_id: str) -> Optional[Dict]:
        conn = self.get_connection()
        try:
            cur = self._cursor(conn)
            self._execute(cur, "SELECT * FROM devices WHERE device_id = ?", (device_id,))
            row = cur.fetchone()
            if not row: return None
            data = dict(row)
            if device_id in DEVICE_FARM_CAPABILITIES:
                data["capabilities"] = DEVICE_FARM_CAPABILITIES[device_id]
            elif "capabilities_json" in data and data["capabilities_json"]:
                try: data["capabilities"] = json.loads(data["capabilities_json"])
                except: data["capabilities"] = ["CPU", "MEMORY"]
            else:
                data["capabilities"] = ["CPU", "MEMORY"]
            return data
        finally:
            self.release_connection(conn)

    def reserve_device(self, device_id: str) -> bool:
        """Atomic Device Lock Acquisition. Invariant: successful_reservations <= 1."""
        now_ts = time.time()
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            if self.backend == "postgres":
                cur.execute("UPDATE devices SET is_reserved = 1, reserved_at = %s WHERE device_id = %s AND is_reserved = 0", (now_ts, device_id))
            else:
                cur.execute("UPDATE devices SET is_reserved = 1, reserved_at = ? WHERE device_id = ? AND is_reserved = 0", (now_ts, device_id))
            conn.commit()
            return cur.rowcount > 0
        except Exception:
            conn.rollback()
            return False
        finally:
            self.release_connection(conn)

    def release_device(self, device_id: str):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            if self.backend == "postgres":
                cur.execute("UPDATE devices SET is_reserved = 0 WHERE device_id = %s", (device_id,))
            else:
                cur.execute("UPDATE devices SET is_reserved = 0 WHERE device_id = ?", (device_id,))
            conn.commit()
        finally:
            self.release_connection(conn)

    def recover_stale_reservations(self, timeout_sec: float = 30.0) -> int:
        """Auto-recovers devices reserved longer than timeout_sec due to worker crashes."""
        cutoff_ts = time.time() - timeout_sec
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            if self.backend == "postgres":
                cur.execute("UPDATE devices SET is_reserved = 0 WHERE is_reserved = 1 AND reserved_at < %s", (cutoff_ts,))
            else:
                cur.execute("UPDATE devices SET is_reserved = 0 WHERE is_reserved = 1 AND reserved_at < ?", (cutoff_ts,))
            conn.commit()
            return cur.rowcount
        finally:
            self.release_connection(conn)

    def update_device_status(self, device_id: str, status: str, cpu: float = None, mem: float = None, temp: float = None):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE devices 
                SET status = ?, 
                    cpu_usage_pct = COALESCE(?, cpu_usage_pct), 
                    memory_used_mb = COALESCE(?, memory_used_mb), 
                    temperature_celsius = COALESCE(?, temperature_celsius),
                    updated_at = datetime('now')
                WHERE device_id = ?
            """, (status, cpu, mem, temp, device_id))
            conn.commit()
        finally:
            self.release_connection(conn)

    # Build Operations
    def create_build(self, build_id: str, version: str, git_commit: str, branch: str = 'main') -> Dict:
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO builds (build_id, version, git_commit, branch, status)
                VALUES (?, ?, ?, ?, 'CREATED')
            """, (build_id, version, git_commit, branch))
            conn.commit()
        finally:
            self.release_connection(conn)
        return self.get_build(build_id)

    def get_build(self, build_id: str) -> Optional[Dict]:
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM builds WHERE build_id = ?", (build_id,))
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            self.release_connection(conn)

    def get_all_builds(self) -> List[Dict]:
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM builds ORDER BY created_at DESC")
            return [dict(row) for row in cur.fetchall()]
        finally:
            self.release_connection(conn)

    def update_build_status(self, build_id: str, status: str):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("UPDATE builds SET status = ? WHERE build_id = ?", (status, build_id))
            conn.commit()
        finally:
            self.release_connection(conn)

    def create_test_run(self, run_id: str, build_id: str, device_id: str, suite_id: str) -> Dict:
        now_str = str(time.time())
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO test_runs (run_id, build_id, device_id, suite_id, status, start_time, total_tests, passed_tests, failed_tests, skipped_tests)
                VALUES (?, ?, ?, ?, 'RUNNING', ?, 0, 0, 0, 0)
            """, (run_id, build_id, device_id, suite_id, now_str))
            conn.commit()
        finally:
            self.release_connection(conn)
        return self.get_test_run(run_id)

    def update_test_run_status(self, run_id: str, status: str):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE test_runs 
                SET status = ?, 
                    end_time = CASE WHEN ? IN ('PASSED', 'FAILED', 'CANCELLED', 'TIMEOUT') THEN datetime('now') ELSE end_time END
                WHERE run_id = ?
            """, (status, status, run_id))
            conn.commit()
        finally:
            self.release_connection(conn)

    def save_test_run(self, summary: TestRunSummary):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO test_runs (run_id, build_id, device_id, suite_id, status, start_time, end_time, duration_sec, total_tests, passed_tests, failed_tests, skipped_tests)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                summary.run_id, summary.build_id, summary.device_id, summary.suite_id,
                summary.status, str(summary.start_time), str(summary.end_time),
                summary.end_time - summary.start_time, summary.total_tests,
                summary.passed_tests, summary.failed_tests, summary.skipped_tests
            ))

            for res in summary.results:
                metrics_json = json.dumps([{"ts": m.timestamp, "cpu": m.cpu_pct, "mem": m.memory_mb, "temp": m.temp_celsius} for m in res.metrics])
                cur.execute("""
                    INSERT OR REPLACE INTO test_results (result_id, run_id, test_id, status, duration_sec, actual_result, expected_result, error_log, metrics_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"RES-{summary.run_id}-{res.test_id}", summary.run_id, res.test_id,
                    res.status.value, res.duration_sec, res.actual_result, res.expected_result,
                    res.error_log, metrics_json
                ))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.release_connection(conn)

    def get_test_run(self, run_id: str) -> Optional[Dict]:
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM test_runs WHERE run_id = ?", (run_id,))
            row = cur.fetchone()
            if not row:
                return None
            data = dict(row)
            cur.execute("SELECT * FROM test_results WHERE run_id = ?", (run_id,))
            data["results"] = [dict(r) for r in cur.fetchall()]
            return data
        finally:
            self.release_connection(conn)

    def get_all_test_runs(self) -> List[Dict]:
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM test_runs ORDER BY start_time DESC")
            return [dict(row) for row in cur.fetchall()]
        finally:
            self.release_connection(conn)

    def get_all_components(self) -> List[Dict]:
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM components")
            return [dict(row) for row in cur.fetchall()]
        finally:
            self.release_connection(conn)

    def get_all_test_cases(self) -> List[Dict]:
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM test_cases")
            return [dict(row) for row in cur.fetchall()]
        finally:
            self.release_connection(conn)

    def get_all_test_suites(self) -> List[Dict]:
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM test_suites")
            return [dict(row) for row in cur.fetchall()]
        finally:
            self.release_connection(conn)

    def create_defect(self, defect: DefectTicket):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO defects (defect_id, title, severity, status, component_name, first_failing_build, affected_tests, root_cause)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                defect.defect_id, defect.title, defect.severity, defect.status,
                defect.component_name, defect.first_failing_build,
                ",".join(defect.affected_tests), defect.root_cause
            ))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.release_connection(conn)

    def get_all_defects(self) -> List[Dict]:
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM defects ORDER BY created_at DESC")
            return [dict(row) for row in cur.fetchall()]
        finally:
            self.release_connection(conn)

    def get_defect(self, defect_id: str) -> Optional[Dict]:
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM defects WHERE defect_id = ?", (defect_id,))
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            self.release_connection(conn)

    def update_defect_status(self, defect_id: str, status: str, root_cause: str = None):
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE defects 
                SET status = ?, 
                    root_cause = COALESCE(?, root_cause)
                WHERE defect_id = ?
            """, (status, root_cause, defect_id))
            conn.commit()
        finally:
            self.release_connection(conn)
