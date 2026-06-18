"""
complex_logic.py
================
Triggers:
  - High Cyclomatic Complexity (CC > 20) → Execution Path Integrity (Crosshair/McCabe)
  - High Cognitive Complexity (radon) → Human Cognitive Load, Reviewer Fatigue Factor
  - Modularization Opportunity, Technical Debt Impact
  - Total Logical Combinatorial Coverage (Crosshair)
  - Defect Probability, Unit Test Complexity
  - QA Resource Allocation (pytest-testmon)
"""

# ── CC ≈ 22 | CogCC ≈ 28 – deliberately over-engineered scheduler ────────────
def schedule_task(  # noqa: PLR0912,PLR0915
    task_type,
    priority,
    user_role,
    resource_available,
    deadline_hours,
    retry_count,
    is_critical,
    system_load,
):
    """
    Intentionally high complexity to trigger CC > 20 threshold alerts.
    Modularization Opportunity: could be split into ≥ 5 helpers.
    Cognitive Complexity penalty: 4 levels of nesting.
    """
    result = {"status": "PENDING", "assigned_to": None, "eta_hours": None}

    if task_type == "BATCH":
        if priority == "HIGH":
            if resource_available:
                if system_load < 70:
                    result["status"] = "RUNNING"
                    result["assigned_to"] = "batch_worker_1"
                    result["eta_hours"] = 1
                else:
                    if retry_count < 3:
                        result["status"] = "QUEUED"
                        result["eta_hours"] = 2
                    else:
                        result["status"] = "FAILED"
            else:
                result["status"] = "WAITING"
                result["eta_hours"] = deadline_hours
        elif priority == "MEDIUM":
            if is_critical:
                result["status"] = "ESCALATED"
                result["assigned_to"] = "batch_worker_2"
            else:
                result["status"] = "QUEUED"
                result["eta_hours"] = deadline_hours * 2
        else:
            result["status"] = "DEFERRED"
    elif task_type == "REALTIME":
        if not resource_available:
            if is_critical:
                result["status"] = "EMERGENCY_QUEUE"
                result["eta_hours"] = 0.5
            else:
                result["status"] = "DROPPED"
        else:
            if user_role == "ADMIN":
                result["assigned_to"] = "rt_worker_admin"
                result["status"] = "RUNNING"
                result["eta_hours"] = 0.1
            elif user_role == "OPERATOR":
                if system_load < 50:
                    result["assigned_to"] = "rt_worker_op"
                    result["status"] = "RUNNING"
                    result["eta_hours"] = 0.2
                else:
                    result["status"] = "THROTTLED"
                    result["eta_hours"] = 1
            else:
                result["status"] = "UNAUTHORIZED"
    elif task_type == "SCHEDULED":
        if deadline_hours <= 0:
            result["status"] = "OVERDUE"
        elif deadline_hours < 1:
            result["status"] = "URGENT"
            result["eta_hours"] = 0.5
        elif deadline_hours < 24:
            result["status"] = "NORMAL"
            result["eta_hours"] = deadline_hours * 0.8
        else:
            result["status"] = "FUTURE"
            result["eta_hours"] = deadline_hours
    else:
        result["status"] = "UNKNOWN_TYPE"

    # Additional risk modifier (more CC)
    if result["status"] in ("RUNNING", "ESCALATED"):
        if retry_count > 0:
            result["status"] = "RETRY_RUNNING"
        if system_load > 90:
            result["status"] = "OVERLOADED"

    return result


# ── Recursive function – triggers Loop / Recursive Path Detection ─────────────
def flatten(nested, depth=0, max_depth=10):
    """
    Recursive flatten; triggers:
    - Loop Path Detection
    - Deep Logic Probing (Nested Condition Path Testing)
    - Boundary Mutant Analysis (mutation on depth < max_depth)
    """
    if depth > max_depth:
        raise RecursionError("Max depth exceeded")
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item, depth + 1, max_depth))
        elif isinstance(item, tuple):
            result.extend(flatten(list(item), depth + 1, max_depth))
        else:
            result.append(item)
    return result


# ── Multi-condition classifier – triggers MC-DC condition coverage ────────────
def access_control(is_authenticated, has_role, is_active, ip_whitelisted):
    """
    Four-condition compound predicate.
    pymcdc requires each of the 4 booleans to independently affect outcome.
    Triggers: Logical Sub-expression Validation, Access Control Verification.
    """
    if is_authenticated and has_role and is_active and ip_whitelisted:
        return "FULL_ACCESS"
    if is_authenticated and has_role and is_active:
        return "LIMITED_ACCESS"
    if is_authenticated and is_active:
        return "READ_ONLY"
    if is_authenticated:
        return "LOCKED"
    return "DENIED"


# ── State machine – triggers Coverage Gap Analysis, Sequence Integrity ────────
_VALID_TRANSITIONS = {
    "IDLE": ["RUNNING", "CANCELLED"],
    "RUNNING": ["PAUSED", "COMPLETED", "FAILED"],
    "PAUSED": ["RUNNING", "CANCELLED"],
    "COMPLETED": [],
    "FAILED": ["IDLE"],
    "CANCELLED": [],
}


def transition_state(current, event):
    """
    State machine transition.
    Triggers: Control Flow Validation, Sequence Integrity Mapping.
    """
    allowed = _VALID_TRANSITIONS.get(current, [])
    if event not in allowed:
        raise ValueError(f"Invalid transition: {current} -> {event}")
    return event


# ── Boundary-heavy function – triggers Boundary Failure Identification ────────
def categorise_temperature(temp_celsius):
    """
    Multiple boundary comparisons → Branch Misdirection Discovery.
    """
    if temp_celsius < -273.15:
        raise ValueError("Temperature below absolute zero")
    if temp_celsius < 0:
        return "FREEZING"
    if temp_celsius == 0:
        return "MELTING_POINT"
    if temp_celsius < 20:
        return "COLD"
    if temp_celsius < 37:
        return "COMFORTABLE"
    if temp_celsius < 50:
        return "HOT"
    return "EXTREME"
