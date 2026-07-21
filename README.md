
---

# Monitoring System

A system monitoring stack (Python exporter + Prometheus + Grafana) that runs
two ways: as native **systemd** services on a host, or as a **Kubernetes**
deployment managed via **GitOps (ArgoCD)**, provisioned with **Terraform**,
with SLO-based alerting on top of Prometheus.

## 🚀 Features

* Real-time monitoring of CPU, memory, disk, and network usage
* Custom Python metrics exporter (`simple_monitor.py`, `psutil` + `prometheus-client`)
* Two deployment paths: systemd services, or containerized on Kubernetes
* GitOps delivery via ArgoCD — the cluster state is whatever is in `k8s/` on `main`
* SLO/error-budget alerting on exporter availability (multi-window burn-rate)
* Terraform module to provision the local kind cluster the stack runs on

## 📊 Technologies Used

* **Python 3** (`psutil`, `prometheus-client`) — the exporter
* **Prometheus** — metrics storage, recording & alerting rules
* **Grafana** — dashboards, including an SLO/error-budget view
* **Docker** — exporter image
* **Kubernetes** (via `kind`) — Deployment/StatefulSet, ConfigMaps, PVC, probes, resource limits
* **ArgoCD** — GitOps continuous delivery
* **Terraform** (`tehcyx/kind` provider) — cluster provisioning
* **systemd** — the original bare-metal service path

---

## 📂 Project Structure

```
monitoring-system/
├── python-apps/       # Exporter source + Dockerfile
├── prometheus/        # Native systemd config (prometheus.yml, unit files)
├── scripts/           # Install/start scripts for the systemd path
├── k8s/               # Kubernetes manifests (the GitOps source of truth)
│   ├── namespace.yaml
│   ├── exporter/      # Deployment + Service for the Python exporter
│   ├── prometheus/    # StatefulSet + PVC, ConfigMaps (scrape config, SLO rules)
│   └── grafana/       # Deployment + Service, provisioned datasource + dashboard
├── argocd/            # ArgoCD Application pointing at k8s/
├── terraform/         # Provisions the local kind cluster
└── README.md
```

---

## Path A: native systemd

The original setup — exporter, Prometheus, Grafana, and node_exporter run as
systemd services directly on the host.

```bash
git clone https://github.com/swagrzyk/monitoring-system.git
cd monitoring-system

chmod +x scripts/install_monitor.sh scripts/start_monitor.sh
./scripts/install_monitor.sh
./scripts/start_monitor.sh
```

* **Grafana** → http://localhost:3000
* **Prometheus** → http://localhost:9090
* **Python Exporter** → http://localhost:8000/metrics

---

## Path B: Kubernetes + GitOps

The same stack, containerized and deployed to a local
[kind](https://kind.sigs.k8s.io/) cluster, managed declaratively.

### 1. Provision the cluster (Terraform)

```bash
cd terraform
terraform init
terraform apply
cd ..
```

See [`terraform/README.md`](terraform/README.md) for details. Equivalent to
`kind create cluster --name monitoring-system` by hand.

### 2. Build and load the exporter image

kind nodes don't have access to your local Docker registry, so the image
needs to be loaded into the cluster explicitly:

```bash
docker build -t monitoring-exporter:local python-apps/
kind load docker-image monitoring-exporter:local --name monitoring-system
```

### 3. Grafana admin credentials

Secrets aren't committed to git. Create the credential Secret before
deploying (see [`k8s/grafana/secret.yaml.example`](k8s/grafana/secret.yaml.example)):

```bash
kubectl create namespace monitoring
kubectl create secret generic grafana-admin \
  --namespace monitoring \
  --from-literal=admin-password='<your-password>'
```

### 4. Deploy

Either manually:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/exporter/ -f k8s/prometheus/ -f k8s/grafana/
```

Or via GitOps — install ArgoCD and point it at this repo:

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.13.2/manifests/install.yaml
kubectl apply -f argocd/application.yaml
```

From then on, `main` is the source of truth: `syncPolicy.automated` with
`selfHeal: true` means ArgoCD both applies new commits automatically *and*
reverts any manual `kubectl edit` drift back to what's in git. (The
`grafana-admin` Secret from step 3 is intentionally *not* tracked by the
Application, so ArgoCD leaves it alone — see the comments in
`secret.yaml.example` for why secrets aren't managed this way.)

### 5. Access the UIs

Services are `ClusterIP`, so use port-forwarding:

```bash
kubectl port-forward -n monitoring svc/grafana 3000:3000
kubectl port-forward -n monitoring svc/prometheus 9090:9090
```

* **Grafana** → http://localhost:3000 (dashboard: *Exporter SLO / Error Budget*)
* **Prometheus** → http://localhost:9090

> **Known quirk:** inside a container, `psutil.disk_partitions()` sees
> Docker's bind mounts (`/etc/resolv.conf`, `/etc/hostname`, ...) as
> separate mount points, so `system_disk_percent` reports a few extra
> low-signal series in the containerized deployment. Harmless, just noisy —
> a real fix would filter partitions by filesystem type in `simple_monitor.py`.

---

## 📈 Metrics Collected

* `system_cpu_percent` → CPU usage percentage
* `system_memory_percent` → Memory usage percentage
* `system_disk_percent` → Disk usage per mount point
* `system_network_sent_bytes` → Network bytes sent
* `system_network_recv_bytes` → Network bytes received

---

## SLO / Error Budget

**SLI**: fraction of Prometheus scrapes against the exporter that succeed
(`up{job="python-monitor"}`).

**SLO**: 99.5% of scrapes succeed over a rolling 30-day window (0.5% error
budget).

Recording and alerting rules live in
[`k8s/prometheus/configmap-rules.yaml`](k8s/prometheus/configmap-rules.yaml)
and follow the [Google SRE Workbook's multi-window,
multi-burn-rate](https://sre.google/workbook/alerting-on-slos/) pattern:

| Alert | Burn rate | Windows | Budget exhausted in | Severity |
|---|---|---|---|---|
| `ExporterAvailabilityBurnRateFast` | 14.4x | 1h + 5m | ~2 days | page |
| `ExporterAvailabilityBurnRateSlow` | 6x | 6h + 30m | ~5 days | page |
| `ExporterAvailabilityBurnRateTicket` | 3x | 1d + 2h | ~10 days | ticket |

A short window alongside each long window means the alert clears quickly
once the exporter actually recovers, instead of staying red for the entire
long window.

The Grafana dashboard *Exporter SLO / Error Budget* (auto-provisioned, see
[`k8s/grafana/configmap-dashboards.yaml`](k8s/grafana/configmap-dashboards.yaml))
visualizes current availability, remaining error budget, and burn rate over
time, alongside the raw host metrics.

Prometheus TSDB retention is set to 30d to match the SLO window, and a
`prometheus-config-reloader` sidecar watches the mounted ConfigMaps and calls
Prometheus's `/-/reload` automatically, so a rule change merged to `main`
takes effect without manual intervention once ArgoCD syncs it.

---

## 🤝 Contributing

Contributions are welcome! Open an issue or submit a pull request.

---

## 📝 License

This project is licensed under the **MIT License**.

---
