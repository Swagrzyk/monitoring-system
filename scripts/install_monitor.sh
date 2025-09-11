#!/bin/bash
set -e

echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y wget tar python3 python3-venv python3-pip apt-transport-https software-properties-common

# Python venv setup
echo "Setting up Python exporter..."
cd ~/monitoring-system/python-apps
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "Installation completed!"
