import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="MCP stdio client (dry-run until SDK confirmed)")
    parser.add_argument("exec_path", help="Path to MCP server executable")
    parser.add_argument("--args", nargs=argparse.REMAINDER, default=[], help="Args for the server")
    parser.add_argument("--dry", action="store_true", help="Dry-run: print only")
    args = parser.parse_args()

    if not Path(args.exec_path).exists():
        print(f"[ERROR] exec not found: {args.exec_path}")
        sys.exit(2)

    cmd = [args.exec_path] + args.args
    if args.dry:
        print("[DRY] Would start:", " ".join(cmd))
        sys.exit(0)

    # Placeholder: spawn process; actual MCP protocol handling requires SDK/integration
    print("[INFO] Starting process (no protocol I/O yet):", " ".join(cmd))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        outs, errs = proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
    print("[INFO] Process exited:", proc.returncode)
    print("[STDOUT]\n", outs.decode(errors="ignore")[:500])
    print("[STDERR]\n", errs.decode(errors="ignore")[:500])


if __name__ == "__main__":
    main()
