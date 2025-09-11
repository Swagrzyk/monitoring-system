#!/bin/bash
set -e

echo "Starting monitoring system..."

# Start services
sudo systemctl start prometheus
sudo systemctl start node_exporter
sudo systemctl start grafana-server

# Start Python exporter
cd ~/monitoring-system/python-apps
source venv/bin/activate
nohup python simple_monitor.py > simple_monitor.log 2>&1 &

echo "Monitoring system started!"
echo "➡ Grafana: http://localhost:3000"
echo "➡ Prometheus: http://localhost:9090"
echo "➡ Python Exporter: http://localhost:8000"
