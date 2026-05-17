#!/usr/bin/env python3
"""Run php -l for candidate files inside a generic PHP Docker image.

The subject repository is mounted read-only at /app. A file list is mounted at
/gate/files.txt so the container can lint all candidate-bearing files in one
process.
"""

from __future__ import annotations

import argparse
import base64
import csv
import subprocess
from pathlib import Path


FIELDS = ["project", "file", "php_version", "image", "status", "message"]


def run(cmd: list[str], timeout: int = 600) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout


def candidate_files(candidate_csv: Path) -> list[str]:
    with candidate_csv.open(encoding="utf-8", newline="") as handle:
        return sorted({row["file"] for row in csv.DictReader(handle)})


def docker_mount_path(path: Path) -> str:
    resolved = path.resolve()
    raw = str(resolved)
    if resolved.drive:
        drive = resolved.drive.rstrip(":").lower()
        rest = raw[len(resolved.drive):].replace("\\", "/")
        return f"//{drive}{rest}"
    return raw


def main() -> int:
    parser = argparse.ArgumentParser(description="Run php -l in a Docker PHP image.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--subject-dir", required=True, type=Path)
    parser.add_argument("--candidate-csv", required=True, type=Path)
    parser.add_argument("--image", default="php:5.6-cli")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--tmp-dir", default=".tmp", type=Path)
    args = parser.parse_args()

    args.tmp_dir.mkdir(parents=True, exist_ok=True)
    file_list = args.tmp_dir / "files.txt"
    with file_list.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(candidate_files(args.candidate_csv)) + "\n")

    shell = r'''
set -eu
version="$(php -r 'echo PHP_VERSION;')"
while IFS= read -r f; do
  [ -z "$f" ] && continue
  out="$(php -l "/app/$f" 2>&1)" || code="$?"
  code="${code:-0}"
  if [ "$code" = "0" ]; then status="PASS"; else status="FAIL"; fi
  msg="$(printf "%s" "$out" | base64 | tr -d '\n')"
  printf "%s\t%s\t%s\t%s\n" "$f" "$version" "$status" "$msg"
  unset code
done < /gate/files.txt
'''

    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{docker_mount_path(args.subject_dir)}:/app:ro",
        "-v",
        f"{docker_mount_path(args.tmp_dir)}:/gate:ro",
        args.image,
        "sh",
        "-c",
        shell,
    ]
    code, output = run(cmd, timeout=1800)
    if code != 0:
        raise SystemExit(output)

    rows = []
    for line in output.splitlines():
        parts = line.split("\t", 3)
        if len(parts) != 4:
            continue
        file, version, status, encoded = parts
        try:
            message = base64.b64decode(encoded).decode("utf-8", errors="replace")
        except Exception:
            message = encoded
        rows.append(
            {
                "project": args.project,
                "file": file,
                "php_version": version,
                "image": args.image,
                "status": status,
                "message": message,
            }
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    failures = sum(1 for row in rows if row["status"] != "PASS")
    version = rows[0]["php_version"] if rows else "UNKNOWN"
    print(f"Wrote {args.out} ({len(rows)} files, {failures} failures, {args.image}, PHP {version})")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
