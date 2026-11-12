"""One command to check everything:  python scripts/verify.py"""
import subprocess
import sys
import time
import urllib.request

PORT = 8765


def run(name, cmd):
    print(f"\n▶ {name}")
    ok = subprocess.run(cmd).returncode == 0
    return ok


def server_smoke_test():
    """Start Streamlit headless and wait for its health endpoint to answer 'ok'."""
    print("\n▶ Streamlit server smoke test")
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py",
         "--server.headless", "true", "--server.port", str(PORT),
         "--browser.gatherUsageStats", "false"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(60):
            if proc.poll() is not None:
                return False
            try:
                with urllib.request.urlopen(f"http://localhost:{PORT}/_stcore/health", timeout=2) as r:
                    if r.status == 200 and r.read().strip() == b"ok":
                        return True
            except Exception:
                time.sleep(0.5)
        return False
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()


def main():
    rows = []
    steps = [
        ("Compile all sources", lambda: run("Compile all sources",
            [sys.executable, "-m", "compileall", "-q", "algorithm", "ui", "app.py"])),
        ("Unit + UI tests", lambda: run("Unit + UI tests", [sys.executable, "-m", "pytest", "-q"])),
        ("Server smoke test", server_smoke_test),
    ]
    failed = False
    for name, fn in steps:
        ok = fn()
        rows.append((name, ok))
        if not ok:
            failed = True
            break
    print("\n=== VERIFY SUMMARY ===")
    for name, ok in rows:
        print(f"{'✔ PASS' if ok else '✘ FAIL'}  {name}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

