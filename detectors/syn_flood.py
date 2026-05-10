import time

class SynFloodDetector:
    
    def __init__(self, cfg):
        self.history={}
        self.max_threshold=cfg["max_threshold"]
        self.time_window=cfg["time_window"]
        self.alerted={}
        
    def check(self, src_ip, timestamp):
        now = time.time()
        
        if src_ip not in self.history:
            self.history[src_ip]=[]
        self.history[src_ip].append(timestamp)
        
        self.history[src_ip] = [t for t in self.history[src_ip] if  t > now - self.time_window]
        
        if len(self.history[src_ip]) > self.max_threshold:
            if src_ip in self.alerted:
                if now - self.alerted[src_ip] < 10:
                    return False
            self.alerted[src_ip] = now
            return True
        else: return False
            