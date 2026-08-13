from fastapi import APIRouter
from qvalidate.scheduler import DistributedTestScheduler
from qvalidate.distributed_runner import DistributedTestWorkerPool
from qvalidate.event_bus import EventBus
from run_phase6c_comparative_benchmark import execute_benchmark_pass

router = APIRouter(prefix="/scheduler", tags=["Distributed Test Scheduler"])
scheduler = DistributedTestScheduler()

@router.get("/queue", response_model=dict)
def get_queue_status():
    """Retrieve active test queue depth, worker utilization, and queued jobs."""
    return scheduler.get_queue_status()

@router.get("/events", response_model=dict)
def get_event_bus_log():
    """Get recent Kafka / EventBus execution event log."""
    bus = EventBus()
    return {"total_events": len(bus.get_events()), "events": bus.get_events(30)}

@router.post("/benchmark", response_model=dict)
def run_parallel_benchmark():
    """Trigger parallel test execution benchmark comparing sequential vs 10x parallel speedup."""
    test_workload = [
        {"test_id": "BOOT-001", "name": "Cold Boot Sanity Check", "required_capability": "CPU"},
        {"test_id": "MEM-003", "name": "Dynamic Memory Allocation", "required_capability": "MEMORY"},
        {"test_id": "CPU-007", "name": "Multicore Load Stress", "required_capability": "CPU"},
        {"test_id": "DSP-012", "name": "Hexagon DSP FFT Processing", "required_capability": "DSP"},
        {"test_id": "AI-045", "name": "ResNet-50 Neural Inference", "required_capability": "AI_ACCELERATOR"},
    ] * 4 # 20 test workload

    pool = DistributedTestWorkerPool(max_workers=10)
    res_seq = pool.run_workload(test_workload, mode="SEQUENTIAL")
    res_par = pool.run_workload(test_workload, mode="PARALLEL")

    speedup = round(res_seq['duration_sec'] / res_par['duration_sec'], 2) if res_par['duration_sec'] > 0 else 1.0

    return {
        "workload_size": len(test_workload),
        "sequential_duration_sec": res_seq['duration_sec'],
        "parallel_duration_sec": res_par['duration_sec'],
        "speedup_ratio": f"{speedup}x",
        "parallel_throughput_tps": res_par['tests_per_sec']
    }

@router.get("/comparative-benchmark", response_model=dict)
def get_comparative_benchmark_results():
    """Retrieve Phase 6C empirical persistence benchmark metrics across SQLite vs PostgreSQL."""
    scales = [10, 25, 50, 100]
    comparison_data = []

    for s in scales:
        s_sqlite = execute_benchmark_pass("sqlite", num_devices=s, test_count=20)
        s_pg = execute_benchmark_pass("postgres", num_devices=s, test_count=20)
        
        diff_tps_pct = round(((s_pg["real_tps"] - s_sqlite["real_tps"]) / max(s_sqlite["real_tps"], 0.1)) * 100.0, 1)

        comparison_data.append({
            "nodes": s,
            "sqlite": s_sqlite,
            "postgres": s_pg,
            "tps_diff_pct": diff_tps_pct
        })

    return {
        "workload_size": 20,
        "comparison": comparison_data
    }
