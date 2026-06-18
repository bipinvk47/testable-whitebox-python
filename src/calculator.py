"""
calculator.py
=============
Triggers:
  - Cyclomatic Complexity (McCabe / Crosshair): CC ranges from 1 (simple) to 12+ (complex)
  - Decision Coverage (Coverage.py + McCabe): every if/else branch
  - Condition Coverage / MC-DC (pymcdc): compound boolean expressions
  - Cognitive Complexity (radon): nested control flow
  - Path Coverage (Coverage.py + AST): multiple independent paths
  - Data-flow All-Defs / All-Uses (Beniget + pyflakes): variable def-use pairs
"""

import math


# ── Simple CC=1 function ─────────────────────────────────────────────────────
def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


# ── CC=3 – introduces two decision points ────────────────────────────────────
def divide(numerator, denominator):
    if denominator == 0:                 # branch 1
        raise ValueError("Cannot divide by zero")
    if not isinstance(numerator, (int, float)):  # branch 2
        raise TypeError("Numerator must be numeric")
    return numerator / denominator


# ── CC=5 – compound boolean (MC-DC trigger) ──────────────────────────────────
def classify_score(score, is_bonus, is_premium):
    """
    Compound predicate:  score >= 90 and (is_bonus or is_premium)
    Triggers pymcdc MC-DC condition coverage.
    """
    if score < 0 or score > 100:             # guard
        return "INVALID"
    if score >= 90 and (is_bonus or is_premium):
        return "EXCELLENT+"
    if score >= 75:
        return "GOOD"
    if score >= 50:
        return "AVERAGE"
    return "POOR"


# ── CC=8 – decision-heavy function ───────────────────────────────────────────
def grade_student(marks, attendance, passed_exam):
    """McCabe CC ≈ 8; triggers Decision Outcome Verification metric."""
    grade = "F"
    if attendance < 75:
        return "DETAINED"
    if not passed_exam:
        if marks >= 40:
            grade = "E"
        else:
            grade = "F"
    elif marks >= 90:
        grade = "A+"
    elif marks >= 80:
        grade = "A"
    elif marks >= 70:
        grade = "B"
    elif marks >= 60:
        grade = "C"
    elif marks >= 50:
        grade = "D"
    return grade


# ── CC=12 – high-complexity function; triggers Technical Debt metric ──────────
def compute_insurance_premium(
    age, bmi, smoker, pre_existing, region, occupation_risk
):
    """
    Deliberately high cyclomatic complexity (CC ≈ 12).
    Triggers: Technical Debt Impact, QA Resource Allocation, Execution Path Integrity.
    """
    base = 500.0
    risk_factor = 1.0

    # Age-based risk
    if age < 25:
        risk_factor += 0.1
    elif age < 40:
        risk_factor += 0.0
    elif age < 60:
        risk_factor += 0.2
    else:
        risk_factor += 0.4

    # BMI-based risk
    if bmi < 18.5:
        risk_factor += 0.05
    elif bmi <= 24.9:
        pass
    elif bmi <= 29.9:
        risk_factor += 0.1
    else:
        risk_factor += 0.25

    # Smoker + pre-existing compound logic (MC-DC trigger)
    if smoker and pre_existing:
        risk_factor += 0.5
    elif smoker or pre_existing:
        risk_factor += 0.2

    # Regional modifier
    region_modifiers = {"URBAN": 0.05, "SUBURBAN": 0.0, "RURAL": -0.05}
    risk_factor += region_modifiers.get(region.upper(), 0.0)

    # Occupation risk (1–5 scale)
    if occupation_risk >= 5:
        risk_factor += 0.3
    elif occupation_risk >= 3:
        risk_factor += 0.1

    return round(base * risk_factor, 2)


# ── Dead code (never executed) – triggers Unreachable Logic Identification ────
def _legacy_compute(x):  # noqa: F401
    result = x * 2
    return result
    result = result + 1  # noqa: unreachable – intentional dead code
    return result


# ── Loop boundary – triggers Iteration Boundary Verification ─────────────────
def factorial(n):
    """Iterative factorial; loop-path triggers branch/loop coverage metrics."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result


# ── Exception path – triggers Error Flow Verification ────────────────────────
def safe_sqrt(value):
    """Raises on negative; triggers Exception Path Handling metric."""
    try:
        if value < 0:
            raise ValueError(f"Cannot compute sqrt of {value}")
        return math.sqrt(value)
    except TypeError as exc:
        raise TypeError("Input must be numeric") from exc


# ── Cross-function data flow – triggers Inter-procedural Tracking ────────────
def _validate_number(value):
    """Helper – defines 'validated' variable used downstream."""
    validated = float(value)   # definition (D)
    return validated


def process_number(raw):
    """Uses the variable defined in _validate_number – All-Uses coverage."""
    validated = _validate_number(raw)   # use (U)
    return validated * 2
