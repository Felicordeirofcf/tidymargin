"""Shared infrastructure for the TidyMargin operations agents.

Principles (see docs/10_AUTOMATION_ARCHITECTURE.md):
* Agents run ON DEMAND (CLI). No daemon, no hidden background work.
* Least privilege: every agent declares the actions it may take. Critical
  actions (spend money, refund, send email, publish, change prices) are NEVER
  executed — they are written to reports/PENDING_APPROVALS.md for the owner.
* No invented data: when an input file is missing the agent says "no data".
* Logs are JSON lines without personal data (emails are hashed).
* Hard limits on runtime, rows read and network requests.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "analytics" / "data"
REPORTS = ROOT / "reports"
LOGS = ROOT / "agents" / "logs"

MAX_ROWS = 50_000
MAX_SECONDS = 120
CRITICAL_ACTIONS = {"spend_money", "refund", "send_email", "publish_content", "change_price",
                    "delete_data", "move_money", "create_account"}

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def today() -> dt.date:
    return dt.date.today()


def mask(text: str) -> str:
    """Replace email addresses with a short stable hash (for logs/reports)."""
    return EMAIL_RE.sub(lambda m: "user#" + hashlib.sha256(m.group(0).lower().encode()).hexdigest()[:8], str(text))


def read_csv(path: Path, limit: int = MAX_ROWS) -> list[dict] | None:
    """Return rows or None when the file does not exist (= no data, never invented)."""
    if not path.exists():
        return None
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = []
        for i, row in enumerate(csv.DictReader(f)):
            if i >= limit:
                raise RuntimeError(f"{path.name}: more than {limit} rows — refusing to continue")
            rows.append({(k or "").strip().lower(): (v or "").strip() for k, v in row.items()})
        return rows


def money(v) -> float:
    if v in (None, ""):
        return 0.0
    s = str(v).replace("$", "").replace(",", "").replace("USD", "").strip()
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    try:
        x = float(s)
    except ValueError:
        raise ValueError(f"not a money value: {v!r}")
    return -x if neg else x


def parse_date(v) -> dt.date | None:
    if not v:
        return None
    v = v.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%m/%d/%Y %H:%M", "%m/%d/%Y", "%b %d, %Y"):
        try:
            return dt.datetime.strptime(v, fmt).date()
        except ValueError:
            continue
    try:
        return dt.date.fromisoformat(v[:10])
    except ValueError:
        return None


@dataclass
class Result:
    agent: str
    summary: list[str] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)
    proposals: list[str] = field(default_factory=list)   # need owner approval
    metrics: dict = field(default_factory=dict)
    ok: bool = True

    def markdown(self) -> str:
        out = [f"# {self.agent} — {today().isoformat()}", ""]
        if self.summary:
            out += ["## Summary", *[f"- {s}" for s in self.summary], ""]
        if self.metrics:
            out += ["## Metrics", "| Metric | Value |", "|---|---|",
                    *[f"| {k} | {v} |" for k, v in self.metrics.items()], ""]
        if self.findings:
            out += ["## Findings", *[f"- {s}" for s in self.findings], ""]
        if self.proposals:
            out += ["## Proposals (need owner approval — nothing was executed)", *[f"- [ ] {s}" for s in self.proposals], ""]
        return mask("\n".join(out))


class Agent:
    name = "agent"
    allowed_actions: set[str] = {"read_local", "write_report"}

    def __init__(self, data_dir: Path = DATA, reports_dir: Path = REPORTS, logs_dir: Path = LOGS):
        self.data_dir, self.reports_dir, self.logs_dir = data_dir, reports_dir, logs_dir
        self._t0 = time.monotonic()
        assert not (self.allowed_actions & CRITICAL_ACTIONS), f"{self.name} declares a critical action"

    # -- guard rails ---------------------------------------------------------
    def require(self, action: str):
        if action in CRITICAL_ACTIONS:
            raise PermissionError(f"{self.name}: '{action}' is a critical action — propose it, never execute it")
        if action not in self.allowed_actions:
            raise PermissionError(f"{self.name}: action '{action}' not allowed")
        if time.monotonic() - self._t0 > MAX_SECONDS:
            raise TimeoutError(f"{self.name}: exceeded {MAX_SECONDS}s")

    def log(self, event: str, **kw):
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        rec = {"ts": dt.datetime.now().isoformat(timespec="seconds"), "agent": self.name, "event": event,
               **{k: mask(v) if isinstance(v, str) else v for k, v in kw.items()}}
        with open(self.logs_dir / f"{today().isoformat()}.jsonl", "a") as f:
            f.write(json.dumps(rec) + "\n")

    # -- run -----------------------------------------------------------------
    def run(self) -> Result:  # pragma: no cover - abstract
        raise NotImplementedError

    def execute(self, write=True) -> Result:
        self.log("start")
        try:
            res = self.run()
        except Exception as e:  # never crash the whole pipeline
            self.log("error", error=f"{type(e).__name__}: {e}")
            res = Result(self.name, ok=False, findings=[f"ERROR {type(e).__name__}: {e}"])
        if write:
            self.require("write_report")
            out = self.reports_dir / "agent_runs"
            out.mkdir(parents=True, exist_ok=True)
            (out / f"{today().isoformat()}-{self.name}.md").write_text(res.markdown())
            if res.proposals:
                self._append_approvals(res)
        self.log("end", ok=res.ok, findings=len(res.findings), proposals=len(res.proposals))
        return res

    def _append_approvals(self, res: Result):
        p = self.reports_dir / "PENDING_APPROVALS.md"
        head = "" if p.exists() else ("# Pending approvals\n\nAgents never execute these. The owner decides "
                                       "and acts manually, then ticks the box.\n\n")
        with open(p, "a") as f:
            f.write(head + f"\n## {today().isoformat()} · {res.agent}\n" + "".join(f"- [ ] {mask(x)}\n" for x in res.proposals))
