from scapy.all import sniff
from scapy.layers.inet import IP, TCP, UDP, ICMP
from datetime import datetime
from detectors.port_scan import PortScanDetector
from detectors.syn_flood import SynFloodDetector
from detectors.icmp_flood import ICMPfloodDetector

detector = PortScanDetector()
syn_detector = SynFloodDetector()
icmp_detector = ICMPfloodDetector()

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
                print(f"[ALERT] Port scan detected from {src_ip}")
                
            if packet[TCP].flags == "S":
                if syn_detector.check(src_ip, now):
                    print(f"[ALERT] SYN flood detected from {src_ip}")
            
            print(f"[{rntime}] TCP | {src_ip}:{tsrc_p} -> {dst_ip}:{tdst_p}")
            
        elif packet.haslayer(UDP):
            usrc_p = packet[UDP].sport
            udst_p = packet[UDP].dport
            print(f"[{rntime}] UDP | {src_ip}:{usrc_p} -> {dst_ip}:{udst_p}")
            
        elif packet.haslayer(ICMP):
            if icmp_detector.check(src_ip, now):
                print(f"[ALERT] ICMP flood detected from {src_ip}")
            print(f"[{rntime}] ICMP | {src_ip} -> {dst_ip}")

sniff(iface="eth0", filter="tcp or udp or icmp", prn=process_packet, store=False)