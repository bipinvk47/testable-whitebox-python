"""Beniget def-use chain analysis for all src/ Python files."""
import json
import sys
from pathlib import Path

try:
    from beniget import DefUseChains
    import gast as ast
except ImportError:
    print(json.dumps({"error": "beniget or gast not installed"}))
    sys.exit(0)

results = {}
for pyfile in Path("src").glob("*.py"):
    src_text = pyfile.read_text(encoding="utf-8")
    try:
        module = ast.parse(src_text)
        duc = DefUseChains()
        duc.visit(module)
        results[str(pyfile)] = {
            "chains_count": len(duc.chains),
            "file": str(pyfile),
        }
    except Exception as exc:
        results[str(pyfile)] = {"error": str(exc)}

print(json.dumps(results, indent=2))
