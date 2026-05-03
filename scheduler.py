import os
import sys
import time
from datetime import datetime, time as dtime

from dotenv import load_dotenv

from db import is_clocked_in, is_clocked_out, record_clock_in, record_clock_out
from main import perform_attendance

os.makedirs("screenshots", exist_ok=True)


def parse_time(val: str) -> dtime:
    h, m = val.strip().split(":")
    return dtime(int(h), int(m))


def run_cycle() -> None:
    load_dotenv()
    clock_in_time = parse_time(os.environ.get("CLOCK_IN_TIME", "09:00"))
    clock_out_time = parse_time(os.environ.get("CLOCK_OUT_TIME", "18:00"))
    now = datetime.now()
    current_time = now.time()
    today = now.date()

    print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] Checking attendance...", flush=True)
    print(f"  Schedule: clock_in={clock_in_time}, clock_out={clock_out_time}", flush=True)

    # Clock in: langsung gas kapanpun belum dilakukan hari ini
    if not is_clocked_in(today):
        print(f"  -> Clock in belum dilakukan, executing...", flush=True)
        if perform_attendance("clock_in"):
            record_clock_in(today)
            print(f"  -> Clock in recorded!", flush=True)
        else:
            print(f"  -> Clock in FAILED", flush=True)
    else:
        print(f"  -> Sudah clock in hari ini", flush=True)

    # Clock out: gas kalau sudah lewat jam clock out
    if not is_clocked_out(today):
        if current_time >= clock_out_time:
            print(f"  -> Clock out belum dilakukan, executing...", flush=True)
            if perform_attendance("clock_out"):
                record_clock_out(today)
                print(f"  -> Clock out recorded!", flush=True)
            else:
                print(f"  -> Clock out FAILED", flush=True)
        else:
            print(f"  -> Belum waktunya clock out ({current_time.strftime('%H:%M')} < {clock_out_time})", flush=True)
    else:
        print(f"  -> Sudah clock out hari ini", flush=True)


def main() -> None:
    check_interval = int(os.environ.get("CHECK_INTERVAL_MINUTES", "15"))
    print(f"Talenta Auto Attendance Scheduler", flush=True)
    print(f"Check interval: {check_interval} minutes", flush=True)
    print(f"Press Ctrl+C to stop\n", flush=True)

    while True:
        try:
            run_cycle()
        except Exception as e:
            print(f"[error] {type(e).__name__}: {e}", flush=True)
        time.sleep(check_interval * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        run_cycle()
    else:
        main()
