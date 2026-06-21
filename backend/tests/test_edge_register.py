"""Pre-registration discipline — a hypothesis written after the result is rejected.

The rule that makes a backtest result trustworthy: `pre_registered_at` must exist and
must predate the run. These tests pin all three branches — missing timestamp, a
timestamp *after* the run (hindsight), and a valid one — plus that `discover` refuses
to compute OR journal anything for an unregistered edge.

    uv run pytest tests/test_edge_register.py -v
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.modules.edges.edge_data import Bars
from app.modules.edges.edge_discover import discover
from app.modules.edges.edge_register import PreRegistrationError, assert_pre_registered
from app.modules.edges.edge_schema import EdgeSpec

_RUN = datetime(2026, 6, 21, 12, 0, tzinfo=UTC)


def _spec(pre: datetime | None) -> EdgeSpec:
    return EdgeSpec(
        id="e", hypothesis="h", universe=["X"], signal="momentum", pre_registered_at=pre
    )


def test_missing_timestamp_is_rejected():
    with pytest.raises(PreRegistrationError, match="no pre_registered_at"):
        assert_pre_registered(_spec(None), _RUN)


def test_timestamp_after_the_run_is_rejected():
    after = _RUN + timedelta(seconds=1)
    with pytest.raises(PreRegistrationError, match="after"):
        assert_pre_registered(_spec(after), _RUN)


def test_timestamp_before_the_run_is_accepted():
    before = _RUN - timedelta(days=1)
    assert_pre_registered(_spec(before), _RUN)  # does not raise


@pytest.mark.asyncio
async def test_discover_refuses_an_unregistered_edge_before_any_compute():
    journaled: list[object] = []

    class _Spy:
        async def bars(self, symbol: str, years: int) -> Bars:
            journaled.append("computed")  # must never run for an unregistered edge
            return Bars(dates=["2024-01-01"], close=[100.0])

    with pytest.raises(PreRegistrationError):
        await discover(_spec(None), provider=_Spy(), run_at=_RUN, journal=True)
    assert journaled == []  # refused before touching data or the journal
