"""Initial schema: listings and alerts tables

Revision ID: 0001
Revises:
Create Date: 2026-05-30

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE listings (
            id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            source        TEXT NOT NULL,
            source_url    TEXT UNIQUE NOT NULL,
            title         TEXT NOT NULL,
            body_type     TEXT,
            make          TEXT,
            model         TEXT,
            year          INTEGER,
            price_lkr     BIGINT,
            mileage_km    INTEGER,
            fuel_type     TEXT,
            transmission  TEXT,
            district      TEXT,
            description   TEXT,
            image_urls    TEXT[],
            content_hash  TEXT NOT NULL,
            scraped_at    TIMESTAMPTZ DEFAULT NOW(),
            updated_at    TIMESTAMPTZ DEFAULT NOW(),
            is_active     BOOLEAN DEFAULT TRUE
        )
    """)

    op.execute("CREATE INDEX idx_listings_body_type  ON listings(body_type)")
    op.execute("CREATE INDEX idx_listings_price      ON listings(price_lkr)")
    op.execute("CREATE INDEX idx_listings_district   ON listings(district)")
    op.execute("CREATE INDEX idx_listings_scraped_at ON listings(scraped_at DESC)")

    # Trigger keeps updated_at current for both ORM and raw SQL updates
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """)
    op.execute("""
        CREATE TRIGGER listings_updated_at
        BEFORE UPDATE ON listings
        FOR EACH ROW EXECUTE FUNCTION update_updated_at()
    """)

    op.execute("""
        CREATE TABLE alerts (
            id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email      TEXT NOT NULL,
            filters    JSONB NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS alerts")
    op.execute("DROP TRIGGER IF EXISTS listings_updated_at ON listings")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at")
    op.execute("DROP TABLE IF EXISTS listings")
