"""add users table and user_id to prediction_logs

Revision ID: 0002_users_auth
Revises: 0001_create_prediction_logs
Create Date: 2026-04-04 21:10:00
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_users_auth"
down_revision = "0001_create_prediction_logs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.add_column("prediction_logs", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_prediction_logs_user_id_users",
        "prediction_logs",
        "users",
        ["user_id"],
        ["id"],
    )

    op.alter_column(
        "prediction_logs",
        "user_id",
        existing_type=sa.Integer(),
        nullable=False,
    )


def downgrade() -> None:
    op.drop_constraint("fk_prediction_logs_user_id_users", "prediction_logs", type_="foreignkey")
    op.drop_column("prediction_logs", "user_id")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
