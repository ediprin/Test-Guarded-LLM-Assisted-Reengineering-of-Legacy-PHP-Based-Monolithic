#!/usr/bin/env python3
"""Run simple HTTP characterization checks for restored web subjects."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path
from urllib.request import Request, urlopen


FIELDS = ["project", "url", "status", "content_sha256", "assertions_passed", "assertions_failed", "message"]


def fetch(url: str, timeout: int) -> tuple[int, str]:
    req = Request(url, headers={"User-Agent": "test-guarded-characterization/0.1"})
    with urlopen(req, timeout=timeout) as response:
        status = response.getcode()
        body = response.read().decode("utf-8", errors="replace")
    return status, body


def main() -> int:
    parser = argparse.ArgumentParser(description="Run basic HTTP characterization assertions.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--contains", action="append", default=[])
    parser.add_argument("--selector-id", action="append", default=[])
    parser.add_argument("--selector-class", action="append", default=[])
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()

    failures: list[str] = []
    try:
        status, body = fetch(args.url, args.timeout)
    except Exception as exc:
        status, body = 0, ""
        failures.append(f"request_failed: {exc}")

    if status != 200:
        failures.append(f"expected_status_200_got_{status}")

    for expected in args.contains:
        if expected not in body:
            failures.append(f"missing_text:{expected}")

    for selector in args.selector_id:
        pattern = rf"\bid\s*=\s*['\"]{re.escape(selector.lstrip('#'))}['\"]"
        if not re.search(pattern, body, re.I):
            failures.append(f"missing_id:{selector}")

    for selector in args.selector_class:
        cls = re.escape(selector.lstrip("."))
        pattern = rf"\bclass\s*=\s*['\"][^'\"]*\b{cls}\b"
        if not re.search(pattern, body, re.I):
            failures.append(f"missing_class:{selector}")

    passed = 1 if status == 200 else 0
    passed += len(args.contains) + len(args.selector_id) + len(args.selector_class) - len(
        [f for f in failures if not f.startswith("request_failed") and not f.startswith("expected_status")]
    )

    row = {
        "project": args.project,
        "url": args.url,
        "status": "PASS" if not failures else "FAIL",
        "content_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest() if body else "",
        "assertions_passed": str(max(passed, 0)),
        "assertions_failed": str(len(failures)),
        "message": "; ".join(failures),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow(row)

    print(f"Wrote {args.out}: {row['status']}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
