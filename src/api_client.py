"""
api_client.py
=============
Triggers:
  - Supply Chain Security (pip-audit / safety): uses pinned older deps
  - Dependency Health Monitoring: Community Vitality Tracking
  - Transitive Dependency Analysis: Hidden Relationship Mapping
  - License Compliance Testing: Legal Risk Validation
  - Risk Prioritization: Mitigation Effort Ranking
  - Outdated Dependency Detection: Version Lag Assessment
  - Known CVE Count (pip-audit)
  - Real-Time Alerting (Continuous Dependency Monitoring)
  - Semgrep: Best Practice Compliance, Sensitive Information Tracking
"""
import os

# Intentionally uses older library versions declared in requirements.txt
# to trigger pip-audit / safety CVE detection.
try:
    import requests          # pinned to older version in requirements.txt
except ImportError:
    requests = None  # type: ignore[assignment]

# ── Hardcoded base URL + token (Semgrep sensitive-data rule) ─────────────────
BASE_URL = "https://api.example.com/v1"
API_TOKEN = os.environ.get("API_TOKEN", "hardcoded-fallback-token-xyz")  # noqa: S105


def _get_headers() -> dict:
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }


# ── Missing TLS verification (Bandit B501) ────────────────────────────────────
def fetch_resource(endpoint: str) -> dict:
    """
    verify=False disables SSL cert check.
    Triggers Bandit B501 (requests_without_timeout) and Semgrep TLS rules.
    """
    if requests is None:
        return {}
    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        headers=_get_headers(),
        verify=False,         # noqa: S501 – intentional for Bandit B501
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


# ── No timeout on request (Bandit B113) ──────────────────────────────────────
def post_data(endpoint: str, payload: dict) -> dict:
    """Missing timeout → Denial-of-service risk. Bandit B113."""
    if requests is None:
        return {}
    response = requests.post(      # noqa: S113
        f"{BASE_URL}/{endpoint}",
        headers=_get_headers(),
        json=payload,
    )
    return response.json()


# ── Dependency version check helper (used by pip-audit analysis) ─────────────
PINNED_DEPS = {
    "requests": "2.25.1",      # known CVEs in older versions
    "urllib3": "1.26.4",       # known CVEs
    "cryptography": "3.4.7",   # known CVEs
    "Pillow": "8.2.0",         # known CVEs
    "pyyaml": "5.3.1",         # CVE-2020-14343
}


def get_pinned_version(package: str) -> str:
    return PINNED_DEPS.get(package, "unknown")
