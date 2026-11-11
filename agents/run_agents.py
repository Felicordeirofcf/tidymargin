"""Run the TidyMargin agents on demand.

    python3 agents/run_agents.py            # CEO: runs QA, sales, finance, support, content
    python3 agents/run_agents.py sales_analyst
    python3 agents/run_agents.py dashboard  # rebuild analytics/dashboard.html
    python3 agents/run_agents.py list

Reports: reports/agent_runs/<date>-<agent>.md · approvals: reports/PENDING_APPROVALS.md
Logs: agents/logs/<date>.jsonl (no personal data).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dashboard import build_dashboard  # noqa: E402
from team import ALL  # noqa: E402


def main(argv):
    target = argv[0] if argv else "ceo"
    if target == "list":
        print("\n".join(ALL))
        return 0
    if target == "dashboard":
        print("dashboard:", build_dashboard())
        return 0
    if target not in ALL:
        print(f"unknown agent '{target}'. Options: {', '.join(ALL)}, dashboard, list")
        return 2
    res = ALL[target]().execute()
    print(res.markdown())
    if target == "ceo":
        print("dashboard:", build_dashboard())
    return 0 if res.ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
