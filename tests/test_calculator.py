"""
test_calculator.py
==================
Coverage targets:
  - Statement Coverage %   : 100% of calculator.py statements
  - Branch Coverage %      : True + False of every if/else
  - Decision Coverage      : every branch outcome verified
  - MC-DC / Condition Cov  : compound predicates exercised individually
  - Path Coverage          : multiple independent paths through functions
  - Mutation Score         : assertions tight enough to kill mutations
  - Regression / Delta     : stable baseline for coverage delta tracking
"""
import pytest
from src.calculator import (
    add,
    classify_score,
    compute_insurance_premium,
    divide,
    factorial,
    grade_student,
    multiply,
    process_number,
    safe_sqrt,
    subtract,
)


# ── Basic arithmetic (statement coverage) ────────────────────────────────────
class TestBasicArithmetic:
    def test_add_positive(self):
        assert add(3, 4) == 7

    def test_add_negative(self):
        assert add(-1, -2) == -3

    def test_add_zero(self):
        assert add(0, 5) == 5

    def test_subtract(self):
        assert subtract(10, 4) == 6

    def test_multiply(self):
        assert multiply(3, 5) == 15

    def test_multiply_by_zero(self):
        assert multiply(7, 0) == 0


# ── divide – branch coverage (both True/False of each if) ────────────────────
class TestDivide:
    def test_normal_division(self):
        assert divide(10, 2) == 5.0

    def test_division_by_zero_raises(self):
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(5, 0)

    def test_non_numeric_numerator_raises(self):
        with pytest.raises(TypeError):
            divide("ten", 2)

    def test_float_division(self):
        assert divide(7.0, 2.0) == pytest.approx(3.5)


# ── classify_score – MC-DC: each boolean independently changes outcome ────────
class TestClassifyScore:
    # Guard branch
    def test_invalid_low(self):
        assert classify_score(-1, False, False) == "INVALID"

    def test_invalid_high(self):
        assert classify_score(101, False, False) == "INVALID"

    # EXCELLENT+ requires score >= 90 AND (is_bonus OR is_premium)
    def test_excellent_with_bonus(self):
        assert classify_score(95, True, False) == "EXCELLENT+"

    def test_excellent_with_premium(self):
        assert classify_score(95, False, True) == "EXCELLENT+"

    def test_excellent_with_both(self):
        assert classify_score(95, True, True) == "EXCELLENT+"

    # score >= 90 but neither flag → falls to GOOD
    def test_ninety_no_flags(self):
        assert classify_score(90, False, False) == "GOOD"

    def test_good(self):
        assert classify_score(80, False, False) == "GOOD"

    def test_average(self):
        assert classify_score(60, False, False) == "AVERAGE"

    def test_poor(self):
        assert classify_score(30, False, False) == "POOR"

    # Exact boundary (score == 75)
    def test_boundary_good(self):
        assert classify_score(75, False, False) == "GOOD"

    def test_boundary_average(self):
        assert classify_score(74, False, False) == "AVERAGE"


# ── grade_student – all grade paths ──────────────────────────────────────────
class TestGradeStudent:
    def test_detained_low_attendance(self):
        assert grade_student(85, 60, True) == "DETAINED"

    def test_f_failed_exam_low_marks(self):
        assert grade_student(30, 80, False) == "F"

    def test_e_failed_exam_passing_marks(self):
        assert grade_student(45, 80, False) == "E"

    def test_a_plus(self):
        assert grade_student(92, 80, True) == "A+"

    def test_a(self):
        assert grade_student(85, 80, True) == "A"

    def test_b(self):
        assert grade_student(72, 80, True) == "B"

    def test_c(self):
        assert grade_student(65, 80, True) == "C"

    def test_d(self):
        assert grade_student(55, 80, True) == "D"

    def test_f_passed_but_below_50(self):
        assert grade_student(45, 80, True) == "F"


# ── compute_insurance_premium – path coverage across all branches ─────────────
class TestComputeInsurancePremium:
    def test_young_normal_bmi_non_smoker(self):
        result = compute_insurance_premium(22, 22.0, False, False, "URBAN", 2)
        assert result > 0

    def test_elderly_obese_smoker_preexisting(self):
        result = compute_insurance_premium(65, 32.0, True, True, "RURAL", 5)
        assert result > compute_insurance_premium(22, 22.0, False, False, "URBAN", 1)

    def test_middle_age_overweight_smoker_no_preexisting(self):
        result = compute_insurance_premium(45, 27.5, True, False, "SUBURBAN", 3)
        assert result > 500

    def test_underweight_young(self):
        result = compute_insurance_premium(20, 17.0, False, False, "URBAN", 1)
        assert result > 0

    def test_unknown_region(self):
        result = compute_insurance_premium(35, 24.0, False, False, "PACIFIC", 2)
        assert result > 0


# ── factorial – loop boundary testing ────────────────────────────────────────
class TestFactorial:
    def test_zero(self):
        assert factorial(0) == 1

    def test_one(self):
        assert factorial(1) == 1

    def test_five(self):
        assert factorial(5) == 120

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            factorial(-1)


# ── safe_sqrt – exception path testing ───────────────────────────────────────
class TestSafeSqrt:
    def test_positive(self):
        assert safe_sqrt(9) == pytest.approx(3.0)

    def test_zero(self):
        assert safe_sqrt(0) == 0.0

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="Cannot compute sqrt"):
            safe_sqrt(-4)

    def test_non_numeric_raises(self):
        with pytest.raises(TypeError):
            safe_sqrt("abc")


# ── process_number – inter-procedural data flow ───────────────────────────────
class TestProcessNumber:
    def test_integer(self):
        assert process_number(5) == pytest.approx(10.0)

    def test_float_string(self):
        assert process_number("3.5") == pytest.approx(7.0)
