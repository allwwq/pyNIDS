import time

class PortScanDetector:
    
    def __init__(self, cfg):
        self.history={}
        self.alerted={}
        self.max_threshold = cfg["max_threshold"]
        self.time_window = cfg["time_window"]
        
    def check(self, src_ip, dst_port, timestamp):
        now = time.time()
        
        
        if src_ip not in self.history:
            self.history[src_ip] = []
        self.history[src_ip].append((dst_port, timestamp))
        
        self.history[src_ip] = [(p, t) for p, t in self.history[src_ip] if t > now - self.time_window]
        
        uniq_ports = set(p for p, t in self.history[src_ip])
        
        if len(uniq_ports) > self.max_threshold:
            if src_ip in self.alerted:
                if now - self.alerted[src_ip] < 10:
                    return False
            self.alerted[src_ip] = now    
            return True
        
        else: return False