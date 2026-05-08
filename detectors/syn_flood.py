import time

class SynFloodDetector:
    
    def __init__(self):
        self.history={}
        self.max_syns=100
        self.time_window=10
        self.alerted={}
        
    def check(self, src_ip, timestamp):
        now = time.time()
        
        if src_ip not in self.history:
            self.history[src_ip]=[]
        self.history[src_ip].append(timestamp)
        
        self.history[src_ip] = [t for t in self.history[src_ip] if  t > now - self.time_window]
        
        if len(self.history[src_ip]) > self.max_syns:
            if src_ip in self.alerted:
                if now - self.alerted[src_ip] < 10:
                    return False
            self.alerted[src_ip] = now
            return True
        else: return False
            