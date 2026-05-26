import argparse
import json
import os
import sys
import time
from scapy.all import sniff

packet_count = 0


def packet_callback(packet):
    global packet_count
    packet_count += 1


def main():
    parser = argparse.ArgumentParser(
        description="Packet Counter / Receiver for pyNIDS Benchmarking"
    )
    parser.add_argument(
        "--duration",
        type=int,
        required=True,
        help="How long to listen, in seconds"
    )
    parser.add_argument(
        "--src",
        type=str,
        default="10.0.0.99",
        help="Source IP to filter on (default: 10.0.0.99)"
    )
    parser.add_argument(
        "--iface",
        type=str,
        default="eth0",
        help="Network interface to listen on (default: eth0)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Save results to JSON file (e.g. benchmark/results/recv_001.json)"
    )

    args = parser.parse_args()

    print(f"[ * ] Initializing receiver...")
    print(f"[ * ] Interface: {args.iface}")
    # FIX: use 'src host' instead of 'host' to only count packets
    # originating from the generator — avoids counting reply packets
    # which would inflate the received count and distort drop rate
    bpf_filter = f"src host {args.src}"
    print(f"[ * ] BPF Filter: {bpf_filter}")
    print(f"[ * ] Duration:  {args.duration}s")
    print("\n[ + ] Receiver is running. Start traffic generation now...")

    start_time = time.time()

    try:
        sniff(
            iface=args.iface,
            filter=bpf_filter,
            prn=packet_callback,
            store=False,
            timeout=args.duration
        )
    except Exception as e:
        print(f"[ ERROR ] Sniffer error: {e}")
        sys.exit(1)

    actual_duration = time.time() - start_time
    avg_pps = packet_count / actual_duration if actual_duration > 0 else 0

    print("\n" + "=" * 40)
    print("       BENCHMARK RECEIVER REPORT       ")
    print("=" * 40)
    print(f"  Status:           Completed")
    print(f"  Packets Received: {packet_count}")
    print(f"  Actual Duration:  {actual_duration:.2f}s")
    print(f"  Average Rate:     {avg_pps:.2f} PPS")
    print("=" * 40)

    if args.output:
        results = {
            "src_filter": args.src,
            "packets_received": packet_count,
            "duration": round(actual_duration, 3),
            "avg_pps": round(avg_pps, 2)
        }
        try:
            dir_name = os.path.dirname(args.output)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
            print(f"[ + ] Results saved to {args.output}")
        except Exception as e:
            print(f"[ ! ] Failed to save JSON: {e}")


if __name__ == "__main__":
    main()