#!/usr/bin/env python3
"""Run a PHP syntax gate over candidate files.

This gate records the PHP CLI version used. For legacy subjects, a failure under
modern PHP may indicate version incompatibility rather than a syntax error in the
original target environment, so the version is part of the output artifact.
"""

from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path


FIELDS = ["project", "file", "php_version", "status", "message"]


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return proc.returncode, proc.stdout.strip()


def php_version() -> str:
    code, out = run(["php", "-r", "echo PHP_VERSION;"])
    return out if code == 0 else "UNKNOWN"


def candidate_files(candidate_csv: Path) -> list[str]:
    with candidate_csv.open(encoding="utf-8", newline="") as handle:
        return sorted({row["file"] for row in csv.DictReader(handle)})


def main() -> int:
    parser = argparse.ArgumentParser(description="Run php -l for files referenced by candidate CSV.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--subject-dir", required=True, type=Path)
    parser.add_argument("--candidate-csv", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    version = php_version()
    rows = []
    for rel in candidate_files(args.candidate_csv):
        path = args.subject_dir / rel
        code, out = run(["php", "-l", str(path)])
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
