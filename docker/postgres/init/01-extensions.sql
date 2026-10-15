-- Runs once, on first initialisation of the data volume.
-- Alembic migration 0001 also ensures this, so the DB works either way.
CREATE EXTENSION IF NOT EXISTS vector;
