"""dashboard ticker + watchlist items

Revision ID: 1d8f1014a7d4
Revises: 640eee61bc50
Create Date: 2026-05-16
"""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "1d8f1014a7d4"
down_revision: str | None = "640eee61bc50"
branch_labels = None
depends_on = None


def _table(name: str, *, sublabel: bool) -> None:
    cols = [
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("symbol", sa.String(length=64), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("price", sa.String(length=32), nullable=False, server_default="—"),
        sa.Column("change", sa.String(length=16), nullable=False, server_default="—"),
        sa.Column("tone", sa.String(length=4), nullable=False, server_default="up"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    ]
    if sublabel:
        cols.insert(
            2, sa.Column("sublabel", sa.String(length=64), nullable=False, server_default="")
        )
    op.create_table(name, *cols)
    op.create_index(op.f(f"ix_{name}_sort_order"), name, ["sort_order"], unique=False)


def upgrade() -> None:
    _table("dashboard_ticker_items", sublabel=False)
    _table("dashboard_watchlist_items", sublabel=True)


def downgrade() -> None:
    op.drop_index(
        op.f("ix_dashboard_watchlist_items_sort_order"), table_name="dashboard_watchlist_items"
    )
    op.drop_table("dashboard_watchlist_items")
    op.drop_index(
        op.f("ix_dashboard_ticker_items_sort_order"), table_name="dashboard_ticker_items"
    )
    op.drop_table("dashboard_ticker_items")
