class ArpSpoofDetector:
    def __init__(self):
        self.arp_table = {}
        
    def check(self, src_ip, src_mac):
        
        if src_ip not in self.arp_table:
            self.arp_table[src_ip] = src_mac
            return False
        
        elif src_mac == self.arp_table[src_ip]:
            return False
        
        else:
            self.arp_table[src_ip] = src_mac
            return True