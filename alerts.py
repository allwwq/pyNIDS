from rich import print
import os
import json
from datetime import datetime

def log_packet(rntime, proto, src_ip, src_p, dst_ip, dst_p):
    if proto == "TCP":
        color = "green"
    elif proto == "UDP":
        color = "magenta"
    else:
        color = "bright_black"
    
    print(f"[{color}][{rntime}] {proto} | {src_ip}:{src_p} -> {dst_ip}:{dst_p}[/{color}]")

def log_icmp(rntime, src_ip, dst_ip):
    color = "cyan"
    print(f"[{color}][{rntime}] ICMP | {src_ip} -> {dst_ip}[/{color}]")
    
def log_arp(rntime, src_ip, src_mac, dst_ip):
    color = "bright_white"
    print(f"[{color}][{rntime}] ARP  | {src_mac} ({src_ip}) -> {dst_ip}[/{color}]")

def log_alert(alert_type, src_ip, severity, rntime, now):
    colors = {
        "INFO": "bright_blue",
        "WARNING": "bright_yellow",
        "HIGH": "dark_orange3",
        "CRITICAL": "bright_red"
    }
    color = colors.get(severity, "bold red")
    print(f"[{color}][{rntime}] [{severity}] {alert_type} detected from {src_ip}[/{color}]")
    log_to_file(alert_type, src_ip, severity, now)

def log_to_file(alert_type, src_ip, severity, now):
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.fromtimestamp(now).isoformat()
    alert_data = {
        "timestamp": timestamp,
        "severity": severity,
        "type": alert_type,
        "src_ip": src_ip
    }
    with open("logs/alerts.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(alert_data) + "\n")