#!/usr/bin/env python3
"""Extract candidate-level evidence from restored PHP web subjects.

This is a lightweight pre-treatment extractor. It creates an auditable candidate
dataset from source files and records the evidence needed before testability
screening. It does not apply transformations and does not claim final PHPMD or
PHPStan equivalence; external static tool logs can be joined later by
candidate_id/file/line.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


PHP_EXTENSIONS = {".php", ".phtml", ".inc", ".module"}
SKIP_PARTS = {
    ".git",
    "vendor",
    "node_modules",
    "tests",
    "test",
    "_test",
    "_cs",
    "cache",
    "tmp",
}


CSV_FIELDS = [
    "candidate_id",
    "project",
    "file",
    "start_line",
    "end_line",
    "candidate_type",
    "dominant_issue",
    "complexity_proxy",
    "request_parameters",
    "session_keys",
    "database_tables",
    "dom_selectors",
    "forms",
    "allowed_transformations",
    "oracle_status",
]


@dataclass
class Candidate:
    candidate_id: str
    project: str
    file: str
    start_line: int
    end_line: int
    candidate_type: str
    dominant_issue: str
    complexity_proxy: int
    request_parameters: list[str]
    session_keys: list[str]
    database_tables: list[str]
    dom_selectors: list[str]
    forms: list[str]
    allowed_transformations: list[str]
    oracle_status: str = "pending"


def php_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in PHP_EXTENSIONS:
            continue
        rel_parts = set(path.relative_to(root).parts)
        if rel_parts.intersection(SKIP_PARTS):
            continue
        yield path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def line_no(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def estimate_complexity(text: str) -> int:
    tokens = re.findall(r"\b(if|elseif|for|foreach|while|case|catch|&&|\|\|)\b|\?", text)
    return 1 + len(tokens)


def request_parameters(text: str) -> list[str]:
    found = re.findall(r"\$_(?:GET|POST|REQUEST)\s*\[\s*['\"]([^'\"]+)['\"]\s*\]", text)
    return sorted(set(found))


def session_keys(text: str) -> list[str]:
    found = re.findall(r"\$_SESSION\s*\[\s*['\"]([^'\"]+)['\"]\s*\]", text)
    return sorted(set(found))


def sql_tables(text: str) -> list[str]:
    if not has_sql_access(text):
        return []
    tables: list[str] = []
    for pattern in [
        r"\bFROM\s+`?([A-Za-z_][A-Za-z0-9_]*)`?",
        r"\bJOIN\s+`?([A-Za-z_][A-Za-z0-9_]*)`?",
        r"\bUPDATE\s+`?([A-Za-z_][A-Za-z0-9_]*)`?",
        r"\bINTO\s+`?([A-Za-z_][A-Za-z0-9_]*)`?",
    ]:
        tables.extend(re.findall(pattern, text, flags=re.I))
    return sorted(set(tables))


def dom_selectors(text: str) -> list[str]:
    ids = [f"#{value}" for value in re.findall(r"\bid\s*=\s*['\"]([^'\"]+)['\"]", text, flags=re.I)]
    classes = []
    for value in re.findall(r"\bclass\s*=\s*['\"]([^'\"]+)['\"]", text, flags=re.I):
        classes.extend(f".{part}" for part in value.split()[:3])
    return sorted(set(ids + classes))[:20]


def forms(text: str) -> list[str]:
    names = re.findall(r"<form\b[^>]*\bname\s*=\s*['\"]([^'\"]+)['\"]", text, flags=re.I)
    actions = re.findall(r"<form\b[^>]*\baction\s*=\s*['\"]([^'\"]+)['\"]", text, flags=re.I)
    return sorted(set(names + actions))[:20]


def is_mixed_php_html(text: str) -> bool:
    return "<?php" in text and bool(re.search(r"</?(html|body|div|form|table|script|span|input|a)\b", text, re.I))


def has_sql_access(text: str) -> bool:
    if re.search(r"\b(PDO|mysqli_|mysql_|pg_query|db_query|DB::|executeQuery)\b", text):
        return True
    return bool(
        re.search(
            r"['\"][^'\"]*\b(SELECT\s+.+\s+FROM|INSERT\s+INTO|UPDATE\s+[A-Za-z_`]|DELETE\s+FROM)\b",
            text,
            re.I | re.S,
        )
    )


def candidate_type(text: str, lines: int) -> tuple[str, str, list[str]]:
    has_sql = has_sql_access(text)
    has_request = "$_GET" in text or "$_POST" in text or "$_REQUEST" in text
    has_session = "$_SESSION" in text or "session_start" in text
    mixed = is_mixed_php_html(text)
    complexity = estimate_complexity(text)

    if mixed and has_sql:
        return "mixed_php_html_sql", "SQL in Presentation Logic", [
            "Light Data-Access Isolation",
            "Extract Method",
            "Extract View Helper",
        ]
    if mixed and has_request:
        return "form_handling", "Request Handling Mixed With Rendering", [
            "Extract Validation Helper",
            "Extract Method",
            "Extract View Helper",
        ]
    if mixed:
        return "mixed_php_html", "Mixed PHP/HTML", [
            "Separate PHP Logic from Markup",
            "Extract View Helper",
        ]
    if has_session:
        return "session_dependent_logic", "Session-Dependent Logic", [
            "Extract Guard",
            "Extract Method",
        ]
    if has_sql:
        return "sql_data_access", "SQL/Data Access Region", [
            "Light Data-Access Isolation",
            "Extract Method",
        ]
    if lines >= 100 or complexity >= 10:
        return "long_method_or_region", "Long or Complex Region", ["Extract Method"]
    return "local_region", "Maintainability Candidate", ["Extract Method"]


def function_regions(text: str) -> list[tuple[int, int, str]]:
    matches = list(re.finditer(r"\bfunction\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", text))
    regions: list[tuple[int, int, str]] = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        start_line = line_no(text, start)
        end_line = line_no(text, end)
        region_text = text[start:end]
        if end_line - start_line + 1 >= 40 or estimate_complexity(region_text) >= 8:
            regions.append((start_line, end_line, region_text))
    return regions


def file_region(text: str) -> tuple[int, int, str] | None:
    lines = text.splitlines()
    if len(lines) < 20:
        return None
    signals = [
        is_mixed_php_html(text),
        has_sql_access(text),
        "$_SESSION" in text,
        "$_GET" in text or "$_POST" in text or "$_REQUEST" in text,
        estimate_complexity(text) >= 12,
    ]
    if sum(1 for signal in signals if signal) >= 2:
        return (1, len(lines), text)
    return None


def extract(project: str, subject_dir: Path, limit: int) -> list[Candidate]:
    candidates: list[Candidate] = []
    counter = 1
    for file in php_files(subject_dir):
        rel = file.relative_to(subject_dir).as_posix()
        text = read_text(file)
        regions = function_regions(text)
        top = file_region(text)
        if top:
            regions.insert(0, top)

        for start, end, region_text in regions:
            ctype, issue, transforms = candidate_type(region_text, end - start + 1)
            if ctype == "local_region":
                continue
            candidate_id = f"{project}-C{counter:04d}"
            candidates.append(
                Candidate(
                    candidate_id=candidate_id,
                    project=project,
                    file=rel,
                    start_line=start,
                    end_line=end,
                    candidate_type=ctype,
                    dominant_issue=issue,
                    complexity_proxy=estimate_complexity(region_text),
                    request_parameters=request_parameters(region_text),
                    session_keys=session_keys(region_text),
                    database_tables=sql_tables(region_text),
                    dom_selectors=dom_selectors(region_text),
                    forms=forms(region_text),
                    allowed_transformations=transforms,
                )
            )
            counter += 1
            if limit and len(candidates) >= limit:
                return candidates
    return candidates


def write_outputs(candidates: list[Candidate], out_csv: Path, evidence_dir: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for candidate in candidates:
            row = asdict(candidate)
            for key in [
                "request_parameters",
                "session_keys",
                "database_tables",
                "dom_selectors",
                "forms",
                "allowed_transformations",
            ]:
                row[key] = ";".join(row[key])
            writer.writerow(row)

    for candidate in candidates:
        data = {
            "candidate_id": candidate.candidate_id,
            "subject_id": candidate.project,
            "file": candidate.file,
            "lines": [candidate.start_line, candidate.end_line],
            "candidate_type": candidate.candidate_type,
            "issues": [
                {
                    "type": candidate.dominant_issue,
                    "evidence": "Detected by pre-treatment heuristic extractor; join with PHPMD/PHPStan logs for final static evidence.",
                },
                {
                    "type": "Complexity Proxy",
                    "metric": "branch_keyword_count_plus_one",
                    "value": candidate.complexity_proxy,
                },
            ],
            "dependencies": {
                "request_parameters": candidate.request_parameters,
                "session_keys": candidate.session_keys,
                "database_tables": candidate.database_tables,
            },
            "web_contracts": {
                "dom_selectors": candidate.dom_selectors,
                "forms": candidate.forms,
            },
            "protected_constraints": {
                "must_preserve_request_parameters": candidate.request_parameters,
                "must_preserve_session_keys": candidate.session_keys,
                "must_preserve_database_tables": candidate.database_tables,
                "must_preserve_dom_selectors": candidate.dom_selectors,
                "must_preserve_forms": candidate.forms,
            },
            "allowed_transformations": candidate.allowed_transformations,
            "test_support": {
                "existing_tests": None,
                "characterization_tests": None,
                "oracle_status": candidate.oracle_status,
            },
        }
        path = evidence_dir / f"{candidate.candidate_id}.json"
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract candidate evidence from a PHP subject.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--subject-dir", required=True, type=Path)
    parser.add_argument("--out-csv", required=True, type=Path)
    parser.add_argument("--evidence-dir", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    candidates = extract(args.project, args.subject_dir, args.limit)
    write_outputs(candidates, args.out_csv, args.evidence_dir)
    print(f"Wrote {len(candidates)} candidates to {args.out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
