import argparse, time, signal, sys
from kuksa_client.grpc import VSSClient
from speedMonitor.core import SpeedMonitor, Thresholds
from speedMonitor.io import AlertSink

def parse_args():
    p = argparse.ArgumentParser(description="Speed Anomaly Monitor (Phase 1 scaffold)")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=55556)
    p.add_argument("--max-speed", type=float, default=80.0)
    p.add_argument("--csv", default="alerts.csv")
    p.add_argument("--hz", type=float, default=1.0, help="Polling frequency in Hz")
    # p.add_argument("--tls", action="store_true", help="Use TLS for VSSClient connection")
    return p.parse_args()

def main():
    args = parse_args()
    mon  = SpeedMonitor(Thresholds(args.max_speed))
    sink = AlertSink(args.csv)

    # c = VSSClient(args.host, args.port); c.connect()
    c = VSSClient(args.host, args.port)
    c.connect()

    print(f"Polling Vehicle.Speed at {args.hz} Hz. Ctrl+C to exit.", flush=True)


    running = True
    def _stop(*_):
        nonlocal running; running = False
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    period = 1.0 / max(1e-6, args.hz)

    try:
        while running:
            # 
            cur = c.get_current_values(["Vehicle.Speed"])
            speed = cur["Vehicle.Speed"].value

            # 
            alerts = mon.on_speed(speed)
            for a in alerts:
                #  a.speed / a.value 
                val = getattr(a, "speed", getattr(a, "value", speed))
                reason = getattr(a, "reason", "")
                sink.write(a.kind, val, reason)
                print(f"[ALERT] kind={a.kind} speed={val:.2f} reason={reason}", flush=True)

            time.sleep(period)
    except KeyboardInterrupt:
        print("Interrupted, exiting…", file=sys.stderr)
    finally:
        try:
            sink.close()
        except Exception:
            pass
        try:
            c.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
