# System Monitoring Dashboard

Professional system monitoring solution built with Python, Prometheus, and Grafana.

## 🚀 Features

- Real-time CPU, memory, disk, and network monitoring
- Python-based metrics exporter
- Prometheus metrics collection
- Grafana visualization dashboards
- Systemd service integration

## 📊 Technologies Used

- **Python 3** with psutil and prometheus-client
- **Prometheus** for metrics storage
- **Grafana** for visualization
- **Node Exporter** for system metrics
- **Systemd** for service management

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/system-monitor.git
cd system-monitor

# Run installation script
chmod +x scripts/install_monitor.sh
./scripts/install_monitor.sh

📈 Metrics Collected

    system_cpu_percent - CPU usage percentage

    system_memory_percent - Memory usage percentage

    system_disk_percent - Disk usage per mountpoint

    system_network_sent_bytes - Network bytes sent

    system_network_recv_bytes - Network bytes received

🎯 Usage
bash

# Start the monitoring system
./scripts/start_monitor.sh

# Access dashboards:
# Grafana: http://localhost:3000
# Prometheus: http://localhost:9090
# Python Metrics: http://localhost:8000

📋 Project Structure

system-monitor/
├── src/           # Python source code
├── config/        # Configuration files
├── scripts/       # Installation and setup scripts
├── docs/          # Documentation
└── .github/       # CI/CD workflows

🤝 Contributing

Feel free to submit issues and enhancement requests!
📝 License

This project is licensed under the MIT License.
text


## 2. Plik `requirements.txt`

```txt
prometheus-client==0.20.0
psutil==5.9.0
