#!/usr/bin/env python3
"""Fast in-memory applyability check for generated pilot patches.

This does not mutate source files. It checks whether patch contexts can be
matched against the candidate target file.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path


FIELDS = ["candidate_id", "project", "treatment", "patch_format", "applyability_status", "message"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def detect_format(patch: str) -> str:
    stripped = patch.lstrip()
    if stripped.startswith("*** Begin Patch"):
        return "codex_apply_patch"
    if stripped.startswith("diff --git ") or stripped.startswith("--- "):
        return "unified_diff"
    if stripped:
        return "unknown"
    return "none"


def candidate_map() -> dict[str, dict[str, str]]:
    rows = read_csv(Path("results/summary/eligible_candidates_current.csv"))
    return {row["candidate_id"]: row for row in rows}


def codex_targets(patch: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"\*\*\* Update File: (.+)", patch)]


def codex_contexts_present(patch: str, source: str) -> tuple[bool, str]:
    bodies = re.split(r"\n(?=\*\*\* Update File: )", patch)
    checked = 0
    for body in bodies:
        if "*** Update File:" not in body:
            continue
        for section in re.split(r"\n@@\n", "\n" + body):
            old_lines = []
            for line in section.splitlines():
                if line.startswith("-") or line.startswith(" "):
                    old_lines.append(line[1:])
            old = "\n".join(old_lines).strip("\n")
            if old:
                checked += 1
                if old not in source:
                    return False, "context_not_found"
    return True, f"contexts_checked:{checked}"


def unified_targets(patch: str) -> list[str]:
    targets = []
    for line in patch.splitlines():
        if line.startswith("+++ b/"):
            targets.append(line[6:].strip())
        elif line.startswith("+++ "):
            target = line[4:].strip()
            if target != "/dev/null":
                targets.append(target.replace("b/", "", 1))
    return targets


def unified_basic_check(patch: str, source: str) -> tuple[bool, str]:
    # Conservative check: at least one deletion/context line must appear in source.
    contexts = [line[1:] for line in patch.splitlines() if line.startswith("-") and not line.startswith("---")]
    if not contexts:
        return True, "no_deletion_context"
    present = sum(1 for ctx in contexts if ctx in source)
    if present == 0:
        return False, "no_deletion_context_found"
    return True, f"deletion_contexts_present:{present}/{len(contexts)}"


def main() -> int:
    candidates = candidate_map()
    rows = []
    for row in read_csv(Path("results/summary/treatment_outputs_summary.csv")):
        if row["patch_generated"] != "true" or row["treatment"] == "T2-rule-static-only":
            continue
        candidate = candidates[row["candidate_id"]]
        source_path = Path("subjects") / candidate["project"] / candidate["file"]
        source = source_path.read_text(encoding="utf-8", errors="ignore")
        patch_path = Path("runs") / candidate["project"] / candidate["candidate_id"] / row["treatment"] / "patch.diff"
        patch = patch_path.read_text(encoding="utf-8", errors="ignore")
        fmt = detect_format(patch)

        if fmt == "codex_apply_patch":
            targets = codex_targets(patch)
            if candidate["file"] not in targets:
                status, msg = "suspicious", f"candidate_file_not_in_targets:{targets}"
            else:
                ok, msg = codex_contexts_present(patch, source)
                status = "applyable_context" if ok else "context_failed"
        elif fmt == "unified_diff":
            targets = unified_targets(patch)
            if targets and candidate["file"] not in targets and Path(candidate["file"]).name not in [Path(t).name for t in targets]:
                status, msg = "suspicious", f"candidate_file_not_in_targets:{targets}"
            else:
                ok, msg = unified_basic_check(patch, source)
                status = "applyable_context" if ok else "context_failed"
        else:
            status, msg = "unsupported", fmt

        rows.append(
            {
                "candidate_id": candidate["candidate_id"],
                "project": candidate["project"],
                "treatment": row["treatment"],
                "patch_format": fmt,
                "applyability_status": status,
                "message": msg,
            }
        )

    out = Path("results/summary/pilot_patch_applyability.csv")
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {out} ({len(rows)} generated patches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
