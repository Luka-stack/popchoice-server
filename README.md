# PopChoice

FastAPI + async SQLAlchemy + Alembic + PostgreSQL/pgvector, managed with [uv](https://docs.astral.sh/uv/).

## Development (Docker, hot reload)

```bash
cp .env.example .env   # set POSTGRES_PASSWORD
docker compose up --build
```

`docker compose` automatically merges `docker-compose.override.yml`, which builds the `dev` image,
bind-mounts the project into the container and runs uvicorn with `--reload`. Edits under
`app/` restart the server within ~1 s. Rebuild only when dependencies change.

`migrate` runs `alembic upgrade head` once, then `api` starts on `:8000`.
Health: `/api/v1/health/live`, `/api/v1/health/ready`. Docs at http://localhost:8000/docs.

## Production

Skip the override file so the slim, non-root `runtime` image is used:

```bash
docker compose -f docker-compose.yml up -d --build
```

## Local development without Docker

```bash
docker compose up -d db
uv sync
uv run fastapi dev app/main.py
```

## Migrations

Add models under `app/models/` and import them in `app/models/__init__.py`, then:

```bash
uv run alembic revision --autogenerate -m "add movies"
uv run alembic upgrade head
```

## Quality checks

```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy app tests && uv run pytest
```
