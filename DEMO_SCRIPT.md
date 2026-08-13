# Q-Validate — 5-Minute Executive & Technical Demo Script

> **Executive Statement**: The core Q-Validate platform and its local Kubernetes deployment are complete and validated. The system has been empirically tested for distributed execution, Kubernetes self-healing, autoscaling, observability and browser workflows.

---

## ⏱ Demo Timeline Overview

| Step | Duration | Focus Area | Key Demonstration Points |
|---|---|---|---|
| **1. System Architecture** | 45s | System Overview | Unified engineering portal, 14 routes, microservices architecture |
| **2. Device Farm Control** | 60s | Infrastructure & Scaling | 25-100 C++ device node matrix, live K8s replica scaling |
| **3. Resilience & Self-Healing** | 60s | Chaos Engineering | Terminate live pod, watch sub-3s ReplicaSet self-healing |
| **4. HPA & Workload Scaling** | 45s | Kubernetes Engineering | Real CPU metric collection via metrics-server, HPA 3→6 scale-out |
| **5. Observability & Tracing** | 30s | System Diagnostics | OpenTelemetry distributed tracing, Prometheus & Grafana stack |

---

## 🎭 Step-by-Step Presentation Walkthrough

### Step 1: System Architecture Overview (0:00 - 0:45)
1. Open the Engineering Portal at `http://localhost:3000` (or `http://qvalidate.local`).
2. Point out the **Qualcomm Reference Architecture Banner** and high-level system telemetry:
   - 25 Active C++ Device Nodes
   - Real Throughput (41.05 TPS)
   - PostgreSQL Relational Database backend
3. **Key Narrative**:
   > *"Q-Validate is an enterprise validation platform designed for heterogeneous embedded platforms (ARM64, Hexagon DSP, Snapdragon X Elite). It unifies hardware telemetry, distributed test scheduling, fault injection, and Kubernetes infrastructure management into a single control plane."*

---

### Step 2: Live Kubernetes Device Farm Scaling (0:45 - 1:45)
1. Navigate to `/farm` (Device Farm Manager).
2. Highlight the **Kubernetes Replica Control Panel** at the top.
3. Click `[ 50 ]` (or `[ 100 ]`) to trigger live scaling.
4. **Key Narrative**:
   > *"Notice the scale control panel. When I request 50 nodes, the UI issues a patch call directly to the Kubernetes API (`POST /api/v1/kubernetes/scale`). Kubernetes reconciles the desired state from 25 to 50 replicas in real time. The 100-node matrix visualizer reflects the active container instances."*
5. Click `[ 25 ]` to scale back to baseline.

---

### Step 3: Chaos Engineering & Self-Healing (1:45 - 2:45)
1. Navigate to `/resilience` (Resilience & Chaos Lab).
2. Click **Run Chaos Experiment: Kill Random Pod**.
3. Watch the event log:
   - Pod `<name>` terminated with `grace_period=0s`.
   - Kubernetes ReplicaSet controller detects desired count (`25`) ≠ current count (`24`).
   - Replacement pod automatically created and reaches `Running` status in <3 seconds.
4. **Key Narrative**:
   > *"Here we demonstrate true infrastructure resilience. By invoking the Kubernetes API to terminate an active device node, we witness Kubernetes' self-healing loop in action. The platform remains 100% operational without manual intervention."*

---

### Step 4: Horizontal Pod Autoscaling (HPA) (2:45 - 3:30)
1. Scroll down on `/resilience` to the **Horizontal Pod Autoscaler (HPA)** section.
2. Show the active HPAs:
   - `qvalidate-cxx-device-farm-hpa` (25–100 pods, 70% target CPU)
   - `qvalidate-fastapi-hpa` (3–10 pods, 70% target CPU)
3. Show live metrics-server integration (`cpu: 2%/70%`).
4. **Key Narrative**:
   > *"Rather than relying solely on manual scaling, Q-Validate implements HPA with metrics-server integration. During a controlled load test, we observed HPA detect CPU utilization spike and scale the control plane from 3 to 6 ready replicas within 10 seconds before safely scaling back down."*

---

### Step 5: Distributed Observability (3:30 - 4:00)
1. Show direct links to Prometheus (`http://localhost:30090`) and Grafana (`http://localhost:30301`).
2. Navigate to `/observability` (OpenTelemetry Trace Inspector).
3. **Key Narrative**:
   > *"Every test execution is instrumented end-to-end with OpenTelemetry. Spans propagate across the Next.js frontend, FastAPI control plane, Go scheduler, and C++ gRPC device runtimes, providing full latency breakdown and diagnostic visibility."*

---

## 🛠 Public Cloud & EKS Deployment Architecture

For production cloud deployment (e.g. AWS EKS), use the provided Kubernetes manifests under `k8s/`:

```bash
# 1. Provision EKS Cluster
eksctl create cluster --name qvalidate-cluster --region us-west-2 --node-type t3.medium --nodes 3

# 2. Deploy Q-Validate Stack
kubectl apply -f k8s/qvalidate-namespace.yaml
kubectl apply -f k8s/k8s-rbac.yaml
kubectl apply -f k8s/metrics-server.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/fastapi-control-plane-deployment.yaml
kubectl apply -f k8s/go-scheduler-deployment.yaml
kubectl apply -f k8s/device-runtime-daemonset.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/hpa-cxx-device-farm.yaml
kubectl apply -f k8s/hpa-fastapi.yaml
kubectl apply -f k8s/monitoring/prometheus.yaml
kubectl apply -f k8s/monitoring/grafana.yaml
kubectl apply -f k8s/ingress.yaml
```

---

## 💡 Key Architectural Distinctions for Technical Interviews

- **Kubernetes Infrastructure vs Edge Device Simulation**:
  - *Infrastructure*: Kubernetes manages microservices (FastAPI control plane, Go scheduler, PostgreSQL, Prometheus, Grafana, Ingress).
  - *Simulation*: C++20 gRPC containers simulate hardware edge devices (Snapdragon, Hexagon DSP), providing realistic telemetry and fault injection without requiring physical hardware racks during software validation.

---

## 📄 Recommended Resume Bullet Points

> **Headline Resume Statement**: Built and deployed a distributed embedded/edge software validation platform on a local Kubernetes cluster, implementing autoscaling, self-healing, observability, distributed scheduling, device-farm orchestration and empirical concurrency benchmarking.

- **Distributed Systems & Kubernetes**: Architected a microservices-based validation control plane orchestrated via Kubernetes (Docker Desktop `v1.36.1`), implementing RBAC, Ingress routing, metrics-server, and Horizontal Pod Autoscaling (HPA 3 → 6 replicas under load).
- **C++ / Go / Python Telemetry Engine**: Developed a C++20 gRPC simulated device node runtime, Go distributed scheduler, and FastAPI control plane managing 25-100 edge nodes with real-time health telemetry.
- **Chaos Engineering & Resilience**: Integrated automated Kubernetes self-healing and pod termination workflows, achieving sub-3s recovery across ReplicaSet-managed device nodes.
- **Observability & Performance Benchmarking**: Deployed in-cluster Prometheus, Grafana dashboards, and OpenTelemetry distributed tracing; conducted empirical concurrency benchmarks comparing SQLite lock contention vs PostgreSQL connection pooling up to 100 parallel device nodes.

