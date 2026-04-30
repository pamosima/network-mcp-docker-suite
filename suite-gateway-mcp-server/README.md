# Suite MCP Gateway

Single **Model Context Protocol** server that aggregates tools from the other MCP servers in this repository (Meraki, NetBox, Catalyst Center, IOS XE, ThousandEyes, ISE, Splunk, Prometheus, ClickHouse, GitLab).

Use this when you want **one LibreChat or Cursor entry** instead of ten separate MCP URLs — the same pattern as a multi-server MCP client / bridge in enterprise reference architectures.

## Behavior

1. On startup, the gateway connects to each configured backend URL.
2. It runs MCP `initialize` (and best-effort `notifications/initialized`), then `tools/list`.
3. Each backend tool is registered as **`{alias}__{tool_name}`** (non-alphanumeric characters in the original name are normalized to `_`).
4. Tool calls are forwarded to the correct backend via MCP `tools/call`.

Backends that are down or misconfigured are **skipped** with a log line; the gateway still starts.

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_HOST` / `MCP_PORT` | Gateway bind address / port | `0.0.0.0` / `8010` |
| `SUITE_GATEWAY_USE_DEFAULT_BACKENDS` | Use built-in Docker Compose service URLs | `true` |
| `SUITE_GATEWAY_BACKENDS` | JSON list `[{"alias":"ise","url":"http://ise-mcp-server:8005/mcp"}, ...]` | unset → defaults |
| `SUITE_GATEWAY_VERIFY_HTTP` | TLS verification for backend `httpx` calls | `false` (internal HTTP) |
| `SUITE_GATEWAY_REQUEST_TIMEOUT` | Backend HTTP timeout (seconds) | `120` |
| `SUITE_GATEWAY_MAX_TOOLS_PER_BACKEND` | Cap tools loaded per backend | `96` |
| `SUITE_GATEWAY_MAX_TOOLS_TOTAL` | Cap total tools registered | `512` |

Enable the container with `ENABLE_SUITE_GATEWAY_MCP=true` in `.env` (see root `.env.example`).

## Docker Compose

- Service: `suite-gateway-mcp-server`
- Published host port: **8012** (maps to container `8010`; avoids clashes with other stacks on `8010`)
- Start with other servers, e.g. `./deploy.sh start all` (if the gateway is enabled in `.env`), or only the gateway: `./deploy.sh start suite-gateway`

**Important:** Start the backends you care about **before** or **with** the gateway so `tools/list` can succeed. The gateway does not start other containers for you.

## LibreChat

```yaml
mcpServers:
  Suite-MCP-Gateway:
    type: streamable-http
    url: http://suite-gateway-mcp-server:8010/mcp
    timeout: 120000
```

## Cursor (`~/.cursor/mcp.json`)

```json
"Suite-MCP-Gateway": {
  "transport": "http",
  "url": "http://localhost:8012/mcp",
  "timeout": 120000
}
```

Use the same `Accept` behavior your client expects for streamable HTTP; Cursor typically works with the gateway’s `streamable-http` transport on host port **8012** (or `suite-gateway-mcp-server:8010` inside Docker).

## Security notes

- This gateway **does not** add OIDC or OPA; it forwards to existing suite servers. Protect the published port at the network layer or put an authenticating reverse proxy in front for production.
- Tool descriptions include the backend URL and original tool name for traceability.

## License

Same as the parent repository (Cisco Sample Code License where applicable).
