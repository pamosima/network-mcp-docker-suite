# NetOps MCP Gateway

Single **Model Context Protocol** server that aggregates tools from the other MCP servers in this repository (Meraki, NetBox, Catalyst Center, IOS XE, ThousandEyes, ISE, Splunk, Prometheus, ClickHouse, GitLab).

Use this when you want **one LibreChat or Cursor entry** instead of ten separate MCP URLs — the same pattern as a multi-server MCP client / bridge in enterprise reference architectures.

## Behavior

1. On startup, the gateway connects to each configured backend URL.
2. It runs MCP `initialize` (and best-effort `notifications/initialized`), then `tools/list` on every backend and builds an **in-memory catalog** (capped per backend by `SUITE_GATEWAY_MAX_TOOLS_PER_BACKEND`).
3. **Tool surface:** only **eight** tools are registered — `suite_list_backends`, `suite_search_tools`, `suite_call_tool`, and five playbook tools (`suite_flow_overview`, `suite_flow_troubleshoot`, `suite_flow_compact`, `suite_flow_backends`, `suite_flow_clients`) that return the same Markdown as the `netops://flows/*` MCP resources (so clients that only surface **tools** still get the playbooks). Use `suite_search_tools` then `suite_call_tool` with `backend`, `tool_name`, and `arguments`. This mirrors the *progressive disclosure* idea from Anthropic’s [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) (few definitions in context). It is **not** a code sandbox inside the gateway; full “code mode” also depends on your **client** (agent runs code that calls MCP).
4. Backend tool calls are forwarded over MCP `tools/call` to the correct server.

`suite_search_tools` **`detail_level`** (token budget vs richness):

| Value | Each match includes |
|--------|---------------------|
| `name` | `backend`, `tool_name` only |
| `summary` (default) | + `description` (first 500 chars) |
| `full` | + full cached description + `inputSchema` |

Legacy: `include_input_schema=true` still adds `inputSchema` even when `detail_level` is `name` or `summary`. Invalid `detail_level` falls back to `summary`.

Backends that are down or misconfigured are **skipped** with a log line; the gateway still starts.

## Playbooks (MCP resources)

The gateway exposes **Markdown playbooks** as MCP resources (same pattern as long-form “flows” in other stacks): fetch them when planning multi-step or cross-vendor work so the model does not rely only on short tool descriptions. The same Markdown is also available as **`suite_flow_*` tools** (see Behavior above) for clients that only list tools.

| URI | Purpose |
|-----|---------|
| `netops://flows/overview` | Architecture and when to use the gateway |
| `netops://flows/troubleshoot` | Suggested cross-backend troubleshooting order |
| `netops://flows/compact` | `suite_search_tools` / `suite_call_tool` and `detail_level` |
| `netops://flows/backends` | Default Docker aliases and backend URLs |
| `netops://flows/clients` | LibreChat and Cursor URL examples |

**Server instructions:** MCP `initialize` metadata includes a short instruction block that points at these URIs.

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_HOST` / `MCP_PORT` | Gateway bind address / port | `0.0.0.0` / `8010` |
| `SUITE_GATEWAY_USE_DEFAULT_BACKENDS` | Use built-in Docker Compose service URLs | `true` |
| `SUITE_GATEWAY_BACKENDS` | JSON list `[{"alias":"ise","url":"http://ise-mcp-server:8005/mcp"}, ...]` | unset → defaults |
| `SUITE_GATEWAY_VERIFY_HTTP` | TLS verification for backend `httpx` calls | `false` (internal HTTP) |
| `SUITE_GATEWAY_REQUEST_TIMEOUT` | Backend HTTP timeout (seconds) | `120` |
| `SUITE_GATEWAY_MAX_TOOLS_PER_BACKEND` | Cap tools loaded per backend | `96` |
| `SUITE_GATEWAY_NORMALIZE_TOOL_RESULTS` | Unwrap nested MCP `{ "content": [{ "type":"text", "text": "<json>" }] }` chains from backends so tool output is easier to parse | `true` |
| `SUITE_GATEWAY_NORMALIZE_MAX_DEPTH` | Maximum unwrap iterations (cap 32) | `12` |

Enable the container with `ENABLE_NETOPS_MCP_GATEWAY=true` in `.env` (see root `.env.example`).

## Docker Compose

- Service: `netops-mcp-gateway`
- Published host port: **8010** (maps to container `8010`)
- Start with other servers, e.g. `./deploy.sh start all` (if the gateway is enabled in `.env`), or only the gateway: `./deploy.sh start netops-gateway` (alias: `suite-gateway`)

**Important:** Start the backends you care about **before** or **with** the gateway so `tools/list` can succeed. The gateway does not start other containers for you.

## LibreChat

```yaml
mcpServers:
  NetOps-MCP-Gateway:
    type: streamable-http
    url: http://netops-mcp-gateway:8010/mcp
    timeout: 120000
```

## Cursor (`~/.cursor/mcp.json`)

```json
"NetOps-MCP-Gateway": {
  "transport": "streamable-http",
  "url": "http://localhost:8010/mcp",
  "timeout": 120000
}
```

Use the same `Accept` behavior your client expects for streamable HTTP; Cursor typically works with the gateway’s `streamable-http` transport on host port **8010** (or `netops-mcp-gateway:8010` inside Docker).

## Security notes

- This gateway **does not** add OIDC or OPA; it forwards to existing suite servers. Protect the published port at the network layer or put an authenticating reverse proxy in front for production.
- Tool descriptions include the backend URL and original tool name for traceability.

## License

Same as the parent repository (Cisco Sample Code License where applicable).
