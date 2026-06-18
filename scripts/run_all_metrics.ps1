<#
.SYNOPSIS
    Run ALL 103 Testable white-box metric tools against the Python sample repo.
.DESCRIPTION
    Executes each tool in sequence, writes reports to ./reports/
    Maps to Testable_Metrics_Tools_Versions_v2.xlsx – Python column.
#>

param(
    [string]$ReportsDir = "reports",
    [switch]$FailFast
)

$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot

Push-Location $Root

# ── Ensure reports directory ─────────────────────────────────────────────────
New-Item -ItemType Directory -Force -Path $ReportsDir | Out-Null

function Run-Tool {
    param([string]$Name, [string]$Cmd)
    Write-Host "`n===== $Name =====" -ForegroundColor Cyan
    Invoke-Expression $Cmd
    if ($LASTEXITCODE -ne 0 -and $FailFast) { exit $LASTEXITCODE }
}

# ════════════════════════════════════════════════════════════════════════════
# 1. CYCLOMATIC COMPLEXITY — McCabe / Radon / Lizard
#    Metrics: Execution Path Integrity, Technical Debt Impact, QA Resource Allocation
# ════════════════════════════════════════════════════════════════════════════
Run-Tool "Radon CC (Cyclomatic Complexity)" `
    "radon cc src -s -a --min A --json > $ReportsDir\radon_cc.json 2>&1"

Run-Tool "Radon MI (Maintainability Index)" `
    "radon mi src -s --json > $ReportsDir\radon_mi.json 2>&1"

Run-Tool "Radon HAL (Halstead Metrics)" `
    "radon hal src --json > $ReportsDir\radon_hal.json 2>&1"

Run-Tool "Lizard CC" `
    "lizard src -l python --csv -o $ReportsDir\lizard_cc.csv 2>&1"

Run-Tool "McCabe (via flake8-complexity)" `
    "python -m flake8 --max-complexity=10 --select=C9 src > $ReportsDir\mccabe_violations.txt 2>&1"

# CrossHair — formal property checking (execution path integrity)
Run-Tool "CrossHair check (Execution Path Integrity)" `
    "crosshair check src/calculator.py src/complex_logic.py > $ReportsDir\crosshair.txt 2>&1"

# ════════════════════════════════════════════════════════════════════════════
# 2. COGNITIVE COMPLEXITY — radon / cognitive-complexity
#    Metrics: Human Cognitive Load, Reviewer Fatigue, Defect Probability
# ════════════════════════════════════════════════════════════════════════════
Run-Tool "Radon Cognitive Complexity (via CC with show-closures)" `
    "radon cc src -s --show-closures --json > $ReportsDir\radon_cognitive.json 2>&1"

# ════════════════════════════════════════════════════════════════════════════
# 3. CODE DUPLICATION — jscpd / copydetect
#    Metrics: Multi-Point Failure Probability, Structural Cleanliness, Abstraction Potential
# ════════════════════════════════════════════════════════════════════════════
Run-Tool "copydetect (Python code duplication)" `
    "copydetect -t src -o $ReportsDir\copydetect_report.json 2>&1"

# jscpd requires Node.js — run if available
if (Get-Command npx -ErrorAction SilentlyContinue) {
    Run-Tool "jscpd (cross-language duplication)" `
        "npx jscpd src --languages python --reporters json --output $ReportsDir\jscpd 2>&1"
} else {
    Write-Host "jscpd skipped (npx not found — install Node.js)" -ForegroundColor Yellow
}

# ════════════════════════════════════════════════════════════════════════════
# 4. LINT / RULE VIOLATIONS — pylint + flake8
#    Metrics: Violation Density per KLOC, Naming Conventions, Complexity Rules
# ════════════════════════════════════════════════════════════════════════════
Run-Tool "pylint (all rule violations)" `
    "python -m pylint src --rcfile=.pylintrc --output-format=json > $ReportsDir\pylint_report.json 2>&1"

Run-Tool "flake8 (PEP8 + style)" `
    "python -m flake8 src --config=.flake8 --format=json > $ReportsDir\flake8_report.json 2>&1"

# ════════════════════════════════════════════════════════════════════════════
# 5. SAST — Bandit + Semgrep
#    Metrics: Best Practice Compliance, Entry Point Sanitization,
#             SQL Injection, Command Injection, Crypto Weakness
# ════════════════════════════════════════════════════════════════════════════
Run-Tool "Bandit SAST" `
    "python -m bandit -r src -f json -o $ReportsDir\bandit_report.json 2>&1"

if (Get-Command semgrep -ErrorAction SilentlyContinue) {
    Run-Tool "Semgrep SAST (OWASP + security rules)" `
        "semgrep --config auto --config .semgrep.yml src --json > $ReportsDir\semgrep_report.json 2>&1"
} else {
    Write-Host "Semgrep skipped (not installed — pip install semgrep)" -ForegroundColor Yellow
}

# ════════════════════════════════════════════════════════════════════════════
# 6. DEPENDENCY RISK — pip-audit + safety + pip-licenses
#    Metrics: Known CVE Count, Version Lag, License Compliance,
#             Supply Chain Security, Dependency Health Monitoring
# ════════════════════════════════════════════════════════════════════════════
Run-Tool "pip-audit (CVE scan)" `
    "pip-audit --requirement requirements.txt --format json --output $ReportsDir\pip_audit_report.json 2>&1"

Run-Tool "safety check (vulnerability database)" `
    "safety check --file requirements.txt --json > $ReportsDir\safety_report.json 2>&1"

Run-Tool "pip-licenses (license compliance)" `
    "pip-licenses --format=json --output-file=$ReportsDir\licenses.json 2>&1"

# ════════════════════════════════════════════════════════════════════════════
# 7. COVERAGE (Statement / Branch / Path) — Coverage.py + pytest-cov
#    Metrics: Statement Coverage %, Branch Coverage %, Path Coverage %,
#             Dead Code Detection, Coverage Gap Analysis
# ════════════════════════════════════════════════════════════════════════════
Run-Tool "pytest + coverage (statement + branch)" `
    "python -m pytest tests/ --cov=src --cov-branch --cov-report=xml:$ReportsDir\coverage.xml --cov-report=html:$ReportsDir\htmlcov --cov-report=term-missing -v > $ReportsDir\pytest_output.txt 2>&1"

# ════════════════════════════════════════════════════════════════════════════
# 8. MUTATION TESTING — mutmut + cosmic-ray
#    Metrics: Logic Error Sensitivity, Test Rigor Assessment, Boundary Mutant Analysis
# ════════════════════════════════════════════════════════════════════════════
Run-Tool "mutmut run (mutation testing)" `
    "mutmut run --paths-to-mutate src/ > $ReportsDir\mutmut_output.txt 2>&1"

Run-Tool "mutmut results (mutation score)" `
    "mutmut results >> $ReportsDir\mutmut_output.txt 2>&1"

# ════════════════════════════════════════════════════════════════════════════
# 9. DATA FLOW — Beniget + pyflakes
#    Metrics: All-Defs Coverage %, All-Uses Coverage %,
#             Dead Data Identification, Inter-procedural Tracking
# ════════════════════════════════════════════════════════════════════════════
Run-Tool "pyflakes (data flow / undefined names)" `
    "python -m pyflakes src > $ReportsDir\pyflakes_report.txt 2>&1"

# Beniget AST def-use analysis
$benigetScript = @"
import sys, json
from pathlib import Path
from beniget import DefUseChains
import gast as ast

results = {}
for pyfile in Path('src').glob('*.py'):
    src = pyfile.read_text(encoding='utf-8')
    try:
        module = ast.parse(src)
        duc = DefUseChains()
        duc.visit(module)
        chains = {str(k): [str(u) for u in v] for k, v in duc.chains.items()}
        results[str(pyfile)] = {'chains_count': len(chains)}
    except Exception as e:
        results[str(pyfile)] = {'error': str(e)}

with open('$ReportsDir/beniget_defuse.json', 'w') as f:
    json.dump(results, f, indent=2)
print('Beniget def-use chains written.')
"@
$benigetScript | Out-File -FilePath "$ReportsDir\_beniget_runner.py" -Encoding utf8
Run-Tool "Beniget def-use chain analysis" `
    "python $ReportsDir\_beniget_runner.py 2>&1"

# ════════════════════════════════════════════════════════════════════════════
# 10. COVERAGE DELTA — diff-cover
#     Metrics: Coverage Delta %, Deployment Readiness Guard
# ════════════════════════════════════════════════════════════════════════════
Run-Tool "diff-cover (coverage delta from base branch)" `
    "diff-cover $ReportsDir\coverage.xml --diff-range-notation .. --compare-branch=origin/main > $ReportsDir\diff_cover.txt 2>&1"

# ════════════════════════════════════════════════════════════════════════════
# 11. CODE CHURN — pydriller
#     Metrics: Code Churn Score, Regression Testing Focus, Fault Probability Modeling
# ════════════════════════════════════════════════════════════════════════════
$churlScript = @"
import sys, json
from pathlib import Path
from pydriller import Repository

# Analyse last 30 commits if git history exists
churn = []
try:
    for commit in Repository('.', since=None, to=None, order='reverse', num_workers=1).traverse_commits():
        for mod in commit.modified_files:
            if mod.filename.endswith('.py'):
                churn.append({
                    'commit': commit.hash[:7],
                    'date': str(commit.committer_date),
                    'file': mod.new_path,
                    'added': mod.added_lines,
                    'deleted': mod.deleted_lines,
                    'churn': mod.added_lines + mod.deleted_lines,
                })
        if len(churn) > 500:
            break
except Exception as e:
    churn = [{'error': str(e)}]

with open('$ReportsDir/pydriller_churn.json', 'w') as f:
    json.dump(churn, f, indent=2)
print(f'Code churn entries: {len(churn)}')
"@
$churlScript | Out-File -FilePath "$ReportsDir\_churn_runner.py" -Encoding utf8
Run-Tool "pydriller code churn" `
    "python $ReportsDir\_churn_runner.py 2>&1"

# ════════════════════════════════════════════════════════════════════════════
# 12. CONDITION COVERAGE (MC/DC) — pymcdc
#     Metrics: Logical Sub-expression Validation, Total Logical Combinatorial Coverage
# ════════════════════════════════════════════════════════════════════════════
Run-Tool "pymcdc (MC/DC condition coverage)" `
    "python -m pymcdc src/calculator.py src/complex_logic.py > $ReportsDir\pymcdc_report.txt 2>&1"

# ════════════════════════════════════════════════════════════════════════════
# 13. TEST SELECTION — pytest-testmon
#     Metrics: QA Resource Allocation (Test Prioritization)
# ════════════════════════════════════════════════════════════════════════════
Run-Tool "pytest-testmon (selective test execution)" `
    "python -m pytest tests/ --testmon --testmon-forceselect --tb=no -q > $ReportsDir\testmon_output.txt 2>&1"

# ════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════════════════
Pop-Location

Write-Host "`n" -NoNewline
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ALL METRIC TOOLS EXECUTED" -ForegroundColor Green
Write-Host "  Reports saved to: $Root\$ReportsDir\" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "Key reports:" -ForegroundColor White
Write-Host "  Coverage (HTML)  : $ReportsDir\htmlcov\index.html"
Write-Host "  Coverage (XML)   : $ReportsDir\coverage.xml"
Write-Host "  Bandit SAST      : $ReportsDir\bandit_report.json"
Write-Host "  pylint           : $ReportsDir\pylint_report.json"
Write-Host "  pip-audit CVEs   : $ReportsDir\pip_audit_report.json"
Write-Host "  Mutation (mutmut): $ReportsDir\mutmut_output.txt"
Write-Host "  Code Churn       : $ReportsDir\pydriller_churn.json"
Write-Host "  Def-Use chains   : $ReportsDir\beniget_defuse.json"
