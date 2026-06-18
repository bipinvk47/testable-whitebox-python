"""
duplicated_code.py
==================
Triggers (Code Duplication tools: jscpd / copydetect):
  - Multi-Point Failure Probability  (Defect Propagation Risk Detection)
  - Redundancy Localization          (Refactoring Identification)
  - Structural Cleanliness Score     (Code Quality Assessment)
  - Test Suite Streamlining          (Test Maintenance Reduction)
  - Abstraction Potential            (Refactoring Opportunity Detection)
  - Regression Focus Mapping         (Risk-Based Testing Prioritization)
  - Synchronization Verification     (Maintainability Testing)

The blocks below are intentionally near-identical to produce a high
clone-detection score.  In production code these would be extracted
into a shared helper; leaving them duplicated here is the *point*.
"""


# ═══ CLONE GROUP A – order processing (3 near-identical clones) ═══════════════

def process_retail_order(order_id, items, discount, tax_rate):
    """Process a retail order – original."""
    subtotal = 0.0
    for item in items:
        price = item.get("price", 0.0)
        qty = item.get("quantity", 1)
        subtotal += price * qty
    after_discount = subtotal * (1 - discount)
    total = after_discount * (1 + tax_rate)
    return {
        "order_id": order_id,
        "subtotal": round(subtotal, 2),
        "discount_applied": round(subtotal - after_discount, 2),
        "tax": round(total - after_discount, 2),
        "total": round(total, 2),
    }


def process_wholesale_order(order_id, items, discount, tax_rate):
    """Process a wholesale order – clone of retail (jscpd will flag this)."""
    subtotal = 0.0
    for item in items:
        price = item.get("price", 0.0)
        qty = item.get("quantity", 1)
        subtotal += price * qty
    after_discount = subtotal * (1 - discount)
    total = after_discount * (1 + tax_rate)
    return {
        "order_id": order_id,
        "subtotal": round(subtotal, 2),
        "discount_applied": round(subtotal - after_discount, 2),
        "tax": round(total - after_discount, 2),
        "total": round(total, 2),
    }


def process_digital_order(order_id, items, discount, tax_rate):
    """Process a digital order – second clone (copydetect similarity > 80%)."""
    subtotal = 0.0
    for item in items:
        price = item.get("price", 0.0)
        qty = item.get("quantity", 1)
        subtotal += price * qty
    after_discount = subtotal * (1 - discount)
    total = after_discount * (1 + tax_rate)
    return {
        "order_id": order_id,
        "subtotal": round(subtotal, 2),
        "discount_applied": round(subtotal - after_discount, 2),
        "tax": round(total - after_discount, 2),
        "total": round(total, 2),
    }


# ═══ CLONE GROUP B – validation pattern (2 clones) ════════════════════════════

def validate_user_input(data: dict) -> list[str]:
    """Validate user form data – original."""
    errors = []
    if not data.get("name") or len(data["name"].strip()) < 2:
        errors.append("Name is required and must be at least 2 characters")
    if not data.get("email") or "@" not in data["email"]:
        errors.append("A valid email address is required")
    if not data.get("phone") or len(data["phone"]) < 10:
        errors.append("Phone number must be at least 10 digits")
    if not data.get("dob"):
        errors.append("Date of birth is required")
    return errors


def validate_admin_input(data: dict) -> list[str]:
    """Validate admin form data – clone of validate_user_input."""
    errors = []
    if not data.get("name") or len(data["name"].strip()) < 2:
        errors.append("Name is required and must be at least 2 characters")
    if not data.get("email") or "@" not in data["email"]:
        errors.append("A valid email address is required")
    if not data.get("phone") or len(data["phone"]) < 10:
        errors.append("Phone number must be at least 10 digits")
    if not data.get("dob"):
        errors.append("Date of birth is required")
    return errors


# ═══ CLONE GROUP C – reporting (2 clones) ════════════════════════════════════

def format_sales_report(records: list[dict]) -> str:
    """Format a sales report – original."""
    lines = ["=== SALES REPORT ==="]
    total = 0.0
    for rec in records:
        amount = rec.get("amount", 0.0)
        total += amount
        lines.append(f"  {rec.get('date', 'N/A')} | {rec.get('product', 'N/A')} | ${amount:.2f}")
    lines.append(f"Total: ${total:.2f}")
    lines.append("=" * 20)
    return "\n".join(lines)


def format_returns_report(records: list[dict]) -> str:
    """Format a returns report – near-clone of sales report."""
    lines = ["=== RETURNS REPORT ==="]
    total = 0.0
    for rec in records:
        amount = rec.get("amount", 0.0)
        total += amount
        lines.append(f"  {rec.get('date', 'N/A')} | {rec.get('product', 'N/A')} | ${amount:.2f}")
    lines.append(f"Total: ${total:.2f}")
    lines.append("=" * 20)
    return "\n".join(lines)
