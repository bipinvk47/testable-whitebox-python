"""
test_data_processor.py
======================
Targets:
  - All-Defs Coverage % (Beniget / pyflakes)
  - All-Uses Coverage % (coverage.py + Beniget)
  - C-Use and P-Use detection
  - Null and Boundary Flow Analysis
  - Coverage Delta (regression tracking)
  - Dead Data Identification
"""
import pytest
from src.data_processor import (
    classify_value,
    compute_average,
    filter_positives,
    generate_report,
    ghost_use_example,
    parse_csv,
    process_with_dead_var,
    rank_items,
    run_pipeline,
)


class TestComputeAverage:
    def test_normal_list(self):
        assert compute_average([1.0, 2.0, 3.0]) == pytest.approx(2.0)

    def test_empty_list(self):
        assert compute_average([]) == 0.0

    def test_single_element(self):
        assert compute_average([5.0]) == pytest.approx(5.0)

    def test_negatives(self):
        assert compute_average([-2.0, 2.0]) == pytest.approx(0.0)


class TestFilterPositives:
    def test_mixed(self):
        assert filter_positives([1, -1, 0, 2]) == [1, 2]

    def test_all_negative(self):
        assert filter_positives([-1, -2]) == []

    def test_empty(self):
        assert filter_positives([]) == []


class TestProcessWithDeadVar:
    def test_returns_sum(self):
        assert process_with_dead_var([1, 2, 3]) == 6


class TestClassifyValue:
    def test_negative(self):
        assert classify_value(-5.0) == "negative"

    def test_zero(self):
        assert classify_value(0.0) == "zero"

    def test_positive(self):
        assert classify_value(3.0) == "positive"


class TestRankItems:
    def test_ranking_order(self):
        result = rank_items([0.5, 1.0, 0.2])
        assert result[0][1] == pytest.approx(1.0)  # highest normed value first

    def test_empty(self):
        result = rank_items([])
        assert result == []


class TestParseCsv:
    def test_valid_csv(self):
        raw = "name,age\nAlice,30\nBob,25"
        result = parse_csv(raw)
        assert len(result) == 2
        assert result[0]["name"] == "Alice"

    def test_empty_string(self):
        assert parse_csv("") == []

    def test_whitespace_only(self):
        assert parse_csv("   ") == []

    def test_none_like_empty(self):
        assert parse_csv("") == []


class TestRunPipeline:
    def test_full_pipeline(self):
        records = [
            {"active": True, "score": "80", "name": "Alice"},
            {"active": True, "score": "40", "name": "Bob"},
            {"active": False, "score": "90", "name": "Carol"},
        ]
        result = run_pipeline(records)
        assert result["input_count"] == 3
        assert result["filtered_count"] == 2
        assert result["passed_count"] == 1

    def test_empty_records(self):
        result = run_pipeline([])
        assert result["input_count"] == 0


class TestGenerateReport:
    def test_report_format(self):
        data = {"input_count": 5, "filtered_count": 3, "passed_count": 2}
        report = generate_report(data)
        assert "5" in report
        assert "3" in report


class TestGhostUse:
    def test_flag_true_returns_zero(self):
        assert ghost_use_example(True) == 0

    def test_flag_false_returns_value(self):
        assert ghost_use_example(False) == 42
