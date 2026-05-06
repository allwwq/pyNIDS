from scapy.all import sniff
from scapy.layers.inet import IP, TCP, UDP, ICMP
from datetime import datetime


def process_packet(packet):
    rntime = datetime.now().strftime("%H:%M:%S")
    
    if IP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
    
        if packet.haslayer(TCP):
            tsrc_p = packet[TCP].sport
            tdst_p = packet[TCP].dport
            print(f"[{rntime}] TCP | {src_ip}:{tsrc_p} -> {dst_ip}:{tdst_p}")
            
        elif packet.haslayer(UDP):
            usrc_p = packet[UDP].sport
            udst_p = packet[UDP].dport
            print(f"[{rntime}] UDP | {src_ip}:{usrc_p} -> {dst_ip}:{udst_p}")
            
        elif packet.haslayer(ICMP):
            print(f"[{rntime}] ICMP | {src_ip} -> {dst_ip}")

sniff(iface="eth0", filter="tcp or udp or icmp", prn=process_packet, store=False)