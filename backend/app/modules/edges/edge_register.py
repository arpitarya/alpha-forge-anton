"""Pre-registration discipline — the rule that makes a backtest result trustworthy.

A hypothesis written *after* seeing the result is not a hypothesis, it is hindsight.
So `assert_pre_registered` is the gate every recorded result passes through: it refuses
(raises `PreRegistrationError`) when the edge's `pre_registered_at` is missing, or is
later than the moment the backtest ran. The spec — with its timestamp — must already
live in the elgar store before `discover` is called. Pure check, no I/O, no clock of
its own: the caller supplies `run_at`, so the rule is testable and deterministic.
"""

from __future__ import annotations

from datetime import datetime

from app.modules.edges.edge_schema import EdgeSpec


class PreRegistrationError(RuntimeError):
    """Raised when a result would be recorded for a hypothesis not pre-registered first."""


def assert_pre_registered(spec: EdgeSpec, run_at: datetime) -> None:
    if spec.pre_registered_at is None:
        raise PreRegistrationError(
            f"edge {spec.id!r} has no pre_registered_at — register the hypothesis first"
        )
    if spec.pre_registered_at > run_at:
        raise PreRegistrationError(
            f"edge {spec.id!r} pre_registered_at ({spec.pre_registered_at.isoformat()}) is after "
            f"the run ({run_at.isoformat()}) — a hypothesis written post-result is rejected"
        )
