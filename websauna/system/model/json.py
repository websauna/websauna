"""JSON column compatibiltiy layer."""
import os

if os.environ.get("OLD_POSTGRESQL"):
    # PostgreSQL 9.4+
    from sqlalchemy.dialects.postgresql import JSON as JSONB
else:
    # PostgreSQL 9.3
    from sqlalchemy.dialects.postgresql import JSONB as JSONB

__all__ = ["JSONB"]