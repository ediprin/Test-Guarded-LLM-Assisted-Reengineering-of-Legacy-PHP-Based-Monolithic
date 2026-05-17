#!/usr/bin/env python3
"""HTTP characterization with simple CSRF login support."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from http.cookiejar import CookieJar
from pathlib import Path
from urllib.parse import urlencode, urljoin
from urllib.request import HTTPCookieProcessor, Request, build_opener


FIELDS = ["project", "login_url", "target_url", "status", "content_sha256", "assertions_passed", "assertions_failed", "message"]


def request(opener, url: str, data: dict[str, str] | None = None) -> tuple[int, str]:
    encoded = None if data is None else urlencode(data).encode("utf-8")
    req = Request(url, data=encoded, headers={"User-Agent": "test-guarded-characterization/0.1"})
    with opener.open(req, timeout=30) as response:
        return response.getcode(), response.read().decode("utf-8", errors="replace")


def extract_form_action(base_url: str, html: str) -> str:
    match = re.search(r"<form\b[^>]*action=['\"]([^'\"]+)['\"]", html, re.I)
    if not match:
        return base_url
    return urljoin(base_url, match.group(1).replace("&amp;", "&"))


def extract_csrf(html: str) -> str:
    match = re.search(r"name=['\"]csrf_token['\"]\s+value=['\"]([^'\"]+)['\"]", html, re.I)
    if not match:
        match = re.search(r"value=['\"]([^'\"]+)['\"]\s+name=['\"]csrf_token['\"]", html, re.I)
    return match.group(1) if match else ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Login and characterize a target page.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--login-url", required=True)
    parser.add_argument("--target-url", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--contains", action="append", default=[])
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    failures: list[str] = []

    try:
        login_status, login_html = request(opener, args.login_url)
        csrf = extract_csrf(login_html)
        action = extract_form_action(args.login_url, login_html)
        payload = {"username": args.username, "password": args.password}
        if csrf:
            payload["csrf_token"] = csrf
        request(opener, action, payload)
        status, body = request(opener, args.target_url)
    except Exception as exc:
        status, body = 0, ""
        failures.append(f"request_failed:{exc}")

    if status != 200:
        failures.append(f"expected_status_200_got_{status}")
    for expected in args.contains:
        if expected not in body:
            failures.append(f"missing_text:{expected}")

    total_assertions = 1 + len(args.contains)
    row = {
        "project": args.project,
        "login_url": args.login_url,
        "target_url": args.target_url,
        "status": "PASS" if not failures else "FAIL",
        "content_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest() if body else "",
        "assertions_passed": str(total_assertions - len(failures)),
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
