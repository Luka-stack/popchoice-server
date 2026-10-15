"""Import every model here so Alembic autogenerate can discover it via Base.metadata."""

from app.db.base import Base

__all__ = ["Base"]
