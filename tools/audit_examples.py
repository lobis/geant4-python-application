#!/usr/bin/env python3
"""Inventory official Geant4 examples and execute every claimed Python port."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path


def official_inventory(root: Path) -> dict:
    targets = sorted(p.parent.relative_to(root).as_posix() for p in root.rglob("CMakeLists.txt"))
    gdml = sorted(root.rglob("*.gdml"))
    standalone: list[str] = []
    fragments: list[str] = []
    invalid: list[str] = []
    for path in gdml:
        relative = path.relative_to(root).as_posix()
        try:
            tree = ET.parse(path)
            document = tree.getroot()
        except (ET.ParseError, OSError):
            invalid.append(relative)
            continue
        setup = document.find("setup")
        if setup is not None and setup.find("world") is not None:
            standalone.append(relative)
        else:
            fragments.append(relative)
    return {
        "root": str(root.resolve()),
        "cmake_targets": targets,
        "gdml": {
            "total": len(gdml),
            "standalone_candidates": standalone,
            "fragments": fragments,
            "invalid_or_external_entity": invalid,
        },
    }


def python_ports(root: Path, events: int, timeout: int) -> list[dict]:
    results: list[dict] = []
    for path in sorted(root.rglob("*.py")):
        if path.name == "run_gdml.py":
            results.append({"path": path.relative_to(root).as_posix(), "status": "utility"})
            continue
        text = path.read_text(errors="replace")
        if "--batch" not in text:
            results.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "status": "not-batch-testable",
                }
            )
            continue
        command = [sys.executable, str(path.resolve()), "--batch", "-n", str(events)]
        started = time.monotonic()
        with tempfile.TemporaryDirectory(prefix="g4-port-audit-") as workdir:
            try:
                completed = subprocess.run(
                    command,
                    cwd=workdir,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False,
                )
                status = "passed" if completed.returncode == 0 else "failed"
                result = {
                    "path": path.relative_to(root).as_posix(),
                    "status": status,
                    "returncode": completed.returncode,
                    "seconds": round(time.monotonic() - started, 3),
                }
                if completed.returncode:
                    result["stderr_tail"] = completed.stderr[-2000:]
                results.append(result)
            except subprocess.TimeoutExpired as error:
                results.append(
                    {
                        "path": path.relative_to(root).as_posix(),
                        "status": "timeout",
                        "seconds": round(time.monotonic() - started, 3),
                        "stderr_tail": (error.stderr or "")[-2000:],
                    }
                )
    return results


def markdown(report: dict) -> str:
    inventory = report["official"]
    results = report["python_ports"]
    passed = sum(item["status"] == "passed" for item in results)
    failed = sum(item["status"] in {"failed", "timeout"} for item in results)
    lines = [
        "# Geant4 example compatibility audit",
        "",
        f"- Official CMake targets: {len(inventory['cmake_targets'])}",
        f"- Official GDML files: {inventory['gdml']['total']}",
        f"- Standalone GDML candidates: {len(inventory['gdml']['standalone_candidates'])}",
        f"- Python ports passing: {passed}",
        f"- Python ports failing/timing out: {failed}",
        "",
        "| Python port | Status | Seconds |",
        "|---|---:|---:|",
    ]
    for item in results:
        lines.append(f"| `{item['path']}` | {item['status']} | {item.get('seconds', '')} |")
    lines.append("")
    lines.append("Only entries marked `passed` are validated as runnable Python ports.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("official_root", type=Path)
    parser.add_argument("python_root", type=Path)
    parser.add_argument("--events", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()

    report = {
        "official": official_inventory(args.official_root),
        "python_ports": python_ports(args.python_root, args.events, args.timeout),
    }
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2) + "\n")
    rendered = markdown(report)
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(rendered)
    print(rendered, end="")
    failed = any(item["status"] in {"failed", "timeout"} for item in report["python_ports"])
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
