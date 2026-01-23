# Quickstart (Experimental Docker Stack)

**This Docker stack is intended for local experimentation, development, and exploration only.**  
It is **not** hardened, secured, or tuned for production use.

The goal is to provide a fast, reproducible environment for:
- Exploring schemas and data
- Prototyping ETL / ORM logic
- Testing materialized views, loaders, and queries
- Running notebooks against a local PostgreSQL instance

---

## What this stack provides

When started with the appropriate profile, this stack runs:

- **PostgreSQL** (`cava-database`)
  - Custom-built image (see `docker/postgres/Dockerfile`)
  - Persistent storage via Docker volumes
- **pgAdmin** (`pgadmin`)
  - Web UI for inspecting and querying PostgreSQL
- **JupyterLab** (`cava-jupyter-notebook`, optional)
  - Notebook environment wired to the same database

All services communicate on a dedicated Docker bridge network (`cava-network`).

---

## Prerequisites

You’ll need:

- Docker Desktop (or Docker Engine + Compose v2)
- `docker compose` available on your PATH
- A `.env` file in the `docker/` directory

---

## Environment configuration

Create a `.env` file alongside `docker-compose.yml`, for example:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=cava

HOST=localhost
HTTP_TYPE=http

PYTHON_BIND_MOUNT=/absolute/path/to/your/code_or_data
```

These credentials are not secure and are intentionally simple for local use.

### Starting the stack

From the `docker` directory

#### Database + pgAdmin only

```
docker compose --profile default up -d
```

#### Database + pgAdmin + Jupyter

```
docker compose --profile jupyter up -d
```
