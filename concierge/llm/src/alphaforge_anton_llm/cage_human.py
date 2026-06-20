"""Human-baseline backfill — file one Tier-1 ``tool="human"`` receipt per task.

Lights up ``cage human`` / ``cage trend`` (the agent-vs-human counterfactual,
design §4.1/§5b.4). cage's task record (``tasks.jsonl``, written by
``cage hook-session-end``) is the source of tasks; for each one we let cage's
own resolver + ``[human.tasks.*]`` policy do minutes→USD and the confidence
ladder — Anton supplies only the task id and its type. No minutes are invented:
a typeless task falls to cage's global default (honestly low-confidence).

Off the request path and **fail-open** like ``cage_meter``: cage absent, or any
error, is a silent no-op. ``record_human`` is itself idempotent on ``(task,
call)``, so re-running this backfill never double-records (criterion 6). One
receipt per task — never per LLM call. Run at SessionEnd *after*
``cage hook-session-end`` (so the task rows exist), or via ``just cage-human``.
"""

from __future__ import annotations

import logging

from alphaforge_anton_llm.cage_meter import _ROOT

logger = logging.getLogger(__name__)


def backfill(root=_ROOT) -> int:
    """Record a human alternative for each task lacking one. Returns #recorded."""
    try:
        import cage
        from cage import tasks
    except ImportError:
        return 0
    try:
        recorded = 0
        for task_id, row in tasks.read(root).items():
            if cage.record_human(task=task_id, task_type=row.get("type", ""), root=root):
                recorded += 1  # "" ⇒ already present (idempotent) ⇒ not counted
        return recorded
    except Exception as exc:  # pragma: no cover — backfill is best-effort
        logger.debug("cage human backfill skipped: %s", exc)
        return 0


def main() -> int:
    n = backfill()
    if n:
        logger.info("cage: recorded %d human alternative(s)", n)
    return 0  # always succeed — a hook must never break the session


if __name__ == "__main__":
    raise SystemExit(main())
