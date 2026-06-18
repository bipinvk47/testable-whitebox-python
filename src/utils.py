"""
utils.py
========
Triggers:
  - Lint / Rule Violations (pylint + flake8):
      * Violation Density per KLOC
      * Unused Variable Detection   (F841)
      * Naming Convention Violation (C0103)
      * Long lines                  (E501)
      * Missing docstring           (C0114/C0116)
      * Complexity rule             (R0912, R0915)
      * Aggregated Risk Assessment  (multiple violations)
      * Impact Prioritization       (severity categories)
      * Custom Rule Validation      (project-specific .pylintrc)
      * CI/CD Integration           (non-zero exit code if violations found)
      * Quality Audit Trail         (--output-format=json)
  - Code Churn (pydriller): this file is modified in multiple commits
  - Test Regression / Coverage Delta: added functions between commits

NOTE: Some violations below are intentional for metric triggering.
"""
# flake8: noqa
# pylint: disable=invalid-name,missing-function-docstring

import os
import sys


# ── Naming convention violation (C0103) – short names ────────────────────────
def calc(x, y, z):   # C0103: function name too short; params too short
    a = x + y        # C0103: variable 'a'
    b = a * z        # C0103: variable 'b'
    return b


# ── Unused variable (F841, W0612) ────────────────────────────────────────────
def unused_vars_example():
    result = 42           # used
    temp = "throwaway"   # F841 – assigned but never used
    another = [1, 2, 3]  # F841 – assigned but never used
    return result


# ── Long line (E501) – exceeds 79/100 char limit ─────────────────────────────
VERY_LONG_CONSTANT = "This is a deliberately very long string constant that exceeds the PEP 8 line length limit of 79 characters and will be flagged by flake8 E501 rule"

def get_long_description(item_id, item_name, item_category, item_price, item_currency):
    return f"Item ID={item_id}, Name={item_name}, Category={item_category}, Price={item_price} {item_currency}"


# ── Missing docstring (C0116) ─────────────────────────────────────────────────
def no_docstring_function(value):
    return value * 2


class NoDocstringClass:  # C0115
    def method(self):    # C0116
        pass


# ── Multiple violations in one function ──────────────────────────────────────
def bad_style_aggregated(X, Y):  # C0103 (X, Y uppercase)
    Sum = X + Y          # C0103 (Sum capitalised)
    Diff = X - Y         # C0103 (Diff)
    unused = Sum * Diff  # F841, C0103
    return Sum


# ── Complexity rule trigger (R0912) – too many branches ──────────────────────
def high_branch_count(a, b, c, d, e, f):  # R0912: too-many-branches
    if a == 1:
        pass
    elif a == 2:
        pass
    elif a == 3:
        pass
    if b == 1:
        pass
    elif b == 2:
        pass
    if c:
        if d:
            if e:
                if f:
                    return "deep"
                return "e_only"
            return "d_only"
        return "c_only"
    return "none"


# ── Import order violation (E401, C0411) ─────────────────────────────────────
# (sys and os imported at top; re-importing inside function is E401-style)
def get_platform_info():
    return sys.platform, os.getcwd()


# ── Wildcard import (F403) – intentional module-level, flagged by flake8 ─────
# Placed at module level as Python requires; flake8 F403 will still fire.
from math import *  # noqa: F401,F403,E402 – intentional wildcard import demo


def load_math():
    return sqrt(9)  # noqa: F405


# ── Configuration file handling – Environment Standardization ────────────────
def get_env_or_default(key: str, default: str = "") -> str:
    """Returns env var or default – used in CI/CD standardisation tests."""
    return os.environ.get(key, default)


# ── Syntactic Uniformity – mix of quote styles (W1405 / Q000) ────────────────
CONFIG_A = {'host': "localhost", 'port': 5432}   # mixed quotes
CONFIG_B = {"host": 'localhost', "port": 5432}   # mixed quotes

# ── Semantic Consistency – inconsistent naming styles ────────────────────────
def getUserName():     # camelCase instead of snake_case – C0103 / N802
    return "admin"


def get_user_age():    # correct snake_case
    return 30


# ── Impact Prioritization – mix of Error / Warning / Convention severity ─────
def divide_no_guard(a, b):   # W0612 potential ZeroDivisionError
    return a / b


# ── Project-Specific Enforcement (custom rule example) ───────────────────────
# Custom pylint rule: all public functions must have type hints
def compute_tax(amount, rate):   # missing type hints – would fire custom rule
    return amount * rate
