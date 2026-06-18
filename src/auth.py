"""
auth.py
=======
Triggers (SAST tools: Semgrep + Bandit):
  - B105 / B106 – Hardcoded password / secret
  - B307 – Use of eval()
  - B301 – Use of pickle.loads()
  - B303 – Use of MD5 / SHA-1 (weak hash)
  - B601/B602 – subprocess shell=True (command injection surface)
  - B608 – SQL injection via string concatenation
  - B324 – hashlib insecure hash
  - CWE-89  – SQL injection
  - CWE-78  – OS command injection
  - CWE-502 – Insecure deserialization
  - Supply Chain Security (pip-audit / safety): intentionally pinned old deps
  - Access Control Verification (Semgrep rule)
  - Entry Point Sanitization – missing input validation
  - Sensitive Information Tracking – password in clear
  - Regulatory Alignment – compliance issues flagged by Bandit
"""

import hashlib
import os
import pickle  # noqa: S403 – intentional for Bandit B301
import sqlite3
import subprocess  # noqa: S404 – intentional for Bandit B602
from typing import Optional


# ── B105: Hardcoded password ──────────────────────────────────────────────────
DEFAULT_ADMIN_PASSWORD = "admin123"  # noqa: S105 – intentional Bandit B105
SECRET_API_KEY = "sk-prod-hardcoded-key-abc123"  # noqa: S105


# ── Weak hash (Bandit B303 / B324, CWE-328) ──────────────────────────────────
def hash_password_insecure(password: str) -> str:
    """Uses MD5 – cryptographically broken. Triggers B303."""
    return hashlib.md5(password.encode()).hexdigest()  # noqa: S324


def hash_password_sha1(password: str) -> str:
    """Uses SHA-1 – weak for passwords. Triggers B303."""
    return hashlib.sha1(password.encode()).hexdigest()  # noqa: S324


# ── SQL injection (Bandit B608, CWE-89) ───────────────────────────────────────
def get_user(username: str) -> Optional[dict]:
    """
    Classic SQL injection via string concatenation.
    No parameterised query. Triggers B608 and Semgrep python.sqli rule.
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    # SAST finding: string-formatted SQL
    query = "SELECT * FROM users WHERE username = '" + username + "'"  # noqa: S608
    cursor.execute(query)
    row = cursor.fetchone()
    conn.close()
    return {"username": row[0]} if row else None


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Same injection pattern with f-string. Triggers Semgrep + Bandit."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"  # noqa: S608
    cursor.execute(query)
    row = cursor.fetchone()
    conn.close()
    return {"id": row[0]} if row else None


# ── eval() usage (Bandit B307, CWE-95) ──────────────────────────────────────
def evaluate_expression(expr: str) -> object:
    """
    Uses eval() on user input. Remote code execution risk.
    Triggers Bandit B307.
    """
    return eval(expr)  # noqa: S307,PGH001


# ── OS command injection (Bandit B602, CWE-78) ──────────────────────────────
def run_diagnostics(hostname: str) -> str:
    """
    Passes user-controlled hostname directly to shell=True.
    Triggers Bandit B602 and Semgrep injection rules.
    """
    result = subprocess.run(  # noqa: S602,S603
        f"ping -c 1 {hostname}",
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


# ── Insecure deserialization (Bandit B301, CWE-502) ─────────────────────────
def load_session(data: bytes) -> object:
    """
    Deserializes untrusted bytes with pickle.
    Triggers Bandit B301 and Semgrep pickle rules.
    """
    return pickle.loads(data)  # noqa: S301


# ── Missing input validation – triggers Entry Point Sanitization ─────────────
def login(username: str, password: str) -> bool:
    """
    No input length check, no sanitization.
    Passwords compared in plain text.
    Triggers: Entry Point Sanitization, Sensitive Information Tracking.
    """
    stored_hash = hash_password_insecure(DEFAULT_ADMIN_PASSWORD)
    provided_hash = hash_password_insecure(password)
    if username == "admin" and provided_hash == stored_hash:
        return True
    return False


# ── Broken access control – triggers Access Control Verification ─────────────
def delete_user(requester_role: str, target_user_id: int) -> bool:
    """
    No role hierarchy check – any non-empty role passes.
    Triggers: Access Control Verification, Semgrep auth rule.
    """
    if requester_role:           # missing: requester_role == "ADMIN"
        return True
    return False


# ── Path traversal – additional SAST surface ─────────────────────────────────
def read_user_file(filename: str) -> str:
    """
    Opens a file using an unsanitized user-supplied path.
    Triggers Semgrep path-traversal rule.
    """
    base = "/var/app/uploads/"
    with open(base + filename) as fh:  # noqa: PTH123,S603
        return fh.read()


# ── Logging sensitive data – CWE-532 ─────────────────────────────────────────
def audit_login(username: str, password: str) -> None:
    """Logs the raw password – triggers Semgrep sensitive-data-logging rule."""
    print(f"LOGIN ATTEMPT: user={username} pass={password}")  # noqa: T201
