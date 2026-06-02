"""initial schema: cities, prayer_times, islamic_events

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-02

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name_sq", sa.String(length=128), nullable=False),
        sa.Column("name_en", sa.String(length=128), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column(
            "region",
            sa.Enum("kosova", "lugina", name="region", native_enum=False, length=16),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_cities_slug", "cities", ["slug"], unique=True)

    op.create_table(
        "prayer_times",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("city_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("imsak", sa.Time(), nullable=False),
        sa.Column("sunrise", sa.Time(), nullable=False),
        sa.Column("dhuhr", sa.Time(), nullable=False),
        sa.Column("asr", sa.Time(), nullable=False),
        sa.Column("maghrib", sa.Time(), nullable=False),
        sa.Column("isha", sa.Time(), nullable=False),
        sa.ForeignKeyConstraint(["city_id"], ["cities.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("city_id", "date", name="uq_prayer_times_city_date"),
    )
    op.create_index("ix_prayer_times_city_id", "prayer_times", ["city_id"])
    op.create_index("ix_prayer_times_date", "prayer_times", ["date"])

    op.create_table(
        "islamic_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("hijri_label", sa.String(length=64), nullable=False),
        sa.Column("name_sq", sa.String(length=128), nullable=False),
        sa.Column("name_en", sa.String(length=128), nullable=False),
        sa.Column(
            "type",
            sa.Enum("day", "night", "holiday", name="event_type", native_enum=False, length=16),
            nullable=False,
        ),
        sa.Column("description_sq", sa.Text(), nullable=True),
        sa.Column("description_en", sa.Text(), nullable=True),
    )
    op.create_index("ix_islamic_events_date", "islamic_events", ["date"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_islamic_events_date", table_name="islamic_events")
    op.drop_table("islamic_events")
    op.drop_index("ix_prayer_times_date", table_name="prayer_times")
    op.drop_index("ix_prayer_times_city_id", table_name="prayer_times")
    op.drop_table("prayer_times")
    op.drop_index("ix_cities_slug", table_name="cities")
    op.drop_table("cities")
