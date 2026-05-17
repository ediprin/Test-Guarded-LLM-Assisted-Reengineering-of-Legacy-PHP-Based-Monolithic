#!/usr/bin/env python3
"""Run php -l for candidate files inside a Docker Compose service."""

from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path


FIELDS = ["project", "file", "php_version", "status", "message"]


def run(cmd: list[str], timeout: int = 120) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout.strip()


def candidate_files(candidate_csv: Path) -> list[str]:
    with candidate_csv.open(encoding="utf-8", newline="") as handle:
        return sorted({row["file"] for row in csv.DictReader(handle)})


def compose_base(compose_file: Path, service: str) -> list[str]:
    return ["docker", "compose", "-f", str(compose_file), "exec", "-T", service]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run container php -l for files referenced by candidate CSV.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--compose-file", required=True, type=Path)
    parser.add_argument("--service", required=True)
    parser.add_argument("--container-root", default="/var/www/html")
    parser.add_argument("--candidate-csv", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    base = compose_base(args.compose_file, args.service)
    code, version = run(base + ["php", "-r", "echo PHP_VERSION;"])
    if code != 0:
        raise SystemExit(f"Could not read PHP version from container: {version}")

    rows = []
    for rel in candidate_files(args.candidate_csv):
        container_path = f"{args.container_root.rstrip('/')}/{rel}"
        code, out = run(base + ["php", "-l", container_path])
        rows.append(
            {
                "project": args.project,
                "file": rel,
                "php_version": version,
                "status": "PASS" if code == 0 else "FAIL",
                "message": out,
            }
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    failures = sum(1 for row in rows if row["status"] != "PASS")
    print(f"Wrote {args.out} ({len(rows)} files, {failures} failures, PHP {version})")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
