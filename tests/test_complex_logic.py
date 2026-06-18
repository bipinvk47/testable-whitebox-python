"""
test_complex_logic.py
=====================
Targets:
  - All 22 paths through schedule_task (path coverage)
  - All 5 outputs of access_control (MC-DC – 4 boolean predicates)
  - Recursive flatten (mutation + boundary)
  - State machine transitions (sequence integrity)
  - Temperature boundaries (boundary failure identification)
"""
import pytest
from src.complex_logic import (
    access_control,
    categorise_temperature,
    flatten,
    schedule_task,
    transition_state,
)


# ── schedule_task – systematic path coverage ─────────────────────────────────
class TestScheduleTask:
    def test_batch_high_resources_low_load(self):
        r = schedule_task("BATCH", "HIGH", "USER", True, 4, 0, False, 50)
        assert r["status"] == "RUNNING"

    def test_batch_medium_critical_overloaded(self):
        # ESCALATED status + system_load > 90 → triggers OVERLOADED modifier
        r = schedule_task("BATCH", "MEDIUM", "USER", True, 4, 0, True, 95)
        assert r["status"] == "OVERLOADED"

    def test_batch_high_resources_high_load_max_retry(self):
        r = schedule_task("BATCH", "HIGH", "USER", True, 4, 5, False, 80)
        assert r["status"] == "FAILED"

    def test_batch_high_resources_low_load_with_retry(self):
        # RUNNING + retry_count > 0 → triggers RETRY_RUNNING modifier
        r = schedule_task("BATCH", "HIGH", "USER", True, 4, 1, False, 50)
        assert r["status"] == "RETRY_RUNNING"

    def test_batch_high_no_resource(self):
        r = schedule_task("BATCH", "HIGH", "USER", False, 4, 0, False, 50)
        assert r["status"] == "WAITING"

    def test_batch_medium_critical(self):
        r = schedule_task("BATCH", "MEDIUM", "USER", True, 4, 0, True, 50)
        assert r["status"] == "ESCALATED"

    def test_batch_medium_not_critical(self):
        r = schedule_task("BATCH", "MEDIUM", "USER", True, 4, 0, False, 50)
        assert r["status"] == "QUEUED"

    def test_batch_low_priority(self):
        r = schedule_task("BATCH", "LOW", "USER", True, 4, 0, False, 50)
        assert r["status"] == "DEFERRED"

    def test_realtime_no_resource_critical(self):
        r = schedule_task("REALTIME", "HIGH", "USER", False, 2, 0, True, 50)
        assert r["status"] == "EMERGENCY_QUEUE"

    def test_realtime_no_resource_not_critical(self):
        r = schedule_task("REALTIME", "HIGH", "USER", False, 2, 0, False, 50)
        assert r["status"] == "DROPPED"

    def test_realtime_admin(self):
        r = schedule_task("REALTIME", "HIGH", "ADMIN", True, 2, 0, False, 50)
        assert r["status"] == "RUNNING"

    def test_realtime_operator_low_load(self):
        r = schedule_task("REALTIME", "HIGH", "OPERATOR", True, 2, 0, False, 30)
        assert r["status"] == "RUNNING"

    def test_realtime_operator_high_load(self):
        r = schedule_task("REALTIME", "HIGH", "OPERATOR", True, 2, 0, False, 70)
        assert r["status"] == "THROTTLED"

    def test_realtime_unknown_role(self):
        r = schedule_task("REALTIME", "HIGH", "GUEST", True, 2, 0, False, 50)
        assert r["status"] == "UNAUTHORIZED"

    def test_scheduled_overdue(self):
        r = schedule_task("SCHEDULED", "LOW", "USER", True, -1, 0, False, 50)
        assert r["status"] == "OVERDUE"

    def test_scheduled_urgent(self):
        r = schedule_task("SCHEDULED", "LOW", "USER", True, 0.5, 0, False, 50)
        assert r["status"] == "URGENT"

    def test_scheduled_normal(self):
        r = schedule_task("SCHEDULED", "LOW", "USER", True, 12, 0, False, 50)
        assert r["status"] == "NORMAL"

    def test_scheduled_future(self):
        r = schedule_task("SCHEDULED", "LOW", "USER", True, 48, 0, False, 50)
        assert r["status"] == "FUTURE"

    def test_unknown_type(self):
        r = schedule_task("UNKNOWN", "HIGH", "USER", True, 4, 0, False, 50)
        assert r["status"] == "UNKNOWN_TYPE"


# ── access_control – MC-DC 4 boolean predicates ───────────────────────────────
class TestAccessControl:
    def test_full_access(self):
        assert access_control(True, True, True, True) == "FULL_ACCESS"

    def test_limited_no_ip(self):
        assert access_control(True, True, True, False) == "LIMITED_ACCESS"

    def test_read_only_no_role(self):
        assert access_control(True, False, True, False) == "READ_ONLY"

    def test_locked_inactive(self):
        assert access_control(True, False, False, False) == "LOCKED"

    def test_denied(self):
        assert access_control(False, False, False, False) == "DENIED"


# ── flatten – recursion + boundary ───────────────────────────────────────────
class TestFlatten:
    def test_empty(self):
        assert flatten([]) == []

    def test_flat(self):
        assert flatten([1, 2, 3]) == [1, 2, 3]

    def test_nested_list(self):
        assert flatten([[1, 2], [3, [4, 5]]]) == [1, 2, 3, 4, 5]

    def test_nested_tuple(self):
        assert flatten([(1, 2), 3]) == [1, 2, 3]

    def test_mixed_deep(self):
        assert flatten([1, [2, [3, [4]]]]) == [1, 2, 3, 4]

    def test_max_depth_exceeded(self):
        # 12 levels deep exceeds max_depth=10
        deep = [["leaf"]]
        for _ in range(11):
            deep = [deep]
        with pytest.raises(RecursionError):
            flatten(deep)


# ── state machine ─────────────────────────────────────────────────────────────
class TestTransitionState:
    def test_idle_to_running(self):
        assert transition_state("IDLE", "RUNNING") == "RUNNING"

    def test_running_to_completed(self):
        assert transition_state("RUNNING", "COMPLETED") == "COMPLETED"

    def test_running_to_failed(self):
        assert transition_state("RUNNING", "FAILED") == "FAILED"

    def test_paused_to_cancelled(self):
        assert transition_state("PAUSED", "CANCELLED") == "CANCELLED"

    def test_failed_to_idle(self):
        assert transition_state("FAILED", "IDLE") == "IDLE"

    def test_invalid_transition(self):
        with pytest.raises(ValueError, match="Invalid transition"):
            transition_state("COMPLETED", "RUNNING")

    def test_unknown_state(self):
        with pytest.raises(ValueError):
            transition_state("GHOST", "RUNNING")


# ── temperature categorisation – boundary identification ─────────────────────
class TestCategoriseTemperature:
    def test_below_absolute_zero(self):
        with pytest.raises(ValueError):
            categorise_temperature(-300)

    def test_freezing(self):
        assert categorise_temperature(-10) == "FREEZING"

    def test_melting_point(self):
        assert categorise_temperature(0) == "MELTING_POINT"

    def test_cold(self):
        assert categorise_temperature(10) == "COLD"

    def test_comfortable(self):
        assert categorise_temperature(25) == "COMFORTABLE"

    def test_hot(self):
        assert categorise_temperature(45) == "HOT"

    def test_extreme(self):
        assert categorise_temperature(60) == "EXTREME"
