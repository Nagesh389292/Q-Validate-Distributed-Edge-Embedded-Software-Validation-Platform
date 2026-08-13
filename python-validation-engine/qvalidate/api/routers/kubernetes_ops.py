"""
kubernetes_ops.py — Live Kubernetes Cluster API Router

Provides real-time cluster data by calling the Kubernetes API using in-cluster
ServiceAccount credentials (automatically mounted at /var/run/secrets/kubernetes.io/).

Endpoints:
  GET  /api/v1/kubernetes/cluster       — Node info, K8s version, pod totals
  GET  /api/v1/kubernetes/deployments   — All deployments with replica health
  GET  /api/v1/kubernetes/pods          — All pods with status, restarts, age
  POST /api/v1/kubernetes/scale/{name}  — Scale a deployment to ?replicas=N
  DELETE /api/v1/kubernetes/pod/{name}  — Delete (kill) a pod (chaos lab)
  POST /api/v1/kubernetes/rollout-restart/{name} — Rolling restart a deployment
"""

import time
import datetime
import logging
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/kubernetes", tags=["Kubernetes Operations"])

NAMESPACE = "qvalidate-system"

def _get_k8s_clients():
    """
    Load in-cluster config (injected by Kubernetes ServiceAccount) and return
    CoreV1Api and AppsV1Api clients. Falls back gracefully when running locally.
    """
    try:
        from kubernetes import client, config as k8s_config
        try:
            k8s_config.load_incluster_config()
        except Exception:
            # Fallback for local development
            k8s_config.load_kube_config()
        core = client.CoreV1Api()
        apps = client.AppsV1Api()
        auto = client.AutoscalingV2Api()
        return core, apps, auto
    except Exception as e:
        logger.error(f"Failed to load Kubernetes config: {e}")
        raise HTTPException(status_code=503, detail=f"Kubernetes API unavailable: {str(e)}")


def _age_str(timestamp) -> str:
    """Convert a k8s timestamp to a human-readable age string."""
    if timestamp is None:
        return "unknown"
    now = datetime.datetime.now(datetime.timezone.utc)
    delta = now - timestamp
    secs = int(delta.total_seconds())
    if secs < 60:
        return f"{secs}s"
    elif secs < 3600:
        return f"{secs // 60}m"
    elif secs < 86400:
        return f"{secs // 3600}h"
    else:
        return f"{secs // 86400}d"


@router.get("/cluster", response_model=dict)
def get_cluster_info():
    """
    Return live Kubernetes cluster information:
    node name, K8s version, OS, container runtime, total pod count,
    and a per-deployment summary.
    """
    core, apps, _ = _get_k8s_clients()

    # Node information
    nodes = core.list_node()
    node_data = []
    for n in nodes.items:
        status_conds = {c.type: c.status for c in (n.status.conditions or [])}
        ready = status_conds.get("Ready", "Unknown") == "True"
        node_data.append({
            "name": n.metadata.name,
            "ready": ready,
            "kubernetes_version": n.status.node_info.kubelet_version if n.status.node_info else "unknown",
            "os_image": n.status.node_info.os_image if n.status.node_info else "unknown",
            "container_runtime": n.status.node_info.container_runtime_version if n.status.node_info else "unknown",
            "architecture": n.status.node_info.architecture if n.status.node_info else "unknown",
        })

    # Pod counts in our namespace
    pods = core.list_namespaced_pod(namespace=NAMESPACE)
    total_pods = len(pods.items)
    running_pods = sum(1 for p in pods.items if p.status.phase == "Running")

    # Deployment summary
    deps = apps.list_namespaced_deployment(namespace=NAMESPACE)
    deployment_summary = []
    total_desired = 0
    total_ready = 0
    for d in deps.items:
        desired = d.spec.replicas or 0
        ready = d.status.ready_replicas or 0
        total_desired += desired
        total_ready += ready
        deployment_summary.append({
            "name": d.metadata.name,
            "desired": desired,
            "ready": ready,
            "available": d.status.available_replicas or 0,
        })

    k8s_version = node_data[0]["kubernetes_version"] if node_data else "unknown"

    return {
        "cluster_connected": True,
        "timestamp": time.time(),
        "kubernetes_version": k8s_version,
        "namespace": NAMESPACE,
        "nodes": node_data,
        "pod_totals": {
            "total": total_pods,
            "running": running_pods,
        },
        "replica_totals": {
            "desired": total_desired,
            "ready": total_ready,
        },
        "deployment_summary": deployment_summary,
    }


@router.get("/deployments", response_model=dict)
def get_deployments():
    """
    Return all deployments in qvalidate-system with full replica health,
    image names, conditions, and resource limits.
    """
    _, apps, _ = _get_k8s_clients()

    deps = apps.list_namespaced_deployment(namespace=NAMESPACE)
    result = []
    for d in deps.items:
        containers = d.spec.template.spec.containers or []
        images = [c.image for c in containers]
        conditions = []
        for cond in (d.status.conditions or []):
            conditions.append({
                "type": cond.type,
                "status": cond.status,
                "reason": cond.reason,
                "message": cond.message,
            })

        result.append({
            "name": d.metadata.name,
            "namespace": d.metadata.namespace,
            "desired_replicas": d.spec.replicas or 0,
            "ready_replicas": d.status.ready_replicas or 0,
            "available_replicas": d.status.available_replicas or 0,
            "updated_replicas": d.status.updated_replicas or 0,
            "images": images,
            "conditions": conditions,
            "created_at": d.metadata.creation_timestamp.isoformat() if d.metadata.creation_timestamp else None,
            "age": _age_str(d.metadata.creation_timestamp),
        })

    total_desired = sum(d["desired_replicas"] for d in result)
    total_ready = sum(d["ready_replicas"] for d in result)

    return {
        "namespace": NAMESPACE,
        "timestamp": time.time(),
        "total_desired": total_desired,
        "total_ready": total_ready,
        "all_healthy": total_desired == total_ready and total_desired > 0,
        "deployments": result,
    }


@router.get("/pods", response_model=dict)
def get_pods():
    """
    Return all pods in qvalidate-system with status, node, IPs,
    restart counts, and ages.
    """
    core, _, _ = _get_k8s_clients()

    pods = core.list_namespaced_pod(namespace=NAMESPACE)
    result = []
    for p in pods.items:
        restarts = 0
        containers_ready = 0
        total_containers = len(p.spec.containers) if p.spec.containers else 0

        if p.status.container_statuses:
            for cs in p.status.container_statuses:
                restarts += cs.restart_count
                if cs.ready:
                    containers_ready += 1

        result.append({
            "name": p.metadata.name,
            "namespace": p.metadata.namespace,
            "node": p.spec.node_name,
            "pod_ip": p.status.pod_ip,
            "phase": p.status.phase,
            "ready": f"{containers_ready}/{total_containers}",
            "restarts": restarts,
            "age": _age_str(p.metadata.creation_timestamp),
            "created_at": p.metadata.creation_timestamp.isoformat() if p.metadata.creation_timestamp else None,
        })

    # Sort: running first, then by name
    result.sort(key=lambda x: (x["phase"] != "Running", x["name"]))

    return {
        "namespace": NAMESPACE,
        "timestamp": time.time(),
        "total": len(result),
        "running": sum(1 for p in result if p["phase"] == "Running"),
        "pods": result,
    }


@router.post("/scale/{deployment_name}", response_model=dict)
def scale_deployment(deployment_name: str, replicas: int = Query(..., ge=1, le=100)):
    """
    Scale a deployment to the specified replica count.
    Used for live device farm scaling from the UI.
    """
    _, apps, _ = _get_k8s_clients()

    try:
        # Patch the scale subresource
        body = {"spec": {"replicas": replicas}}
        apps.patch_namespaced_deployment_scale(
            name=deployment_name,
            namespace=NAMESPACE,
            body=body
        )

        # Read back current state
        dep = apps.read_namespaced_deployment(name=deployment_name, namespace=NAMESPACE)
        return {
            "success": True,
            "deployment": deployment_name,
            "desired_replicas": dep.spec.replicas,
            "message": f"Deployment '{deployment_name}' scaled to {replicas} replicas",
            "timestamp": time.time(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scale failed: {str(e)}")


@router.delete("/pod/{pod_name}", response_model=dict)
def delete_pod(pod_name: str):
    """
    Delete (kill) a specific pod. Kubernetes will immediately create a
    replacement via ReplicaSet reconciliation. Used in the Chaos / Resilience Lab.
    """
    core, _, _ = _get_k8s_clients()

    try:
        from kubernetes import client as k8s_client
        core.delete_namespaced_pod(
            name=pod_name,
            namespace=NAMESPACE,
            body=k8s_client.V1DeleteOptions(grace_period_seconds=0)
        )
        return {
            "success": True,
            "deleted_pod": pod_name,
            "message": f"Pod '{pod_name}' terminated. Kubernetes will self-heal.",
            "timestamp": time.time(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pod deletion failed: {str(e)}")


@router.post("/rollout-restart/{deployment_name}", response_model=dict)
def rollout_restart(deployment_name: str):
    """
    Trigger a rolling restart of a deployment by patching the pod template
    annotation with the current timestamp. Zero-downtime.
    """
    _, apps, _ = _get_k8s_clients()

    try:
        now = datetime.datetime.utcnow().isoformat() + "Z"
        body = {
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "kubectl.kubernetes.io/restartedAt": now
                        }
                    }
                }
            }
        }
        apps.patch_namespaced_deployment(
            name=deployment_name,
            namespace=NAMESPACE,
            body=body
        )
        return {
            "success": True,
            "deployment": deployment_name,
            "restarted_at": now,
            "message": f"Rolling restart triggered for '{deployment_name}'",
            "timestamp": time.time(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rollout restart failed: {str(e)}")


@router.get("/services", response_model=dict)
def get_services():
    """Return all services in qvalidate-system."""
    core, _, _ = _get_k8s_clients()
    svcs = core.list_namespaced_service(namespace=NAMESPACE)
    result = []
    for s in svcs.items:
        ports = []
        for p in (s.spec.ports or []):
            port_entry = {"port": p.port, "target_port": str(p.target_port), "protocol": p.protocol}
            if p.node_port:
                port_entry["node_port"] = p.node_port
            ports.append(port_entry)
        result.append({
            "name": s.metadata.name,
            "type": s.spec.type,
            "cluster_ip": s.spec.cluster_ip,
            "ports": ports,
        })
    return {
        "namespace": NAMESPACE,
        "timestamp": time.time(),
        "services": result,
    }


@router.get("/hpa", response_model=dict)
def get_hpa_status():
    """Return all HorizontalPodAutoscalers in qvalidate-system."""
    _, _, auto = _get_k8s_clients()
    try:
        hpas = auto.list_namespaced_horizontal_pod_autoscaler(namespace=NAMESPACE)
        result = []
        for h in hpas.items:
            current_cpu = None
            if h.status and h.status.current_metrics:
                for m in h.status.current_metrics:
                    if m.type == "Resource" and m.resource and m.resource.name == "cpu":
                        current_cpu = m.resource.current.average_utilization

            target_cpu = None
            if h.spec.metrics:
                for m in h.spec.metrics:
                    if m.type == "Resource" and m.resource and m.resource.name == "cpu":
                        target_cpu = m.resource.target.average_utilization

            result.append({
                "name": h.metadata.name,
                "target_deployment": h.spec.scale_target_ref.name,
                "min_replicas": h.spec.min_replicas,
                "max_replicas": h.spec.max_replicas,
                "current_replicas": h.status.current_replicas if h.status else 0,
                "desired_replicas": h.status.desired_replicas if h.status else 0,
                "current_cpu_utilization": current_cpu,
                "target_cpu_utilization": target_cpu,
            })
        return {
            "namespace": NAMESPACE,
            "timestamp": time.time(),
            "hpas": result,
        }
    except Exception as e:
        logger.warning(f"Failed to query HPA: {e}")
        return {
            "namespace": NAMESPACE,
            "timestamp": time.time(),
            "hpas": [],
            "error": str(e),
        }


@router.post("/stress", response_model=dict)
def trigger_cpu_stress(duration_sec: int = Query(20, ge=5, le=60)):
    """
    Generate CPU stress on control-plane pod for duration_sec seconds to test
    HorizontalPodAutoscaler (HPA) CPU utilization triggering.
    """
    import threading, math
    def cpu_burn():
        end_time = time.time() + duration_sec
        while time.time() < end_time:
            _ = math.sqrt(123456.789) * math.sin(98765.4321)

    threads = []
    for _ in range(4):
        t = threading.Thread(target=cpu_burn)
        t.daemon = True
        t.start()
        threads.append(t)

    return {
        "success": True,
        "duration_sec": duration_sec,
        "message": f"Triggered CPU stress for {duration_sec}s across {len(threads)} threads to test HPA",
        "timestamp": time.time(),
    }


