#!/usr/bin/env python3
"""Run every Python port of the Geant4 examples headless; exit 1 if any fails."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORTS = ROOT / "examples" / "geant4-examples" / "Geant4-11.4.2-examples-python"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--events", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()

    failed = []
    # Examples live in subdirectories; top-level scripts (run_gdml.py) are utilities.
    ports = sorted(
        p
        for p in PORTS.rglob("*.py")
        if p.parent != PORTS and "--batch" in p.read_text()
    )
    for port in ports:
        name = port.relative_to(PORTS).as_posix()
        try:
            result = subprocess.run(
                [sys.executable, str(port), "--batch", "-n", str(args.events)],
                capture_output=True,
                text=True,
                timeout=args.timeout,
                check=False,
            )
            ok = result.returncode == 0
            detail = (
                (result.stderr or result.stdout).strip().splitlines()[-1:]
                if not ok
                else []
            )
        except subprocess.TimeoutExpired:
            ok, detail = False, [f"timed out after {args.timeout} s"]
        print(f"{'ok    ' if ok else 'FAILED'} {name} {' '.join(detail)}", flush=True)
        if not ok:
            failed.append(name)

    print(f"{len(ports) - len(failed)}/{len(ports)} example ports passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
