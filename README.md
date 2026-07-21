
---

# System Monitoring Dashboard

Professional system monitoring solution built with **Python**, **Prometheus**, and **Grafana**.

## 🚀 Features

* Real-time monitoring of CPU, memory, disk, and network usage
* Python-based custom metrics exporter (`simple_monitor.py`)
* Prometheus metrics collection and storage
* Grafana dashboards for visualization
* Systemd service integration for automatic startup

## 📊 Technologies Used

* **Python 3** (`psutil`, `prometheus-client`)
* **Prometheus** for metrics storage
* **Grafana** for visualization
* **Node Exporter** for system metrics
* **Systemd** for service management

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/swagrzyk/monitoring-system.git
cd monitoring-system

# Install dependencies and Python environment
chmod +x scripts/install_monitor.sh
./scripts/install_monitor.sh
```

## 🎯 Starting Monitoring

```bash
# Start all monitoring services
chmod +x scripts/start_monitor.sh
./scripts/start_monitor.sh
```

### Access Dashboards

* **Grafana** → [http://localhost:3000](http://localhost:3000)
* **Prometheus** → [http://localhost:9090](http://localhost:9090)
* **Python Exporter** → [http://localhost:8000/metrics](http://localhost:8000/metrics)

---

## 📈 Metrics Collected

* `system_cpu_percent` → CPU usage percentage
* `system_memory_percent` → Memory usage percentage
* `system_disk_percent` → Disk usage per mount point
* `system_network_sent_bytes` → Network bytes sent
* `system_network_recv_bytes` → Network bytes received

---

## 📂 Project Structure

```
monitoring-system/
├── docs/           # Documentation and installation guides
├── grafana/        # Grafana dashboards
├── prometheus/     # Prometheus config and systemd service units
├── python-apps/    # Python exporter and dependencies
├── scripts/        # Installation and start scripts
└── README.md       # Project overview
```

---

## 🤝 Contributing

Contributions are welcome! Open an issue or submit a pull request.

---

## 📝 License

This project is licensed under the **MIT License**.

---
