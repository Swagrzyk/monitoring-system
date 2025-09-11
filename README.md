
# System Monitoring Dashboard

<<<<<<< HEAD
A professional system monitoring solution built with **Python**, **Prometheus**, and **Grafana**.
=======
Professional system monitoring solution built with **Python**, **Prometheus**, and **Grafana**.
>>>>>>> b781580 (final)

## 🚀 Features

* Real-time monitoring of CPU, memory, disk, and network usage
<<<<<<< HEAD
* Python-based custom metrics exporter
* Prometheus for efficient metrics collection and storage
* Grafana dashboards for rich visualization
=======
* Python-based custom metrics exporter (`simple_monitor.py`)
* Prometheus metrics collection and storage
* Grafana dashboards for visualization
>>>>>>> b781580 (final)
* Systemd service integration for automatic startup

## 📊 Technologies Used

<<<<<<< HEAD
* **Python 3** (with `psutil`, `prometheus-client`)
* **Prometheus** (metrics storage & querying)
* **Grafana** (visualization and dashboards)
* **Node Exporter** (system metrics exporter)
* **Systemd** (service management)
=======
* **Python 3** (`psutil`, `prometheus-client`)
* **Prometheus** for metrics storage
* **Grafana** for visualization
* **Node Exporter** for system metrics
* **Systemd** for service management
>>>>>>> b781580 (final)

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/monitoring-system.git
cd monitoring-system

<<<<<<< HEAD
# Make installation script executable
=======
# Install dependencies and Python environment
>>>>>>> b781580 (final)
chmod +x scripts/install_monitor.sh

# Run installation
./scripts/install_monitor.sh
```

<<<<<<< HEAD
## 📈 Metrics Collected

* `system_cpu_percent` → CPU usage percentage
* `system_memory_percent` → Memory usage percentage
* `system_disk_percent` → Disk usage per mount point
* `system_network_sent_bytes` → Network bytes sent
* `system_network_recv_bytes` → Network bytes received

## 🎯 Usage

```bash
# Start the monitoring system
./scripts/start_monitor.sh
```

Access dashboards:

* **Grafana** → [http://localhost:3000](http://localhost:3000)
* **Prometheus** → [http://localhost:9090](http://localhost:9090)
* **Python Metrics Exporter** → [http://localhost:8000](http://localhost:8000)

## 📂 Project Structure

```
monitoring-system/
├── src/           # Python source code
├── config/        # Configuration files (Prometheus, systemd units, etc.)
├── scripts/       # Installation and management scripts
├── docs/          # Documentation
└── .github/       # CI/CD workflows
```

## 🤝 Contributing

Contributions are welcome!
Please open an issue or submit a pull request with improvements.

## 📝 License

This project is licensed under the **MIT License**.

=======
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

>>>>>>> b781580 (final)
