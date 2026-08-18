# Ecom MCP Server

FastAPI e-commerce backend that also exposes an MCP server, so an AI agent can browse products, manage a cart, and place orders through the same auth/session layer as the web app.

- **API** — auth (session + OAuth), products, cart, orders. Redis for sessions/locks, MongoDB for data.
- **MCP server** — mounted at `/mcp` on the same FastAPI app, sharing auth. Tools live in `app/modules/mcp/tools`.
- **`web/`** — customer-facing frontend (TanStack Router), served at `/app`, built into `web/dist`.
- **`ui/`** — MCP App UI: interactive UI rendered by MCP tool calls (via `@modelcontextprotocol/ext-apps`). Built to `ui/dist` and served from there by `app/modules/mcp/resources.py`; `pnpm watch` for local dev only.
- **`packages/ui-kit/`** — shared React components between `web/` and `ui/`.

## Setup

```bash
uv sync
cp .env.example .env
docker-compose up -d   # redis + mongodb
```

## Run

```bash
uv run start
```

Serves on `0.0.0.0:8000`. API under `/`, frontend under `/app`, MCP under `/mcp`.

### Frontend / dev panel

```bash
cd web && pnpm install && pnpm dev
cd ui  && pnpm install && pnpm watch
```
