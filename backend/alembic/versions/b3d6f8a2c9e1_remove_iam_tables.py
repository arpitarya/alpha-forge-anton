"""Remove IAM tables — IAM is now owned by Wagner.

Revision ID: b3d6f8a2c9e1
Revises: a3c9f2e1b4d7
Create Date: 2026-05-25
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "b3d6f8a2c9e1"
down_revision = "a3c9f2e1b4d7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_iam_audit_log_created_at", table_name="iam_audit_log")
    op.drop_index("ix_iam_audit_log_user_id", table_name="iam_audit_log")
    op.drop_table("iam_audit_log")

    op.drop_index("ix_iam_api_keys_key_hash", table_name="iam_api_keys")
    op.drop_index("ix_iam_api_keys_user_id", table_name="iam_api_keys")
    op.drop_table("iam_api_keys")

    op.drop_index("ix_iam_refresh_tokens_token_hash", table_name="iam_refresh_tokens")
    op.drop_index("ix_iam_refresh_tokens_user_id", table_name="iam_refresh_tokens")
    op.drop_table("iam_refresh_tokens")

    op.drop_index("ix_iam_users_email", table_name="iam_users")
    op.drop_table("iam_users")


def downgrade() -> None:
    op.create_table(
        "iam_users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.Text(), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_iam_users_email", "iam_users", ["email"], unique=True)

    op.create_table(
        "iam_refresh_tokens",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("token_hash", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["iam_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_iam_refresh_tokens_user_id", "iam_refresh_tokens", ["user_id"])
    op.create_index("ix_iam_refresh_tokens_token_hash", "iam_refresh_tokens", ["token_hash"])

    op.create_table(
        "iam_api_keys",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("label", sa.String(100), nullable=False),
        sa.Column("key_hash", sa.Text(), nullable=False),
        sa.Column("key_prefix", sa.String(8), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["iam_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key_hash"),
    )
    op.create_index("ix_iam_api_keys_user_id", "iam_api_keys", ["user_id"])
    op.create_index("ix_iam_api_keys_key_hash", "iam_api_keys", ["key_hash"])

    op.create_table(
        "iam_audit_log",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("event", sa.String(50), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("detail", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["iam_users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_iam_audit_log_user_id", "iam_audit_log", ["user_id"])
    op.create_index("ix_iam_audit_log_created_at", "iam_audit_log", ["created_at"])
