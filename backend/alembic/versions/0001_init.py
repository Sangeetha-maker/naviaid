"""Initial migration – create all NaviAid tables with pgvector."""
from alembic import op
import sqlalchemy as sa

try:
    from pgvector.sqlalchemy import Vector
    _has_pgvector = True
except ImportError:
    Vector = None
    _has_pgvector = False

try:
    from sqlalchemy.dialects.postgresql import UUID, JSONB
except ImportError:
    UUID = sa.String
    JSONB = sa.JSON


revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table("users",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("role", sa.String(20), nullable=False, server_default="user"),
        sa.Column("google_id", sa.String(255), nullable=True, unique=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
    )

    op.create_table("user_profiles",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("district", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=False, server_default="Tamil Nadu"),
        sa.Column("pincode", sa.String(10), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lon", sa.Float(), nullable=True),
        sa.Column("education_level", sa.String(50), nullable=True),
        sa.Column("stream", sa.String(100), nullable=True),
        sa.Column("institution", sa.String(255), nullable=True),
        sa.Column("annual_income", sa.Integer(), nullable=True),
        sa.Column("caste_category", sa.String(50), nullable=True),
        sa.Column("is_differently_abled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("skills", JSONB(), nullable=False, server_default="[]"),
        sa.Column("interests", JSONB(), nullable=False, server_default="[]"),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.Column("draft_step", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("onboarding_complete", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
    )

    op.create_table("opportunities",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("title_ta", sa.String(500), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("description_ta", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("subcategory", sa.String(100), nullable=True),
        sa.Column("source", sa.String(255), nullable=True),
        sa.Column("source_url", sa.String(1000), nullable=True),
        sa.Column("apply_url", sa.String(1000), nullable=True),
        sa.Column("eligibility", JSONB(), nullable=False, server_default="{}"),
        sa.Column("documents_required", JSONB(), nullable=False, server_default="[]"),
        sa.Column("benefits", sa.Text(), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=True),
        sa.Column("deadline", sa.DateTime(), nullable=True),
        sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("locations", JSONB(), nullable=False, server_default="[]"),
        sa.Column("is_pan_india", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("trust_score", sa.Float(), nullable=False, server_default="0.8"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
    )

    op.create_table("applications",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("opportunity_id", UUID(as_uuid=False), sa.ForeignKey("opportunities.id", ondelete="CASCADE")),
        sa.Column("status", sa.String(30), nullable=False, server_default="saved"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("applied_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
    )

    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_opp_category", "opportunities", ["category"])
    op.create_index("ix_opp_active", "opportunities", ["is_active"])


def downgrade() -> None:
    op.drop_table("applications")
    op.drop_table("opportunities")
    op.drop_table("user_profiles")
    op.drop_table("users")
