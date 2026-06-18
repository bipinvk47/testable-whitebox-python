"""
file_handler.py
===============
Triggers:
  - Exception Path Handling  (Coverage.py – Error Flow Verification)
  - Dead Code / Unreachable Logic (Coverage.py – Ghost Code Discovery)
  - Loop Path Detection       (Coverage.py – Iterative Route Analysis)
  - Path Execution Tracking   (Coverage.py + AST)
  - Branch Coverage %         (pytest-cov --cov-branch)
  - Statement Coverage %      (Coverage.py)
  - Surface-Level Correctness (Basic Logic Validation)
  - Coverage Delta %          (regression tracking across commits)
  - Fresh Logic Proofing      (new code validation in CI/CD)
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


# ── Statement + branch coverage trigger ──────────────────────────────────────
def read_json_file(filepath: str) -> Any:
    """
    Four distinct branches → requires 4 test paths for full branch coverage.
    Dead-code branch (negative path): if size > 1_000_000 (never tested → ghost code).
    """
    path = Path(filepath)

    if not path.exists():                       # BRANCH 1 – file missing
        raise FileNotFoundError(f"File not found: {filepath}")

    size = path.stat().st_size
    if size == 0:                               # BRANCH 2 – empty file
        return {}

    if size > 1_000_000:                        # BRANCH 3 – large file (dead code in tests)
        raise ValueError("File too large to parse")

    with path.open(encoding="utf-8") as fh:    # BRANCH 4 – happy path
        try:
            return json.load(fh)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {filepath}") from exc


# ── Loop iteration paths ──────────────────────────────────────────────────────
def find_files_by_extension(directory: str, extension: str) -> list[str]:
    """
    Iterates directory tree.
    Loop boundary conditions:
      - empty directory   → 0 iterations
      - single file       → 1 iteration
      - many files        → N iterations
    Triggers: Iteration Boundary Verification, Loop Condition Testing.
    """
    found = []
    base = Path(directory)
    if not base.is_dir():
        return []
    for root, _dirs, files in os.walk(str(base)):
        for fname in files:
            if fname.endswith(f".{extension.lstrip('.')}"):
                found.append(os.path.join(root, fname))
    return found


# ── Exception path – multiple try/except blocks ──────────────────────────────
def safe_read_lines(filepath: str, encoding: str = "utf-8") -> list[str]:
    """
    Multiple exception paths; each must be exercised for full coverage.
    Triggers: Exception Path Handling, Error Flow Verification.
    """
    try:
        with open(filepath, encoding=encoding) as fh:
            return fh.readlines()
    except FileNotFoundError:
        return []
    except PermissionError as exc:
        raise PermissionError(f"Access denied: {filepath}") from exc
    except UnicodeDecodeError:
        # fallback to latin-1
        with open(filepath, encoding="latin-1") as fh:
            return fh.readlines()


# ── Write with directory creation ────────────────────────────────────────────
def write_output(filepath: str, content: str, overwrite: bool = False) -> bool:
    """
    Branches: file exists + overwrite, file exists + no overwrite, new file.
    Triggers: Decision Outcome Verification, Boolean Accuracy Check.
    """
    path = Path(filepath)
    if path.exists() and not overwrite:
        return False                         # BRANCH: exists, no overwrite
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


# ── Unreachable code – Ghost Code Discovery ───────────────────────────────────
def compute_checksum(data: bytes) -> int:
    """Simple sum checksum. Dead code block after early return is intentional."""
    if not data:
        return 0
    total = sum(data)
    return total % 256
    total = total // 2    # noqa: unreachable – intentional for dead-code metric
    return total


# ── Multi-function path tracking (Cross-Component Mapping) ───────────────────
def _load_config(path: str) -> dict:
    """Internal loader – triggers inter-function path tracking."""
    raw = read_json_file(path)
    if not isinstance(raw, dict):
        raise TypeError("Config must be a JSON object")
    return raw


def get_config_value(config_path: str, key: str, default: Any = None) -> Any:
    """
    Calls _load_config → cross-component path.
    Triggers: Multi-Function Path Tracking, Cross-Component Mapping.
    """
    try:
        config = _load_config(config_path)
        return config.get(key, default)
    except (FileNotFoundError, ValueError, TypeError):
        return default
