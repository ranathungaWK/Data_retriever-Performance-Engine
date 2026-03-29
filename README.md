# Data Retriever

FastAPI service that loads **applications and test rounds** from PostgreSQL and retrieves **shifted and smoothed metrics** from [VictoriaMetrics](https://victoriametrics.com/) for a chosen test run or manual time range. Intended as a backend for a UI that explores performance test data.

## Features

- **Metrics retrieval** — Single endpoint that coordinates multiple VictoriaMetrics queries and returns calibrated metric series.
- **Dropdown data** — Lists applications and completed test rounds per application from the database.
- **PostgreSQL** — Async SQLAlchemy (`asyncpg`) for reads against your existing schema (`Application`, `Script`, `TestRun`, etc.).

## Requirements

- Python **3.11+**
- [uv](https://docs.astral.sh/uv/) (recommended) or another way to install dependencies from `pyproject.toml`
- Optional: **Docker** and Docker Compose for a reproducible Postgres + API stack (works the same on macOS, Windows, and Linux)

## Configuration

Create a `.env` file in the project root (same folder as `docker-compose.yml`). The app loads it automatically.

| Variable | Description |
|----------|-------------|
| `VICTORIA_URL` | Base URL of VictoriaMetrics (must start with `http://` or `https://`). |
| `VICTORIA_TIMEOUT_SECONDS` | HTTP timeout for VictoriaMetrics calls (default `30`). |
| `GRAFANA_URL` | Grafana base URL (validated like other HTTP URLs). |
| `POSTGRES_USER` | Database user; used by Docker Compose for the bundled Postgres service. |
| `POSTGRES_PASSWORD` | Database password; same value must appear in `DATABASE_URL` when connecting from the host. |
| `POSTGRES_DB` | Database name. |
| `DATABASE_URL` | Async SQLAlchemy URL, e.g. `postgresql+asyncpg://USER:PASSWORD@HOST:5432/DBNAME`. |

### Database URL: host vs Docker

- **Running the API on your machine** (e.g. `uvicorn`): set the host to **`localhost`** (or `127.0.0.1`) so you connect to Postgres on the published port `5432`.
- **Running the API with Docker Compose**: Compose overrides `DATABASE_URL` for the `api` service so the host is the **`postgres`** service name on the Docker network. You do not need to change `.env` for that case.

## Local development (without Docker for the API)

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Ensure PostgreSQL is reachable at the host/port in `DATABASE_URL` (for example, start only the database with Compose: `docker compose up -d postgres`).

3. Run the API:

   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive OpenAPI UI.

## Docker Compose (Postgres + API)

From the project root:

```bash
docker compose up --build
```

- **API**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Postgres**: `localhost:5432` (credentials from `POSTGRES_*` in `.env`). Data is stored in the `postgres_data` volume.

To run **only** PostgreSQL (API still runs locally with `uvicorn`):

```bash
docker compose up -d postgres
```

## API overview

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/` | Health-style message. |
| `GET` | `/api/v1/applications/` | List applications (dropdown). |
| `GET` | `/api/v1/applications/{app_id}/rounds` | List completed test rounds for an application. |
| `POST` | `/api/v1/metrics/retrieval` | Main metrics analysis for a test round or manual range. |

Request/response shapes are defined in `app/schemas/request.py` and visible under `/docs`.

## Project layout

- `app/main.py` — FastAPI app and routers.
- `app/api/v1/routes/` — HTTP endpoints.
- `app/domain/` — Domain logic and SQLAlchemy models.
- `app/db/` — Session and base metadata.
- `app/infrastructure/victoria_client.py` — VictoriaMetrics client.

## License

Add your license here.
