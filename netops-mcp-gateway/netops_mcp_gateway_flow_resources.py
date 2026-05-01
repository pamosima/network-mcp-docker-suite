"""
Markdown playbooks exposed as MCP resources (netops://flows/...).

Mirrors the netops-stack pattern: long-form guidance the client can fetch on demand
without bloating every tools/list response.
"""

from __future__ import annotations

# Shown in MCP initialize metadata; keep actionable and point to resources.
SERVER_INSTRUCTIONS = """\
You are connected to the NetOps MCP Gateway: one MCP server that aggregates tools from multiple backends (Meraki, NetBox, Catalyst Center, IOS XE, ThousandEyes, ISE, Splunk, Prometheus, ClickHouse, GitLab).

**Tools:** only eight gateway tools are registered — `suite_list_backends`, `suite_search_tools`, `suite_call_tool`, plus five playbook tools (`suite_flow_overview`, `suite_flow_troubleshoot`, `suite_flow_compact`, `suite_flow_backends`, `suite_flow_clients`) whose Markdown matches the `netops://flows/...` MCP resources. Use `suite_search_tools` with `detail_level` (`name`, `summary`, or `full`) to find backend tools, then `suite_call_tool` with `backend`, `tool_name`, and `arguments`.

**Playbooks** (same Markdown via tools above, or via MCP `resources/read` on these URIs when the client supports resources):
- `netops://flows/overview` — architecture and when to use the gateway
- `netops://flows/troubleshoot` — cross-backend troubleshooting order
- `netops://flows/compact` — `suite_search_tools` / `suite_call_tool` and `detail_level` (token budget)
- `netops://flows/backends` — default Docker aliases and ports
- `netops://flows/clients` — LibreChat / Cursor wiring

Treat every tool as high-privilege network/infrastructure access: confirm intent for destructive or wide-impact actions; prefer read-only tools first; respect least privilege and change windows.
"""


def get_overview_flow() -> str:
    return """# NetOps MCP Gateway — overview

## What this server is

A **single MCP HTTP endpoint** that proxies to other MCP servers in the suite. On startup it runs `initialize` and `tools/list` against each configured backend, builds an **in-memory catalog** from each backend’s tools, and registers exactly eight gateway tools: `suite_list_backends`, `suite_search_tools`, `suite_call_tool`, and five `suite_flow_*` playbooks (same bodies as `netops://flows/*` resources).

Backends that are unreachable are skipped; the gateway still starts.

## When to use the gateway vs a direct backend URL

| Situation | Prefer |
|-----------|--------|
| One client URL, many vendors | Gateway |
| Minimal tool definitions in context (large suite) | Gateway (progressive disclosure) |
| Debugging one broken server only | That backend’s URL directly |

## Principles

1. Pick the backend that owns the data (Meraki for cloud dashboard objects, ISE for session/policy, Splunk for indexed logs, Prometheus for metrics, etc.).
2. **Search** before **call** (`suite_search_tools` then `suite_call_tool`) so arguments match the real `inputSchema`.
3. Chain reads before writes; for changes, summarize impact and get explicit confirmation when the user did not ask for a mutation.
"""


def get_troubleshoot_flow() -> str:
    return """# Cross-backend troubleshooting (NetOps MCP Gateway)

Use this as a **default order** when the user’s problem spans vendors or layers. Adjust to the symptom.

## 1. Scope and symptom

- Clarify: user/site/network/device/application, time window, and whether the issue is **reachability**, **performance**, **auth**, or **policy**.
- Use `suite_search_tools` with `query` keywords (`ping`, `route`, `session`, `log`, `metric`, etc.) and `detail_level` at least `summary` before calling tools.

## 2. Path / overlay (common first checks)

- **Meraki** (`meraki`): org/network/device status, uplinks, VPN, wireless health as exposed by available tools.
- **ThousandEyes** (`thousandeyes`): cloud or agent tests toward the affected dependency, if configured.

## 3. Campus / WAN device state

- **Catalyst Center** (`catc`): inventory, topology, assurance or health APIs surfaced by the server.
- **IOS XE** (`ios_xe`): live CLI-style diagnostics on specific devices (respect read vs write tools).

## 4. Identity and access

- **ISE** (`ise`): session, authorization, profiling — when failure looks like **802.1X**, **TACACS**, or **policy** mismatch.

## 5. Observability

- **Splunk** (`splunk`): correlate timestamps across systems; start narrow (index/sourcetype/host) then widen.
- **Prometheus** (`prometheus`): golden signals, scrape/up, alert labels — for **metric**-driven incidents.

## 6. Source of truth for design data

- **NetBox** (`netbox`): prefixes, VLANs, circuits, IPs — when documentation vs reality is in question.

## 7. Change correlation

- **GitLab** (`gitlab`): MRs, pipelines, release timing — when the incident follows a deploy or automation change.

## 8. Analytics / telemetry warehouse (if in use)

- **ClickHouse** (`clickhouse`): high-volume or long-range analytics per tools available on that server.

## Closure

Summarize evidence with **which backend** each fact came from. If data was missing, say what tool or scope would be needed next.
"""


def get_compact_flow() -> str:
    return """# Progressive disclosure — gateway tool surface

The gateway always registers **eight** tools:

**Control (3)** — discovery and invocation:

1. **`suite_list_backends`** — aliases and base URLs (and errors if a backend failed discovery).
2. **`suite_search_tools`** — search the cached catalog: `query`, optional `backend`, `limit`, `detail_level`, optional `include_input_schema`.
3. **`suite_call_tool`** — invoke one backend tool: `backend`, `tool_name`, `arguments` (object).

**Playbooks (5)** — long Markdown; same content as MCP resources `netops://flows/overview`, `netops://flows/troubleshoot`, `netops://flows/compact`, `netops://flows/backends`, `netops://flows/clients` (tools: `suite_flow_overview`, `suite_flow_troubleshoot`, `suite_flow_compact`, `suite_flow_backends`, `suite_flow_clients`). Use whichever shape your client lists (tools vs resources).

## detail_level

| Value | Use when |
|-------|----------|
| `name` | You only need tool names to disambiguate. |
| `summary` | Default; short description snippet. |
| `full` | You need the full description and schema text. |

`include_input_schema=true` adds `inputSchema` even for `name` or `summary` (legacy compatibility).

## Workflow

1. Optional: call a **`suite_flow_*`** playbook tool (or read the matching `netops://flows/...` resource) when you need multi-step or cross-vendor guidance.
2. `suite_list_backends` if you are unsure which alias to filter.
3. `suite_search_tools` with a tight `query`; increase `limit` or switch `detail_level` to `full` if the catalog is ambiguous.
4. Build `arguments` keys to match the schema from step 3.
5. `suite_call_tool` once per backend tool invocation.

Invalid `detail_level` values fall back to `summary`.
"""


def get_backends_flow() -> str:
    return """# Default backend aliases (Docker Compose)

When `SUITE_GATEWAY_USE_DEFAULT_BACKENDS=true` and `SUITE_GATEWAY_BACKENDS` is unset, the gateway uses in-container hostnames (published host port for the gateway is typically **8010** → container **8010**).

| Alias | Default URL |
|-------|-------------|
| meraki | http://meraki-mcp-servers:8000/mcp |
| netbox | http://netbox-mcp-server:8001/mcp |
| catc | http://catc-mcp-server:8002/mcp |
| ios_xe | http://ios-xe-mcp-server:8003/mcp |
| thousandeyes | http://thousandeyes-mcp-server:8004/mcp |
| ise | http://ise-mcp-server:8005/mcp |
| splunk | http://splunk-mcp-server:8006/mcp |
| prometheus | http://prometheus-mcp-server:8007/mcp |
| clickhouse | http://clickhouse-mcp-server:8008/mcp |
| gitlab | http://gitlab-mcp-server:8009/mcp |

Override with `SUITE_GATEWAY_BACKENDS` JSON when running outside this compose file or when using different hostnames/ports.
"""


def get_clients_flow() -> str:
    return """# Client configuration (LibreChat / Cursor)

## LibreChat

```yaml
mcpServers:
  NetOps-MCP-Gateway:
    type: streamable-http
    url: http://netops-mcp-gateway:8010/mcp
    timeout: 120000
```

Adjust host/port if the gateway is published differently on the host.

## Cursor (`~/.cursor/mcp.json`)

```json
"NetOps-MCP-Gateway": {
  "transport": "http",
  "url": "http://localhost:8010/mcp",
  "timeout": 120000
}
```

Use **streamable HTTP** / the URL your client expects; from the host machine the mapped port is typically **8010**.

## Resources in clients

If the client supports MCP resources, fetch `netops://flows/overview` (and siblings) for playbooks without expanding every tool definition in the system prompt.
"""
