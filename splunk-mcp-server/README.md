# Splunk MCP Proxy Server

A [FastMCP](https://gofastmcp.com) server that sits in front of Splunk’s **native MCP** endpoint. It speaks **streamable HTTP** on port `8006` and forwards JSON-RPC to Splunk using **HTTPS + Bearer** authentication, so any MCP client that supports HTTP transport (Cursor, LibreChat, custom apps) can use it.

## Overview

- **Inbound:** MCP over HTTP at `http://<host>:8006/mcp` (streamable HTTP).
- **Outbound:** JSON-RPC `2.0` to Splunk’s MCP URL (default `https://<SPLUNK_HOST>:<SPLUNK_PORT>/services/mcp`, or a full `SPLUNK_MCP_URL` e.g. via UI proxy).
- **Tools:** Loaded **dynamically at startup** from Splunk’s `tools/list` (not a fixed list in this repo). Tool names and parameters match whatever Splunk exposes (often `splunk_*` style).
- **Parameters:** Each tool is built from Splunk’s **`inputSchema`**. You can optionally **append that schema to the tool description** so clients see argument names and types (see `SPLUNK_MCP_APPEND_INPUT_SCHEMA`).

## Features

- Bearer token auth to Splunk; optional TLS verification for Splunk (`SPLUNK_VERIFY_SSL`).
- **Dynamic tool registration** from Splunk `tools/list` (with `SPLUNK_MCP_MAX_TOOLS` cap).
- **Optional** embedding of Splunk `inputSchema` in MCP tool descriptions.
- **`.env` support:** reads `.env` from the working directory, or set `DOTENV_PATH`. In Docker, mount the file to `/app/.env` if you want the file on disk (the suite’s `docker-compose` bind-mounts it; Compose `env_file` also injects variables without a file).

## Configuration

### Environment variables

| Variable | Description |
|----------|-------------|
| `SPLUNK_HOST` | Splunk hostname or IP. **Required** unless `SPLUNK_MCP_URL` is set. |
| `SPLUNK_PORT` | Splunk management port (default `8089`). Used with `SPLUNK_MCP_PATH` when building the URL. |
| `SPLUNK_MCP_PATH` | Path to the MCP endpoint (default `/services/mcp`). Use Splunk’s UI proxy form if needed, e.g. `/en-US/splunkd/__raw/services/mcp`. |
| `SPLUNK_MCP_URL` | **Optional** full base URL to the Splunk MCP endpoint; overrides host/port/path. |
| `SPLUNK_API_KEY` | **Required.** Splunk bearer token. |
| `SPLUNK_VERIFY_SSL` | `true` / `false` (default: verify off for dev/self-signed). |
| `MCP_HOST` | Bind address for this server (default `0.0.0.0`). |
| `MCP_PORT` | Port for this server (default `8006`). |
| `DOTENV_PATH` | Path to a dotenv file (default `.env` under the working directory). |
| `SPLUNK_MCP_DYNAMIC` | If `true` (default), load tools from Splunk at startup. |
| `SPLUNK_MCP_MAX_TOOLS` | Max tools to register (default `64`). |
| `SPLUNK_MCP_APPEND_INPUT_SCHEMA` | If `true` (default), append each tool’s `inputSchema` JSON to its description. |
| `SPLUNK_MCP_SCHEMA_DESC_MAX_CHARS` | Max size of embedded schema in descriptions (default `12000`). |

See the parent suite’s **`.env.example`** for a full example block.

### Run with Docker (from suite root)

The **network-mcp-docker-suite** `docker-compose.yml` service `splunk-mcp-server` uses `env_file: ./.env` and mounts `./.env` to `/app/.env` so the app can read the file and Compose can inject the same values.

```bash
cd /path/to/network-mcp-docker-suite
cp .env.example .env   # edit SPLUNK_* and token
docker compose up -d --build splunk-mcp-server
```

### Run locally (optional)

```bash
cd splunk-mcp-server
cp ../.env.example ../.env   # or create .env here
uv sync
uv run python splunk_mcp_server.py
```

## Tools

Splunk **defines** the tool list; the proxy does not hardcode it. At startup the proxy calls Splunk **`tools/list`**, then registers one MCP tool per entry, using each tool’s **`inputSchema`** for the arguments forwarded to Splunk’s **`tools/call`**. Always use parameter names from that schema (e.g. `row_limit` for search limits when that is what Splunk exposes).

### Example: typical tool names (Splunk MCP)

The exact set depends on your Splunk version and entitlement. A **representative** list (names as returned by many Splunk MCP deployments) looks like this:

| Tool (example) | Purpose (summary) |
|----------------|-------------------|
| `splunk_get_info` | Instance / build information |
| `splunk_get_indexes` | List indexes |
| `splunk_get_index_info` | Details for a specific index |
| `splunk_get_user_list` | List users |
| `splunk_get_user_info` | Current or specified user context |
| `splunk_run_query` | Run SPL; primary search entry point |
| `splunk_run_saved_search` | Run a saved search by identifier |
| `splunk_get_metadata` | Hosts, sources, sourcetypes, etc. |
| `splunk_get_kv_store_collections` | KV Store collection stats |
| `splunk_get_knowledge_objects` | Saved searches, alerts, and related knowledge |

To see **your** live list, use Splunk’s MCP `tools/list` (see [Testing](#testing)) or check the proxy logs after startup: it logs how many tools were registered.

## Testing

### Logs

```bash
docker logs splunk-mcp-server
```

### Splunk backend reachability

```bash
curl -k "https://splunk.example.com:8089/services/mcp" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}'
```

### MCP over HTTP (minimal)

Streamable HTTP may use sessions (`Mcp-Session-Id`). Simple one-off `curl` tests can return **404** if the session is unknown or expired; that is **normal** for the Python MCP streamable stack. Prefer testing through a real MCP client or watch logs for `POST .../services/mcp` **200** from the proxy to Splunk.

## Integration (Cursor and others)

**Cursor** `~/.cursor/mcp.json` (example):

```json
{
  "mcpServers": {
    "Splunk-MCP-Server": {
      "url": "http://localhost:8006/mcp"
    }
  }
}
```

Use the exact shape your Cursor version expects (e.g. `type: "streamable-http"` if required).

**LibreChat** (example):

```yaml
mcpServers:
  Splunk-MCP-Server:
    type: streamable-http
    url: http://splunk-mcp-server:8006/mcp
    timeout: 60000
```

Point `url` at the host that can reach the container (`localhost` from the host, service name on the same Docker network).

## Architecture

```text
MCP client (HTTP) → Splunk MCP proxy :8006/mcp → HTTPS + Bearer → Splunk .../services/mcp
                    └─ FastMCP + dynamic tools from Splunk tools/list
```

## Troubleshooting

| Symptom | What to check |
|--------|----------------|
| **401** to Splunk | `SPLUNK_API_KEY` and that the token is allowed to use Splunk’s MCP API. |
| **Connection errors** | Host/port, firewall, and `SPLUNK_MCP_URL` / `SPLUNK_MCP_PATH` for your deployment (UI proxy vs direct `8089`). |
| **SSL errors** | `SPLUNK_VERIFY_SSL=false` for lab/self-signed; or install proper trust on the image. |
| **`.env` warnings** | With Compose `env_file` only, there is no file in the image until you **mount** `./.env` to `/app/.env` (as in the suite compose) or set vars another way. |
| **`GET /.well-known/...` 404** | Clients probing OAuth resource metadata; this server does not implement those routes. Harmless. |
| **`POST /mcp` 404** | Often **unknown or expired** `Mcp-Session-Id` (session timed out or client reused an old id). Reconnect the client. |
| **Pydantic / validation errors on tools** | Use only parameters defined in Splunk’s `inputSchema` for that tool. |

## License

Part of **network-mcp-docker-suite**.

Author: Patrick Mosimann
