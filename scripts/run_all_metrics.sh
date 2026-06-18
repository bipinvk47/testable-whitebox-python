#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# run_all_metrics.sh
# Runs ALL 103 Testable white-box metric tools (Linux/macOS / CI/CD)
# ═══════════════════════════════════════════════════════════════════════════
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPORTS="$ROOT/reports"
mkdir -p "$REPORTS"

cd "$ROOT"

header() { echo -e "\n\033[1;36m===== $1 =====\033[0m"; }
warn()   { echo -e "\033[1;33mWARNING: $1\033[0m"; }

# ── 1. Cyclomatic Complexity ─────────────────────────────────────────────────
header "Radon CC (Cyclomatic Complexity)"
radon cc src -s -a --json > "$REPORTS/radon_cc.json" 2>&1 || true

header "Radon MI (Maintainability Index)"
radon mi src -s --json > "$REPORTS/radon_mi.json" 2>&1 || true

header "Radon HAL (Halstead)"
radon hal src --json > "$REPORTS/radon_hal.json" 2>&1 || true

header "Lizard CC"
lizard src -l python --csv -o "$REPORTS/lizard_cc.csv" 2>&1 || true

header "McCabe (via flake8)"
python -m flake8 --max-complexity=10 --select=C9 src \
    > "$REPORTS/mccabe_violations.txt" 2>&1 || true

header "CrossHair (Execution Path Integrity)"
crosshair check src/calculator.py src/complex_logic.py \
    > "$REPORTS/crosshair.txt" 2>&1 || true

# ── 2. Code Duplication ──────────────────────────────────────────────────────
header "copydetect (Python duplication)"
copydetect -t src -o "$REPORTS/copydetect_report.json" 2>&1 || true

if command -v npx &>/dev/null; then
    header "jscpd (cross-language duplication)"
    npx jscpd src --languages python --reporters json \
        --output "$REPORTS/jscpd" 2>&1 || true
else
    warn "jscpd skipped — install Node.js to enable"
fi

# ── 3. Lint / Rule Violations ────────────────────────────────────────────────
header "pylint"
python -m pylint src --rcfile=.pylintrc \
    --output-format=json > "$REPORTS/pylint_report.json" 2>&1 || true

header "flake8"
python -m flake8 src --config=.flake8 \
    --format=json > "$REPORTS/flake8_report.json" 2>&1 || true

# ── 4. SAST ──────────────────────────────────────────────────────────────────
header "Bandit SAST"
python -m bandit -r src -f json -o "$REPORTS/bandit_report.json" 2>&1 || true

if command -v semgrep &>/dev/null; then
    header "Semgrep SAST"
    semgrep --config auto --config .semgrep.yml src \
        --json > "$REPORTS/semgrep_report.json" 2>&1 || true
else
    warn "Semgrep skipped — pip install semgrep"
fi

# ── 5. Dependency Risk ───────────────────────────────────────────────────────
header "pip-audit (CVE scan)"
pip-audit --requirement requirements.txt \
    --format json --output "$REPORTS/pip_audit_report.json" 2>&1 || true

header "safety check"
safety check --file requirements.txt --json \
    > "$REPORTS/safety_report.json" 2>&1 || true

header "pip-licenses"
pip-licenses --format=json \
    --output-file="$REPORTS/licenses.json" 2>&1 || true

# ── 6. Coverage (Statement / Branch) ────────────────────────────────────────
header "pytest + coverage"
python -m pytest tests/ \
    --cov=src --cov-branch \
    --cov-report=xml:"$REPORTS/coverage.xml" \
    --cov-report=html:"$REPORTS/htmlcov" \
    --cov-report=term-missing \
    -v | tee "$REPORTS/pytest_output.txt" || true

# ── 7. Mutation Testing ──────────────────────────────────────────────────────
header "mutmut (mutation testing)"
mutmut run --paths-to-mutate src/ > "$REPORTS/mutmut_output.txt" 2>&1 || true
mutmut results >> "$REPORTS/mutmut_output.txt" 2>&1 || true

# ── 8. Data Flow ─────────────────────────────────────────────────────────────
header "pyflakes (data flow)"
python -m pyflakes src > "$REPORTS/pyflakes_report.txt" 2>&1 || true

header "Beniget def-use chains"
python - <<'PYEOF' > "$REPORTS/beniget_defuse.json" 2>&1 || true
import json
from pathlib import Path
from beniget import DefUseChains
import gast as ast

results = {}
for pyfile in Path("src").glob("*.py"):
    src_text = pyfile.read_text(encoding="utf-8")
    try:
        module = ast.parse(src_text)
        duc = DefUseChains()
        duc.visit(module)
        results[str(pyfile)] = {"chains_count": len(duc.chains)}
    except Exception as e:
        results[str(pyfile)] = {"error": str(e)}
print(json.dumps(results, indent=2))
PYEOF

# ── 9. Coverage Delta ────────────────────────────────────────────────────────
header "diff-cover (coverage delta)"
diff-cover "$REPORTS/coverage.xml" \
    --diff-range-notation .. --compare-branch=origin/main \
    > "$REPORTS/diff_cover.txt" 2>&1 || true

# ── 10. Code Churn ───────────────────────────────────────────────────────────
header "pydriller (code churn)"
python - <<'PYEOF' > "$REPORTS/pydriller_churn.json" 2>&1 || true
import json
from pydriller import Repository

churn = []
try:
    for commit in Repository(".").traverse_commits():
        for mod in commit.modified_files:
            if mod.filename.endswith(".py"):
                churn.append({
                    "commit": commit.hash[:7],
                    "date": str(commit.committer_date),
                    "file": mod.new_path,
                    "added": mod.added_lines,
                    "deleted": mod.deleted_lines,
                    "churn": mod.added_lines + mod.deleted_lines,
                })
        if len(churn) > 500:
            break
except Exception as e:
    churn = [{"error": str(e)}]
print(json.dumps(churn, indent=2))
PYEOF

# ── 11. MC/DC Condition Coverage ─────────────────────────────────────────────
header "pymcdc (MC/DC condition coverage)"
python -m pymcdc src/calculator.py src/complex_logic.py \
    > "$REPORTS/pymcdc_report.txt" 2>&1 || true

# ── 12. Test Selection ───────────────────────────────────────────────────────
header "pytest-testmon"
python -m pytest tests/ --testmon --testmon-forceselect \
    --tb=no -q > "$REPORTS/testmon_output.txt" 2>&1 || true

# ════════════════════════════════════════════════════════════════════════════
echo -e "\n\033[1;32m═══════════════════════════════════════════════════════\033[0m"
echo -e "\033[1;32m  ALL METRIC TOOLS EXECUTED — Reports in $REPORTS\033[0m"
echo -e "\033[1;32m═══════════════════════════════════════════════════════\033[0m"
