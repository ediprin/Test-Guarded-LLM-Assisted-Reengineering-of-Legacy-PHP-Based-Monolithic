#!/usr/bin/env python3
"""Run OpenAI model execution for prepared treatment prompts.

Reads prompt.md from runs/<project>/<candidate>/<treatment>/ and writes:
- response.txt
- patch.diff (best-effort extraction)
- status.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path

import httpx


def extract_output_text(payload: dict) -> str:
    if "output_text" in payload and payload["output_text"]:
        return payload["output_text"]
    parts: list[str] = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if text:
                parts.append(text)
    return "\n".join(parts)


def extract_patch(text: str) -> str:
    text = text.strip()
    fenced = re.search(r"```(?:diff|patch)?\s*(.*?)```", text, re.S | re.I)
    if fenced:
        text = fenced.group(1).strip()
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if line.startswith("diff --git ") or line.startswith("--- "):
            return "\n".join(lines[idx:]).rstrip() + "\n"
    return text.rstrip() + "\n"


def patch_format(patch: str) -> str:
    stripped = patch.lstrip()
    if stripped.startswith("diff --git ") or stripped.startswith("--- "):
        return "unified_diff"
    if stripped.startswith("*** Begin Patch"):
        return "codex_apply_patch"
    return "unknown"


def call_openai(prompt: str, model: str, timeout: int, max_retries: int = 3) -> dict:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    body = {
        "model": model,
        "input": prompt,
        "reasoning": {"effort": "low"},
        "text": {"format": {"type": "text"}},
    }
    with httpx.Client(timeout=timeout) as client:
        for attempt in range(max_retries + 1):
            response = client.post(
                "https://api.openai.com/v1/responses",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json=body,
            )
            if response.status_code != 429:
                break
            if attempt >= max_retries:
                break
            wait = 20 * (attempt + 1)
            time.sleep(wait)
    if response.status_code >= 400:
        raise RuntimeError(f"OpenAI API error {response.status_code}: {response.text[:1000]}")
    return response.json()


def run_one(treatment_dir: Path, model: str, timeout: int, sleep_seconds: float, max_prompt_chars: int) -> dict:
    prompt_path = treatment_dir / "prompt.md"
    if not prompt_path.exists():
        return {"status": "skipped_no_prompt", "patch_generated": False}
    prompt = prompt_path.read_text(encoding="utf-8")
    if max_prompt_chars and len(prompt) > max_prompt_chars:
        status = {
            "status": "skipped_prompt_too_large",
            "model": model,
            "patch_generated": False,
            "prompt_chars": len(prompt),
            "max_prompt_chars": max_prompt_chars,
        }
        treatment_dir.joinpath("status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
        return status
    started = time.time()
    payload = call_openai(prompt, model, timeout)
    raw = extract_output_text(payload)
    patch = extract_patch(raw)
    treatment_dir.joinpath("response.txt").write_text(raw, encoding="utf-8")
    treatment_dir.joinpath("patch.diff").write_text(patch, encoding="utf-8")
    status = {
        "status": "model_executed",
        "model": model,
        "patch_generated": bool(patch.strip()),
        "patch_format": patch_format(patch),
        "response_id": payload.get("id"),
        "duration_seconds": round(time.time() - started, 3),
        "patch_starts_with": patch.splitlines()[0] if patch.splitlines() else "",
    }
    treatment_dir.joinpath("status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    if sleep_seconds:
        time.sleep(sleep_seconds)
    return status


def iter_treatment_dirs(runs_dir: Path, candidates: list[str], treatments: list[str]):
    for candidate_id in candidates:
        matches = list(runs_dir.glob(f"*/{candidate_id}"))
        if not matches:
            raise RuntimeError(f"Candidate run not found: {candidate_id}")
        candidate_dir = matches[0]
        for treatment in treatments:
            yield candidate_id, treatment, candidate_dir / treatment


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute OpenAI treatments for prepared prompts.")
    parser.add_argument("--runs-dir", default="runs", type=Path)
    parser.add_argument("--candidate-id", action="append")
    parser.add_argument("--eligible-csv", default="results/summary/eligible_candidates_current.csv", type=Path)
    parser.add_argument("--all-eligible", action="store_true")
    parser.add_argument("--treatment", action="append", choices=["T1-llm-only", "T3-evidence-llm"], required=True)
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--sleep-seconds", type=float, default=0.5)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--max-prompt-chars", type=int, default=28000)
    args = parser.parse_args()

    candidate_ids = args.candidate_id or []
    if args.all_eligible:
        import csv

        with args.eligible_csv.open(encoding="utf-8", newline="") as handle:
            candidate_ids.extend(row["candidate_id"] for row in csv.DictReader(handle))
    candidate_ids = list(dict.fromkeys(candidate_ids))
    if not candidate_ids:
        raise SystemExit("No candidate ids selected. Use --candidate-id or --all-eligible.")

    results = []
    for candidate_id, treatment, treatment_dir in iter_treatment_dirs(args.runs_dir, candidate_ids, args.treatment):
        if args.skip_existing and (treatment_dir / "patch.diff").exists() and (treatment_dir / "patch.diff").read_text(encoding="utf-8", errors="ignore").strip():
            print(f"Skipping {candidate_id} {treatment}: patch already exists")
            continue
        print(f"Running {candidate_id} {treatment} with {args.model}")
        status = run_one(treatment_dir, args.model, args.timeout, args.sleep_seconds, args.max_prompt_chars)
        results.append({"candidate_id": candidate_id, "treatment": treatment, **status})
        print(f"  {status['status']} patch_generated={status.get('patch_generated')}")
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
