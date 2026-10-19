"""add movies table

Revision ID: 9a6455a854b5
Revises: 0001
Create Date: 2026-10-19 12:16:15.095531+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9a6455a854b5"
down_revision: str | Sequence[str] | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "movies",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=True),
    )
    op.create_index(op.f("ix_movies_id"), "movies", ["id"])

    op.execute(
        """
        create or replace function match_movies(
          query_embedding vector(1536),
          match_threshold float,
          match_count int
        )
        returns table (
          id bigint,
          content text,
          similarity float
        )
        language sql stable
        as $$
          select
            movies.id,
            movies.content,
            1 - (movies.embedding <=> query_embedding) as similarity
          from movies
          where 1 - (movies.embedding <=> query_embedding) > match_threshold
          order by similarity desc
          limit match_count;
        $$;
        """
    )


def downgrade() -> None:
    op.execute("drop function if exists match_movies(vector, float, int)")
    op.drop_index(op.f("ix_movies_id"), table_name="movies")
    op.drop_table("movies")
