#!/usr/bin/env python3
"""Audit Rio-based PHP subject systems before transformation.

This script intentionally stops before LLM transformation. It builds the
subject-level audit matrix required by the experiment design:

project, repo_url, selected_tag, commit, php_version, db_required,
install_status, test_command, test_status, static_tools_status,
candidate_count, oracle_status, usable_for_experiment, notes
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

import yaml


FIELDNAMES = [
    "project",
    "repo_url",
    "selected_tag",
    "commit",
    "php_version",
    "db_required",
    "install_status",
    "test_command",
    "test_status",
    "static_tools_status",
    "candidate_count",
    "oracle_status",
    "usable_for_experiment",
    "notes",
]


PHP_EXTENSIONS = {".php", ".phtml", ".inc", ".module"}
SKIP_DIRS = {
    ".git",
    "vendor",
    "node_modules",
    "cache",
    "tmp",
    "var/cache",
    "storage/cache",
    "third_party",
    "3rdparty",
    "libraries/vendor",
}


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 120) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout.strip()


def load_subjects(config: Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(config.read_text(encoding="utf-8"))
    return data.get("primary_subjects", [])


def ensure_clone(subject: dict[str, Any], repo_dir: Path, clone: bool) -> str:
    if repo_dir.exists():
        return "CLONED"
    if not clone:
        return "NOT_CLONED"

    repo_dir.parent.mkdir(parents=True, exist_ok=True)
    code, out = run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--branch",
            str(subject["selected_tag"]),
            str(subject["repo_url"]),
            str(repo_dir),
        ],
        timeout=1800,
    )
    if code != 0:
        return f"CLONE_FAILED: {one_line(out)}"

    expected = str(subject.get("commit", ""))
    if expected:
        code, actual = run(["git", "rev-parse", "HEAD"], cwd=repo_dir)
        if code == 0 and actual and actual != expected:
            code, out = run(["git", "checkout", expected], cwd=repo_dir)
            if code != 0:
                return f"CHECKOUT_MISMATCH: got {actual}; {one_line(out)}"
    return "CLONED"


def one_line(value: str, limit: int = 180) -> str:
    return re.sub(r"\s+", " ", value).strip()[:limit]


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def detect_php_version(repo_dir: Path) -> str:
    composer = repo_dir / "composer.json"
    if composer.exists():
        data = read_json(composer)
        php_req = data.get("require", {}).get("php") or data.get("require-dev", {}).get("php")
        if php_req:
            return str(php_req)

    candidates = [
        repo_dir / ".github" / "workflows",
        repo_dir / ".travis.yml",
        repo_dir / "appveyor.yml",
        repo_dir / "Dockerfile",
    ]
    patterns = [
        re.compile(r"php[-: ]?([0-9]+\.[0-9]+)", re.I),
        re.compile(r"PHP_VERSION[=: ]+([0-9]+\.[0-9]+)", re.I),
    ]
    for path in candidates:
        files = path.rglob("*") if path.is_dir() else [path]
        for file in files:
            if not file.is_file():
                continue
            try:
                text = file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for pattern in patterns:
                match = pattern.search(text)
                if match:
                    return match.group(1)
    return ""


def composer_test_command(repo_dir: Path) -> str:
    composer = repo_dir / "composer.json"
    if not composer.exists():
        return ""
    data = read_json(composer)
    scripts = data.get("scripts", {})
    for name in ["test", "phpunit", "unit", "tests"]:
        if name in scripts:
            return f"composer {name}"
    return ""


def detect_test_command(repo_dir: Path) -> str:
    from_composer = composer_test_command(repo_dir)
    if from_composer:
        return from_composer
    if any(repo_dir.glob("phpunit.xml*")):
        return "vendor/bin/phpunit"
    if any((repo_dir / "_test").glob("phpunit.xml*")):
        return "vendor/bin/phpunit -c _test/phpunit.xml"
    if (repo_dir / "vendor" / "bin" / "phpunit").exists():
        return "vendor/bin/phpunit"
    if (repo_dir / "_test").exists():
        return "manual: _test directory exists"
    if (repo_dir / "tests").exists():
        return "manual: tests directory exists"
    return ""


def detect_static_tools(repo_dir: Path) -> str:
    found: list[str] = []
    patterns = {
        "phpstan": ["phpstan.neon", "phpstan.neon.dist", "phpstan.dist.neon"],
        "psalm": ["psalm.xml", "psalm.xml.dist"],
        "phpcs": ["phpcs.xml", "phpcs.xml.dist", "phpcs.xml.dist.sample"],
        "phpmd": ["phpmd.xml", "phpmd.xml.dist", "ruleset.xml"],
        "phpunit": ["phpunit.xml", "phpunit.xml.dist"],
    }
    for tool, names in patterns.items():
        direct = any((repo_dir / name).exists() for name in names)
        legacy_test = tool == "phpunit" and any((repo_dir / "_test" / name).exists() for name in names)
        if direct or legacy_test:
            found.append(tool)

    composer = repo_dir / "composer.json"
    if composer.exists():
        data = read_json(composer)
        deps = {}
        deps.update(data.get("require", {}))
        deps.update(data.get("require-dev", {}))
        dep_text = " ".join(deps.keys()).lower()
        for tool in ["phpstan", "psalm", "php_codesniffer", "phpmd", "phpunit"]:
            if tool in dep_text and tool not in found:
                found.append(tool)

    return ",".join(found) if found else "NO_LOCAL_CONFIG"


def iter_php_files(repo_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in repo_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in PHP_EXTENSIONS:
            continue
        rel = path.relative_to(repo_dir).as_posix()
        if any(rel == skip or rel.startswith(skip + "/") for skip in SKIP_DIRS):
            continue
        files.append(path)
    return files


def has_mixed_php_html(text: str) -> bool:
    return "<?php" in text and "?>" in text and bool(re.search(r"</?(html|body|div|form|table|script|span|input)\b", text, re.I))


def long_function_count(text: str, threshold: int = 100) -> int:
    starts = [m.start() for m in re.finditer(r"\bfunction\s+[A-Za-z_][A-Za-z0-9_]*\s*\(", text)]
    if not starts:
        return 0
    line_offsets = [0]
    for m in re.finditer("\n", text):
        line_offsets.append(m.start())

    count = 0
    lines = text.splitlines()
    for idx, start in enumerate(starts):
        end = starts[idx + 1] if idx + 1 < len(starts) else len(text)
        start_line = text[:start].count("\n")
        end_line = text[:end].count("\n")
        if end_line - start_line + 1 >= threshold:
            count += 1
    return count


def quick_candidate_count(repo_dir: Path) -> int:
    count = 0
    for file in iter_php_files(repo_dir):
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        file_score = 0
        if has_mixed_php_html(text):
            file_score += 1
        if re.search(r"\b(SELECT|INSERT|UPDATE|DELETE)\b", text, re.I):
            file_score += 1
        if "$_SESSION" in text or "session_start" in text:
            file_score += 1
        if "$_GET" in text or "$_POST" in text or "$_REQUEST" in text:
            file_score += 1
        file_score += long_function_count(text)

        count += min(file_score, 5)
    return count


def audit_subject(subject: dict[str, Any], subjects_dir: Path, clone: bool, count_candidates: bool) -> dict[str, Any]:
    project = str(subject["id"])
    repo_dir = subjects_dir / project
    install_status = ensure_clone(subject, repo_dir, clone)

    row = {
        "project": project,
        "repo_url": subject.get("repo_url", ""),
        "selected_tag": subject.get("selected_tag", ""),
        "commit": subject.get("commit", ""),
        "php_version": "",
        "db_required": str(subject.get("db_required", "")).lower(),
        "install_status": install_status,
        "test_command": "",
        "test_status": "NOT_RUN",
        "static_tools_status": "NOT_RUN",
        "candidate_count": "",
        "oracle_status": "PENDING",
        "usable_for_experiment": "false",
        "notes": "",
    }

    if not repo_dir.exists():
        row["notes"] = "Run again with --clone or place repository under subjects/<project>."
        return row

    row["php_version"] = detect_php_version(repo_dir)
    row["test_command"] = detect_test_command(repo_dir)
    row["static_tools_status"] = detect_static_tools(repo_dir)
    if count_candidates:
        row["candidate_count"] = str(quick_candidate_count(repo_dir))

    if row["test_command"]:
        row["test_status"] = "DISCOVERED_NOT_RUN"
    else:
        row["test_status"] = "NO_TEST_COMMAND_DISCOVERED"

    row["notes"] = "Audit only; Docker restoration and oracle validation still required."
    return row


def write_csv(rows: list[dict[str, Any]], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Rio PHP web-app subjects.")
    parser.add_argument("--config", default="datasets.rio-audit.yml", type=Path)
    parser.add_argument("--subjects-dir", default="subjects", type=Path)
    parser.add_argument("--out", default="results/summary/audit_matrix.csv", type=Path)
    parser.add_argument("--subject", help="Audit only one subject id.")
    parser.add_argument("--clone", action="store_true", help="Clone missing repositories at the selected tag.")
    parser.add_argument(
        "--count-candidates",
        action="store_true",
        help="Run a fast heuristic candidate count. This is not a substitute for static-analysis evidence.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    subjects = load_subjects(args.config)
    if args.subject:
        subjects = [subject for subject in subjects if subject.get("id") == args.subject]
    if not subjects:
        raise SystemExit("No subjects selected.")

    rows = [
        audit_subject(subject, args.subjects_dir, args.clone, args.count_candidates)
        for subject in subjects
    ]
    write_csv(rows, args.out)
    print(f"Wrote {args.out} ({len(rows)} subjects)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
