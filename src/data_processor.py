"""
data_processor.py
=================
Triggers (Data Flow Testing):
  - All-Defs Coverage %     (Beniget / pyflakes)  – every variable definition is exercised
  - All-Uses Coverage %     (coverage.py + Beniget) – every use of each variable is reached
  - Computational Use (C-Use) / Predicate Use (P-Use) (coverage.py + Beniget)
  - Definition-Use Pair Identification, Path Correlation Mapping
  - Dead Data Identification – some definitions are never used
  - Null and Boundary Flow Analysis (CrossHair)
  - Inter-procedural Tracking – cross-function def-use chains
  - Data Integrity Audit (pydriller / pyflakes)
  - Audit Trail Verification

Also triggers:
  - Code Churn analysis (pydriller on git history)
  - Regression Focus Mapping
"""
from __future__ import annotations

import csv
import io
from typing import Any


# ── Simple def-use chain (C-Use) ──────────────────────────────────────────────
def compute_average(values: list[float]) -> float:
    """
    DEF: total, count
    USE: total (arithmetic), count (division)
    → All-Defs + C-Use coverage.
    """
    total = 0.0          # DEF total
    count = len(values)  # DEF count
    if count == 0:
        return 0.0
    for v in values:
        total += v       # USE total
    return total / count  # USE total, USE count


# ── Predicate Use (P-Use) ─────────────────────────────────────────────────────
def filter_positives(values: list[float]) -> list[float]:
    """
    P-Use: variable 'v' in predicate `v > 0`
    """
    positives = []         # DEF positives
    for v in values:       # DEF v
        if v > 0:          # P-USE v
            positives.append(v)  # USE positives
    return positives


# ── Dead variable – triggers Dead Data Identification ────────────────────────
def process_with_dead_var(data: list[int]) -> int:
    unused_temp = [x * 2 for x in data]  # DEF unused_temp – never used (pyflakes F841)
    result = sum(data)                   # DEF result
    return result                        # USE result


# ── Multiple definitions – Ambiguity Resolution metric ───────────────────────
def classify_value(x: float) -> str:
    """
    Variable 'label' is defined in multiple branches.
    Tests: Multiple Definitions Handling, Data Flow Gap Analysis.
    """
    label = "unknown"       # DEF 1
    if x < 0:
        label = "negative"  # DEF 2
    elif x == 0:
        label = "zero"      # DEF 3
    else:
        label = "positive"  # DEF 4
    return label             # USE label (all 4 defs)


# ── Cross-function def-use (Inter-procedural Tracking) ──────────────────────
def _normalize(values: list[float]) -> list[float]:
    """Defines 'normed' list – used by caller."""
    maximum = max(values) if values else 1.0   # DEF maximum
    normed = [v / maximum for v in values]     # DEF normed, USE maximum
    return normed


def rank_items(raw_scores: list[float]) -> list[tuple[int, float]]:
    """
    Uses 'normed' returned from _normalize → inter-procedural def-use pair.
    Also: Coverage Delta % (if tests change which branches are hit).
    """
    normed = _normalize(raw_scores)         # USE normed (from _normalize)
    ranked = sorted(
        enumerate(normed), key=lambda x: x[1], reverse=True
    )
    return ranked


# ── CSV parsing – triggers Null / Boundary Flow Analysis ────────────────────
def parse_csv(raw_text: str) -> list[dict[str, Any]]:
    """
    Handles empty string and malformed rows.
    CrossHair boundary analysis: empty string → empty list.
    """
    if not raw_text or not raw_text.strip():
        return []
    reader = csv.DictReader(io.StringIO(raw_text))
    rows = []
    for row in reader:
        cleaned = {k: v.strip() for k, v in row.items() if k is not None}
        rows.append(cleaned)
    return rows


# ── Pipeline function – triggers Coverage Delta (regression) ─────────────────
def run_pipeline(records: list[dict]) -> dict:
    """
    Multi-step processing; coverage delta is detected between versions.
    Change Impact Analysis: side effects ripple through steps.
    """
    step1 = [r for r in records if r.get("active")]       # filter
    step2 = [r for r in step1 if int(r.get("score", 0)) > 50]  # score gate
    step3 = sorted(step2, key=lambda r: r.get("name", ""))     # sort
    return {
        "input_count": len(records),
        "filtered_count": len(step1),
        "passed_count": len(step2),
        "sorted_result": step3,
    }


# ── Reporting function – triggers Audit Trail Verification ───────────────────
def generate_report(data: dict) -> str:
    """
    Formats a pipeline result into a human-readable string.
    All-Uses: accesses every key in 'data' dict.
    """
    lines = [
        f"Input records : {data.get('input_count', 0)}",
        f"After filter  : {data.get('filtered_count', 0)}",
        f"Passed gate   : {data.get('passed_count', 0)}",
    ]
    return "\n".join(lines)


# ── Unreachable use – Ghost Use Identification ────────────────────────────────
def ghost_use_example(flag: bool) -> int:
    value = 42          # DEF value
    if flag:
        return 0        # early return – 'value' USE below is never reached when flag=True
    return value        # USE value – only reached when flag=False
