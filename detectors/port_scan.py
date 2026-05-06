import time

class PortScanDetector:
    
    def __init__(self):
        self.history={}
        self.alerted={}
        self.max_ports = 15
        self.max_time = 10
        
    def check(self, src_ip, dst_port, timestamp):
        now = time.time()
        
        
        if src_ip not in self.history:
            self.history[src_ip] = []
        self.history[src_ip].append((dst_port, timestamp))
        
        self.history[src_ip] = [(p, t) for p, t in self.history[src_ip] if t > now - self.max_time]
        
        uniq_ports = set(p for p, t in self.history[src_ip])
        
        if len(uniq_ports) > self.max_ports:
            if src_ip in self.alerted:
                if now - self.alerted[src_ip] < 10:
                    return False
            self.alerted[src_ip] = now    
            return True
        
        else: return False