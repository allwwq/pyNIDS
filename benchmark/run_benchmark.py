import argparse
import json
import os
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(
        description="Automated Benchmark Orchestrator for pyNIDS"
    )
    parser.add_argument("--rate",     type=int, required=True, help="Target rate (PPS)")
    parser.add_argument("--duration", type=int, required=True, help="Test duration (seconds)")
    parser.add_argument("--type",     type=str, choices=["syn", "udp", "icmp"], required=True,
                        help="Traffic type")

    args = parser.parse_args()

    gen_output   = "benchmark/results/temp_generator.json"
    recv_output  = "benchmark/results/temp_receiver.json"
    final_output = f"benchmark/results/final_{args.type}_{args.rate}pps.json"

    for f in [gen_output, recv_output]:
        if os.path.exists(f):
            os.remove(f)

    os.makedirs("benchmark/results", exist_ok=True)

    print(f"\n[ BENCHMARK ] {args.type.upper()} | {args.rate} PPS | {args.duration}s")

    devnull = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}

    print("[ 1/3 ] Starting receiver...")
    recv_proc = subprocess.Popen(
        [
            "sudo", "python3", "benchmark/receiver.py",
            "--duration", str(args.duration + 2),
            "--output",   recv_output
        ],
        **devnull
    )

    time.sleep(1)

    print("[ 2/3 ] Running generator...")
    subprocess.run(
        [
            "sudo", "python3", "benchmark/traffic_gen.py",
            "--rate",     str(args.rate),
            "--duration", str(args.duration),
            "--type",     args.type,
            "--output",   gen_output
        ],
        **devnull
    )

    print("[ 3/3 ] Waiting for receiver to finish...")
    recv_proc.wait()

    try:
        with open(gen_output, "r") as f:
            gen_data = json.load(f)
        with open(recv_output, "r") as f:
            recv_data = json.load(f)

        sent      = gen_data["packets_sent"]
        received  = recv_data["packets_received"]
        drop_rate = ((sent - received) / sent * 100) if sent > 0 else 0.0

        print(f"\n  Packets sent:     {sent}")
        print(f"  Packets received: {received}")
        print(f"  Drop rate:        {drop_rate:.2f}%")
        print(f"  Generator PPS:    {gen_data['achieved_pps']}")
        print(f"  Receiver PPS:     {recv_data['avg_pps']}")

        final_report = {
            "test_type":              args.type,
            "target_pps":             args.rate,
            "duration":               args.duration,
            "mode":                   gen_data["mode"],
            "packets_sent":           sent,
            "packets_received":       received,
            "drop_rate_percent":      round(drop_rate, 2),
            "achieved_generator_pps": gen_data["achieved_pps"],
            "achieved_receiver_pps":  recv_data["avg_pps"]
        }

        with open(final_output, "w") as f:
            json.dump(final_report, f, indent=2)

        print(f"\n[ + ] Report saved to: {final_output}\n")

    except FileNotFoundError as e:
        print(f"\n[ ERROR ] Result file not found: {e}")
    except Exception as e:
        print(f"\n[ ERROR ] {e}")


if __name__ == "__main__":
    main()