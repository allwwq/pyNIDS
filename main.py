import argparse
from scapy.all import sniff
from scapy.layers.inet import IP, TCP, UDP, ICMP
from datetime import datetime
from detectors.port_scan import PortScanDetector
from detectors.syn_flood import SynFloodDetector
from detectors.icmp_flood import ICMPfloodDetector
from config import load_config
from alerts import log_packet, log_icmp, log_alert

parser = argparse.ArgumentParser(description="pyNIDS")
parser.add_argument("--iface", default=None, help="Network interface to sniff on")
parser.add_argument("--config", default="config.yaml", help="Path to config file")
args = parser.parse_args()

config = load_config(args.config)
iface = args.iface if args.iface is not None else config["network"]["iface"]
detector = PortScanDetector(config["detectors"]["port_scan"])
syn_detector = SynFloodDetector(config["detectors"]["syn_flood"])
icmp_detector = ICMPfloodDetector(config["detectors"]["icmp_flood"])

def process_packet(packet):
    now = datetime.now().timestamp()
    rntime = datetime.now().strftime("%H:%M:%S")
    
    if IP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
    
        if packet.haslayer(TCP):
            tsrc_p = packet[TCP].sport
            tdst_p = packet[TCP].dport
            if detector.check(src_ip, tdst_p, now):
                log_alert("PORT SCAN", src_ip)
                
            if packet[TCP].flags == "S":
                if syn_detector.check(src_ip, now):
                    log_alert("SYN FLOOD", src_ip)
            
            log_packet(rntime, "TCP", src_ip, tsrc_p, dst_ip, tdst_p)
            
        elif packet.haslayer(UDP):
            usrc_p = packet[UDP].sport
            udst_p = packet[UDP].dport
            log_packet(rntime, "UDP", src_ip, usrc_p, dst_ip, udst_p)
            
        elif packet.haslayer(ICMP):
            if icmp_detector.check(src_ip, now):
                log_alert("ICMP FLOOD", src_ip)
            log_icmp(rntime, src_ip, dst_ip)

sniff(iface=iface, filter="tcp or udp or icmp", prn=process_packet, store=False)