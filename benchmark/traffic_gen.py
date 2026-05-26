import argparse
import json
import sys
import time
from scapy.all import conf, Ether, IP, TCP, UDP, ICMP, sendpfast


def get_default_gateway():
    try:
        return conf.route.route("0.0.0.0")[2]
    except Exception:
        return "172.25.128.1"


def main():
    parser = argparse.ArgumentParser(
        description="High-Precision Hybrid Traffic Generator for pyNIDS Benchmarking"
    )
    parser.add_argument(
        "--rate",
        type=int,
        required=True,
        help="Target packet injection rate (Packets Per Second)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        required=True,
        help="Test duration in seconds"
    )
    parser.add_argument(
        "--type",
        type=str,
        choices=["syn", "udp", "icmp"],
        required=True,
        help="Type of traffic to simulate"
    )
    parser.add_argument(
        "--target",
        type=str,
        default=None,
        help="Target IP address (default: auto-detected gateway)"
    )
    parser.add_argument(
        "--iface",
        type=str,
        default="eth0",
        help="Network interface to send packets through (default: eth0)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Save results to JSON file (e.g. results/run_001.json)"
    )

    args = parser.parse_args()

    target_ip = args.target if args.target else get_default_gateway()

    print(f"[ * ] Initializing hybrid generator...")
    print(f"[ * ] Target IP:  {target_ip}")
    print(f"[ * ] Interface:  {args.iface}")
    print(f"[ * ] Parameters: {args.type.upper()} | Target Rate: {args.rate} PPS | Duration: {args.duration}s")

    if args.type == "syn":
        packet = Ether() / IP(src="10.0.0.99", dst=target_ip) / TCP(sport=12345, dport=80, flags="S")
    elif args.type == "udp":
        packet = Ether() / IP(src="10.0.0.99", dst=target_ip) / UDP(sport=12345, dport=53)
    elif args.type == "icmp":
        packet = Ether() / IP(src="10.0.0.99", dst=target_ip) / ICMP()

    total_packets_to_send = args.rate * args.duration
    packets_sent = 0

    print("\n[ + ] Traffic generation started. Press Ctrl+C to abort.")
    start_time = time.time()

    if args.rate < 2000:
        print("[ MODE ] Low-Rate Precision Loop")
        send_socket = conf.L2socket(iface=args.iface)
        packet_interval = 1.0 / args.rate

        try:
            while packets_sent < total_packets_to_send:
                target_send_time = start_time + (packets_sent * packet_interval)
                now = time.time()
                if now < target_send_time:
                    time.sleep(target_send_time - now)

                send_socket.send(packet)
                packets_sent += 1
        except KeyboardInterrupt:
            print("\n[ ! ] Generation interrupted by user.")
        finally:
            send_socket.close()

    else:
        print("[ MODE ] High-Rate Performance Mode (sendpfast / tcpreplay)")
        try:
            sendpfast(
                packet,
                pps=args.rate,
                loop=total_packets_to_send,
                iface=args.iface
            )
            packets_sent = total_packets_to_send
        except KeyboardInterrupt:
            print("\n[ ! ] Generation interrupted by user.")
        except Exception as e:
            print(f"\n[ ERROR ] sendpfast failed: {e}")
            print("[ ! ] Ensure tcpreplay is installed: sudo apt install tcpreplay")
            sys.exit(1)

    actual_duration = time.time() - start_time
    actual_pps = packets_sent / actual_duration if actual_duration > 0 else 0

    print("\n" + "=" * 40)
    print("      BENCHMARK GENERATION REPORT      ")
    print("=" * 40)
    print(f"  Status:           Completed")
    print(f"  Total Sent:       {packets_sent} packets")
    print(f"  Actual Duration:  {actual_duration:.2f} seconds")
    print(f"  Achieved Rate:    {actual_pps:.2f} PPS (Target: {args.rate})")
    print("=" * 40)

    if args.output:
        results = {
            "type": args.type,
            "target_ip": target_ip,
            "target_rate": args.rate,
            "duration": args.duration,
            "mode": "low_rate" if args.rate < 2000 else "high_rate",
            "packets_sent": packets_sent,
            "actual_duration": round(actual_duration, 3),
            "achieved_pps": round(actual_pps, 2)
        }
        
        if args.output:
            import os
            os.makedirs(os.path.dirname(args.output), exist_ok=True)
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
            print(f"[ + ] Results saved to {args.output}")


if __name__ == "__main__":
    main()