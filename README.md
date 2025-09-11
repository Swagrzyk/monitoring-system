
# System Monitoring Dashboard

A professional system monitoring solution built with **Python**, **Prometheus**, and **Grafana**.

## 🚀 Features

* Real-time monitoring of CPU, memory, disk, and network usage
* Python-based custom metrics exporter
* Prometheus for efficient metrics collection and storage
* Grafana dashboards for rich visualization
* Systemd service integration for automatic startup

## 📊 Technologies Used

* **Python 3** (with `psutil`, `prometheus-client`)
* **Prometheus** (metrics storage & querying)
* **Grafana** (visualization and dashboards)
* **Node Exporter** (system metrics exporter)
* **Systemd** (service management)

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/monitoring-system.git
cd monitoring-system

# Make installation script executable
chmod +x scripts/install_monitor.sh

# Run installation
./scripts/install_monitor.sh
```

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

