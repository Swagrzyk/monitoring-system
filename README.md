# monitoring-system

A small host monitoring stack: a Python exporter, Prometheus and Grafana. It can run as plain systemd services on a single machine, or on Kubernetes (kind) with the cluster state driven from git by ArgoCD and the cluster itself created with Terraform. Prometheus carries SLO-based alerts for the exporter's availability.

The exporter (`python-apps/simple_monitor.py`) uses `psutil` and `prometheus-client` and exposes CPU, memory, disk and network metrics on port 8000.

## Repository layout

```
python-apps/    exporter source and Dockerfile
prometheus/     config and unit files for the systemd setup
scripts/        install/start scripts for the systemd setup
k8s/            Kubernetes manifests (source of truth for ArgoCD)
  exporter/       Deployment, Service
  prometheus/     StatefulSet, PVC, scrape config and SLO rules
  grafana/        Deployment, Service, provisioned datasource and dashboard
argocd/         ArgoCD Application pointing at k8s/
terraform/      local kind cluster
```

## Running with systemd

The exporter, Prometheus, Grafana and node_exporter run as services on the host.

```bash
git clone https://github.com/swagrzyk/monitoring-system.git
cd monitoring-system

chmod +x scripts/install_monitor.sh scripts/start_monitor.sh
./scripts/install_monitor.sh
./scripts/start_monitor.sh
```

| Component | URL |
|---|---|
| Grafana | http://localhost:3000 |
| Prometheus | http://localhost:9090 |
| Exporter | http://localhost:8000/metrics |

## Running on Kubernetes

Requires `docker`, `kind`, `kubectl` and `terraform`.

### 1. Create the cluster

```bash
cd terraform
terraform init
terraform apply
cd ..
```

This is equivalent to `kind create cluster --name monitoring-system`. Details in [terraform/README.md](terraform/README.md).

### 2. Build and load the exporter image

kind nodes cannot pull from the local Docker daemon, so the image has to be loaded explicitly:

```bash
docker build -t monitoring-exporter:local python-apps/
kind load docker-image monitoring-exporter:local --name monitoring-system
```

### 3. Create the Grafana admin secret

The secret is not stored in git. Create it before deploying (a template is in [k8s/grafana/secret.yaml.example](k8s/grafana/secret.yaml.example)):

```bash
kubectl create namespace monitoring
kubectl create secret generic grafana-admin \
  --namespace monitoring \
  --from-literal=admin-password='<your-password>'
```

### 4. Deploy

Manually:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/exporter/ -f k8s/prometheus/ -f k8s/grafana/
```

Or through ArgoCD:

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.13.2/manifests/install.yaml
kubectl apply -f argocd/application.yaml
```

With ArgoCD, `main` is the source of truth. The Application uses automated sync with `selfHeal: true`, so new commits are applied automatically and manual changes made with `kubectl edit` are reverted. The `grafana-admin` secret is deliberately excluded from the Application and stays untouched by ArgoCD.

### 5. Open the UIs

The services are `ClusterIP`, so use port-forwarding:

```bash
kubectl port-forward -n monitoring svc/grafana 3000:3000
kubectl port-forward -n monitoring svc/prometheus 9090:9090
```

Grafana is then at http://localhost:3000 (dashboard: "Exporter SLO / Error Budget") and Prometheus at http://localhost:9090.

## Metrics

| Metric | Description |
|---|---|
| `system_cpu_percent` | CPU usage, % |
| `system_memory_percent` | Memory usage, % |
| `system_disk_percent` | Disk usage per mount point, % |
| `system_network_sent_bytes` | Bytes sent |
| `system_network_recv_bytes` | Bytes received |

## SLO and alerting

The SLI is the share of successful Prometheus scrapes of the exporter (`up{job="python-monitor"}`). The SLO is 99.5% over a rolling 30 days, which leaves an error budget of 0.5%.

Recording and alerting rules are in [k8s/prometheus/configmap-rules.yaml](k8s/prometheus/configmap-rules.yaml). They follow the multi-window, multi-burn-rate approach from the [Google SRE Workbook](https://sre.google/workbook/alerting-on-slos/):

| Alert | Burn rate | Windows | Budget gone in | Severity |
|---|---|---|---|---|
| `ExporterAvailabilityBurnRateFast` | 14.4x | 1h + 5m | ~2 days | page |
| `ExporterAvailabilityBurnRateSlow` | 6x | 6h + 30m | ~5 days | page |
| `ExporterAvailabilityBurnRateTicket` | 3x | 1d + 2h | ~10 days | ticket |

The short window paired with each long one makes the alert resolve soon after the exporter recovers instead of staying active for the whole long window.

The "Exporter SLO / Error Budget" dashboard is provisioned automatically ([k8s/grafana/configmap-dashboards.yaml](k8s/grafana/configmap-dashboards.yaml)). It shows current availability, remaining budget and burn rate next to the host metrics.

Prometheus retention is set to 30d to match the SLO window. A `prometheus-config-reloader` sidecar watches the mounted ConfigMaps and calls `/-/reload`, so a rule change merged to `main` is picked up after ArgoCD syncs it, with no manual restart.

## Known issues

In the container, `psutil.disk_partitions()` returns Docker's bind mounts (`/etc/resolv.conf`, `/etc/hostname`, etc.) as separate mount points. As a result `system_disk_percent` has a few extra, mostly useless series in the Kubernetes deployment. It is harmless; the proper fix is to filter partitions by filesystem type in `simple_monitor.py`.

## License

MIT
