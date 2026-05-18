# pyNIDS

Lightweight Network Intrusion Detection System for Linux — real-time packet capture with attack detection, alert severity levels, and JSON logging.

## Overview

pyNIDS monitors network traffic in real time and detects common attack patterns. Each packet is parsed and classified; suspicious activity triggers colored alerts in the terminal with severity levels.

**Detected threats:**

- Port scan (Nmap `-sS`, `-sT` and similar)
- SYN flood
- ICMP flood
- ARP spoofing *(v1.1)*

## Demo

```
[00:42:09] TCP  | 172.25.133.160:39561 -> 172.25.128.1:80
[00:42:09] UDP  | 172.25.128.1:51129 -> 239.255.255.250:1900
[00:42:09] ICMP | 172.25.133.160 -> 8.8.8.8
[HIGH]    PORT SCAN detected from 172.25.133.160
[CRITICAL] SYN FLOOD detected from 172.25.133.160
```

## Project Structure

```
pyNIDS/
├── main.py               # Entry point, CLI
├── capture.py            # Packet capture and processing
├── alerts.py             # Colored terminal output and JSON logging
├── config.py             # Config loader
├── config.yaml           # Thresholds and interface settings
├── logs/                 # JSON alert logs (auto-created)
├── detectors/
│   ├── port_scan.py      # Port scan detector
│   ├── syn_flood.py      # SYN flood detector
│   ├── icmp_flood.py     # ICMP flood detector
│   └── arp_spoof.py      # ARP spoofing detector (v1.1)
└── requirements.txt
```

## How It Works

**Packet capture** — Scapy sniffs raw packets on the specified interface and passes each one to `process_packet()`. IP, TCP, UDP, ICMP and ARP layers are parsed to extract source/destination IPs, ports and MAC addresses.

**Detection logic** — each detector maintains a time-windowed history per source IP:

| Detector | Trigger condition | Severity |
| --- | --- | --- |
| Port scan | >15 unique destination ports from one IP in 10s | HIGH |
| SYN flood | >100 SYN packets from one IP in 10s | CRITICAL |
| ICMP flood | >100 ICMP packets from one IP in 10s | CRITICAL |
| ARP spoof | ARP reply changes known MAC→IP mapping | HIGH |

All thresholds are configurable in `config.yaml`. Each detector has a cooldown to avoid alert spam.

## Installation

```bash
git clone https://github.com/allwwq/pyNIDS.git
cd pyNIDS
pip install -r requirements.txt
```

## Usage

```bash
# Default — interface taken from config.yaml
sudo python3 main.py

# Override interface via CLI
sudo python3 main.py --iface wlan0

# Custom config file
sudo python3 main.py --config my_config.yaml

# Help
python3 main.py --help
```

> Root privileges required for raw packet capture.

## Configuration

Edit `config.yaml` to tune detection thresholds:

```yaml
network:
  iface: eth0

detectors:
  port_scan:
    max_threshold: 15
    time_window: 10
  syn_flood:
    max_threshold: 100
    time_window: 10
  icmp_flood:
    max_threshold: 100
    time_window: 10
  arp_spoof:
    enabled: true
```

## Testing

**Port scan:**
```bash
sudo nmap -sS <target_ip>
```

**SYN flood:**
```bash
sudo hping3 -S -p 80 --flood <target_ip>
```

**ICMP flood:**
```bash
sudo ping -f <target_ip>
```

**ARP spoofing:**
```bash
sudo arpspoof -i eth0 -t <target_ip> <gateway_ip>
```

## Roadmap

### v1.x — Core Features

- [x] **v1.0** — Packet capture (TCP/UDP/ICMP), port scan / SYN flood / ICMP flood detectors, YAML config, CLI
- [x] **v1.1** — ARP spoofing detector, alert severity (INFO/WARNING/HIGH/CRITICAL), JSON log file output
- [ ] **v1.2** — Detector plugin API — auto-loading from `detectors/`, unified detector interface
- [ ] **v1.3** — Terminal dashboard — live stats: packets/sec, top IPs, active alerts, protocol breakdown
- [ ] **v1.4** — Packet filters — `--port`, `--host`, `--proto` CLI flags; config profiles (`home.yaml`, `lab.yaml`)
- [ ] **v1.5** — Multithreading — capture thread → packet queue → worker threads
- [ ] **v1.6** — Flow engine — TCP session tracking, flow timeout cleanup, per-flow statistics
- [ ] **v1.7** — Protocol parsers — DNS, HTTP Host/Method/User-Agent, ICMP ping sweep detection
- [ ] **v1.8** — SQLite storage — persistent alert and flow history, `python3 main.py stats`
- [ ] **v1.9** — PCAP support — `python3 main.py replay file.pcap`, pcap export
- [ ] **v1.10** — Rule engine — YAML-based rules, mini-Suricata style
- [ ] **v1.11** — Beaconing detection — C2 repeated connection patterns

### v2.x — Advanced

- [ ] **v2.0** — Web dashboard — live browser UI
- [ ] **v2.1** — Packaging — PyInstaller exe for Windows, Linux package

## Tech Stack

- Python 3.8+
- Scapy — packet capture and parsing
- PyYAML — configuration
- Rich — colored terminal output

## License

MIT
