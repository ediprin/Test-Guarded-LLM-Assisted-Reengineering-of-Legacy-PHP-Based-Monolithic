#!/usr/bin/env python3
"""Summarize generated treatment outputs."""

from __future__ import annotations

import csv
import json
from pathlib import Path


FIELDS = ["candidate_id", "project", "treatment", "status", "patch_generated", "patch_format", "patch_bytes", "response_id"]


def detect_format(patch: str) -> str:
    stripped = patch.lstrip()
    if stripped.startswith("diff --git ") or stripped.startswith("--- "):
        return "unified_diff"
    if stripped.startswith("*** Begin Patch"):
        return "codex_apply_patch"
    if stripped:
        return "unknown"
    return "none"


def main() -> int:
    rows = []
    for candidate_dir in Path("runs").glob("*/*"):
        if not candidate_dir.is_dir():
            continue
        project = candidate_dir.parent.name
        candidate_id = candidate_dir.name
        for treatment in ["T1-llm-only", "T2-rule-static-only", "T3-evidence-llm"]:
            tdir = candidate_dir / treatment
            patch_path = tdir / "patch.diff"
            status_path = tdir / "status.json"
            decision_path = tdir / "decision.json"
            status = {}
            if status_path.exists():
                status = json.loads(status_path.read_text(encoding="utf-8"))
            elif decision_path.exists():
                status = json.loads(decision_path.read_text(encoding="utf-8"))
            patch = patch_path.read_text(encoding="utf-8", errors="ignore") if patch_path.exists() else ""
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "project": project,
                    "treatment": treatment,
                    "status": status.get("status", "missing"),
                    "patch_generated": str(bool(patch.strip())).lower(),
                    "patch_format": status.get("patch_format") or detect_format(patch),
                    "patch_bytes": len(patch.encode("utf-8")),
                    "response_id": status.get("response_id", ""),
                }
            )

    out = Path("results") / "summary" / "treatment_outputs_summary.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
