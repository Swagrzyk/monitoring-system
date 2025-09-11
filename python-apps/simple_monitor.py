#!/usr/bin/env python3
"""
Simple System Monitor - Podstawowy monitoring systemu
"""

import time
import psutil
import socket
from prometheus_client import start_http_server, Gauge, Counter

# Tworzymy metryki Prometheus
cpu_usage = Gauge('system_cpu_percent', 'Procent użycia CPU')
memory_usage = Gauge('system_memory_percent', 'Procent użycia pamięci RAM')
disk_usage = Gauge('system_disk_percent', 'Procent użycia dysku', ['mountpoint'])
network_sent = Gauge('system_network_sent_bytes', 'Wysłane bajty przez sieć')
network_recv = Gauge('system_network_recv_bytes', 'Odebrane bajty przez sieć')

def get_cpu_usage():
    """Pobiera użycie CPU"""
    try:
        usage = psutil.cpu_percent(interval=1)
        cpu_usage.set(usage)
        return usage
    except Exception as e:
        print(f"Błąd przy pobieraniu CPU: {e}")
        return 0

def get_memory_usage():
    """Pobiera użycie pamięci"""
    try:
        memory = psutil.virtual_memory()
        memory_usage.set(memory.percent)
        return memory.percent
    except Exception as e:
        print(f"Błąd przy pobieraniu pamięci: {e}")
        return 0

def get_disk_usage():
    """Pobiera użycie dysku"""
    try:
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage.labels(mountpoint=partition.mountpoint).set(usage.percent)
            except PermissionError:
                continue
    except Exception as e:
        print(f"Błąd przy pobieraniu dysku: {e}")

def get_network_usage():
    """Pobiera użycie sieci"""
    try:
        net_io = psutil.net_io_counters()
        network_sent.set(net_io.bytes_sent)
        network_recv.set(net_io.bytes_recv)
        return net_io.bytes_sent, net_io.bytes_recv
    except Exception as e:
        print(f"Błąd przy pobieraniu sieci: {e}")
        return 0, 0

def monitor_system():
    """Główna funkcja monitorująca"""
    print("Uruchamiam system monitorowania...")
    print("Metryki dostępne pod: http://localhost:8000")
    
    # Uruchom serwer Prometheus
    start_http_server(8000)
    
    print("=" * 50)
    print("SYSTEM MONITOR - PODSTAWOWE INFORMACJE")
    print("=" * 50)
    print(f"Hostname: {socket.gethostname()}")
    print(f"System: {psutil.os.name}")
    print(f"Procesor: {psutil.cpu_count()} rdzeni")
    print("=" * 50)
    
    # Główna pętla monitorowania
    while True:
        try:
            # Pobierz wszystkie metryki
            cpu = get_cpu_usage()
            memory = get_memory_usage()
            get_disk_usage()
            sent, recv = get_network_usage()
            
            # Wyświetl aktualne statystyki
            current_time = time.strftime("%H:%M:%S")
            print(f"[{current_time}] CPU: {cpu}% | RAM: {memory}% | "
                  f"Sieć: ↑{sent//1024}KB ↓{recv//1024}KB")
            
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("\nZatrzymywanie monitora...")
            break
        except Exception as e:
            print(f"Nieoczekiwany błąd: {e}")
            time.sleep(30)

if __name__ == "__main__":
    monitor_system()
