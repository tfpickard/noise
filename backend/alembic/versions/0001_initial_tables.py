from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql as pg

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.create_table(
        "users",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(length=255), unique=True),
        sa.Column("username", sa.String(length=50), unique=True),
        sa.Column("display_name", sa.String(length=100)),
        sa.Column("avatar_url", sa.String(length=500)),
        sa.Column("password_hash", sa.String(length=255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "patterns",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("exhibit_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=200)),
        sa.Column("description", sa.Text()),
        sa.Column("parameters", sa.JSON(), nullable=False),
        sa.Column("seed", sa.BigInteger()),
        sa.Column("thumbnail_url", sa.String(length=500)),
        sa.Column("is_public", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("likes_count", sa.Integer(), server_default=sa.text("0")),
        sa.Column("views_count", sa.Integer(), server_default=sa.text("0")),
        sa.Column("forked_from", pg.UUID(as_uuid=True), sa.ForeignKey("patterns.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_patterns_exhibit", "patterns", ["exhibit_type"])
    op.create_index("idx_patterns_user", "patterns", ["user_id"])
    op.create_index("idx_patterns_public", "patterns", ["is_public"], postgresql_where=sa.text("is_public = true"))

    op.create_table(
        "pattern_embeddings",
        sa.Column("pattern_id", pg.UUID(as_uuid=True), sa.ForeignKey("patterns.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("embedding", Vector(dim=128)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_embeddings_vector", "pattern_embeddings", ["embedding"], postgresql_using="hnsw", postgresql_ops={"embedding": "vector_cosine_ops"})

    op.create_table(
        "pattern_likes",
        sa.Column("pattern_id", pg.UUID(as_uuid=True), sa.ForeignKey("patterns.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "collections",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("is_featured", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "collection_patterns",
        sa.Column("collection_id", pg.UUID(as_uuid=True), sa.ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("pattern_id", pg.UUID(as_uuid=True), sa.ForeignKey("patterns.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("position", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "analytics_events",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("pattern_id", pg.UUID(as_uuid=True), sa.ForeignKey("patterns.id")),
        sa.Column("user_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("session_id", sa.String(length=100)),
        sa.Column("metadata", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_analytics_type_time", "analytics_events", ["event_type", "created_at"], postgresql_using="btree")

    op.create_table(
        "sessions",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.String(length=200)),
        sa.Column("host_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("state", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "exports",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("pattern_id", pg.UUID(as_uuid=True), sa.ForeignKey("patterns.id")),
        sa.Column("status", sa.String(length=50), server_default=sa.text("'queued'")),
        sa.Column("url", sa.String(length=500)),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("exports")
    op.drop_table("sessions")
    op.drop_index("idx_analytics_type_time", table_name="analytics_events")
    op.drop_table("analytics_events")
    op.drop_table("collection_patterns")
    op.drop_table("collections")
    op.drop_table("pattern_likes")
    op.drop_index("idx_embeddings_vector", table_name="pattern_embeddings")
    op.drop_table("pattern_embeddings")
    op.drop_index("idx_patterns_public", table_name="patterns")
    op.drop_index("idx_patterns_user", table_name="patterns")
    op.drop_index("idx_patterns_exhibit", table_name="patterns")
    op.drop_table("patterns")
    op.drop_table("users")
