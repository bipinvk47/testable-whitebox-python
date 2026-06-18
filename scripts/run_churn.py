"""pydriller code churn analysis — last 500 Python file changes."""
import json
import sys

try:
    from pydriller import Repository
except ImportError:
    print(json.dumps({"error": "pydriller not installed"}))
    sys.exit(0)

churn = []
try:
    for commit in Repository(".").traverse_commits():
        for mod in commit.modified_files:
            if mod.filename.endswith(".py"):
                churn.append({
                    "commit": commit.hash[:7],
                    "date": str(commit.committer_date),
                    "author": commit.author.name,
                    "file": mod.new_path,
                    "added": mod.added_lines,
                    "deleted": mod.deleted_lines,
                    "churn": mod.added_lines + mod.deleted_lines,
                    "complexity": mod.complexity,
                })
        if len(churn) > 500:
            break
except Exception as exc:
    churn = [{"error": str(exc)}]

print(json.dumps(churn, indent=2))
