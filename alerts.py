from rich import print

def log_packet(rntime, proto, src_ip, src_p, dst_ip, dst_p):
    if proto == "TCP":
        color = "green"
    elif proto == "UDP":
        color = "magenta"
    else:
        color = "bright_white"
    
    print(f"[{color}][{rntime}] {proto} | {src_ip}:{src_p} -> {dst_ip}:{dst_p}[/{color}]")

def log_icmp(rntime, src_ip, dst_ip):
    color = "cyan"
    print(f"[{color}][{rntime}] ICMP | {src_ip} -> {dst_ip}[/{color}]")

def log_alert(alert_type, src_ip):
    color = "bold red"
    print(f"[{color}][ALERT] {alert_type} detected from {src_ip}[/{color}]")