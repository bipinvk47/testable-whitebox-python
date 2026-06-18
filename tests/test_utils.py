"""
test_utils.py
=============
Covers utils.py to generate lint violation reports
and ensure pydriller / code-churn analysis has a coverage baseline.
"""
from src.utils import (
    bad_style_aggregated,
    calc,
    compute_tax,
    get_env_or_default,
    get_platform_info,
    getUserName,
    get_user_age,
    high_branch_count,
    no_docstring_function,
    unused_vars_example,
)


class TestCalc:
    def test_basic(self):
        assert calc(2, 3, 4) == 20


class TestUnusedVars:
    def test_returns_correct(self):
        assert unused_vars_example() == 42


class TestBadStyle:
    def test_sum(self):
        assert bad_style_aggregated(3, 7) == 10


class TestHighBranchCount:
    def test_deep_nesting(self):
        assert high_branch_count(0, 0, True, True, True, True) == "deep"

    def test_c_only(self):
        assert high_branch_count(0, 0, True, False, False, False) == "c_only"

    def test_none(self):
        assert high_branch_count(0, 0, False, False, False, False) == "none"

    def test_a_equals_1(self):
        high_branch_count(1, 0, False, False, False, False)

    def test_b_equals_2(self):
        high_branch_count(0, 2, False, False, False, False)


class TestEnv:
    def test_default(self):
        result = get_env_or_default("__NONEXISTENT_VAR__", "default_val")
        assert result == "default_val"


class TestNaming:
    def test_get_user_name_camel(self):
        assert getUserName() == "admin"

    def test_get_user_age_snake(self):
        assert get_user_age() == 30


class TestNoDocstring:
    def test_doubles(self):
        assert no_docstring_function(5) == 10


class TestPlatform:
    def test_returns_tuple(self):
        result = get_platform_info()
        assert isinstance(result, tuple) and len(result) == 2


class TestComputeTax:
    def test_tax(self):
        assert compute_tax(100, 0.1) == 10.0
