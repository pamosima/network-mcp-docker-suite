# ClickHouse MCP Server

A FastMCP server that provides read-only access to ClickHouse for querying syslog and log data during network troubleshooting.

## Features

- **Syslog Queries**: Query syslog messages with flexible filters
- **Host Discovery**: List devices that have sent syslog messages
- **Severity Analysis**: Get message counts by severity level
- **Recent Errors**: Fetch recent error/critical messages

Raw SQL is not accepted. Tools use fixed query templates with ClickHouse HTTP bound parameters (`param_*`).

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `CLICKHOUSE_URL` | ClickHouse HTTP interface URL | `http://localhost:8123` |
| `CLICKHOUSE_USER` | Dedicated read-only username | `mcp_readonly` |
| `CLICKHOUSE_PASSWORD` | Password for that user | (empty) |
| `CLICKHOUSE_DATABASE` | Default database (must be a simple identifier) | `default` |
| `MCP_HOST` | Server bind address | `127.0.0.1` |
| `MCP_PORT` | Server port | `8008` |
| `MCP_API_TOKEN` | Bearer token; required when `MCP_HOST` is not loopback | (empty) |

The process refuses to start if `CLICKHOUSE_USER` is empty or `default`. Provision `mcp_readonly` from [`clickhouse/users.d/mcp-readonly.xml`](../clickhouse/users.d/mcp-readonly.xml): readonly profile, DDL disabled, `GRANT SELECT` on `default.syslog` only. Do not grant FILE, URL, S3, Remote, MySQL, PostgreSQL, JDBC, or ODBC table functions.

## Syslog Table Schema

The server expects the gnp-stack syslog table schema:

```sql
CREATE TABLE default.syslog (
    timestamp DateTime64(3),
    host String,
    facility String,
    severity String,
    program String,
    message String,
    raw String,
    received_at DateTime64(3)
) ENGINE = MergeTree()
ORDER BY (timestamp, host)
```

## Tools

### `query_syslog`
Query syslog messages with filters.

**Parameters:**
- `host` (string, optional): Filter by device hostname or IP (partial match)
- `since_minutes` (int, optional): Time window in minutes (default: 15)
- `severity_filter` (string, optional): Filter by severity (e.g., 'error', 'warning')
- `program_filter` (string, optional): Filter by program name
- `message_contains` (string, optional): Search text in message
- `limit` (int, optional): Max results (default: 100, max: 1000)

**Example:**
```
query_syslog(host="core-01", since_minutes=30, severity_filter="error")
```

### `get_syslog_hosts`
List hosts that have sent syslog messages.

**Parameters:**
- `since_minutes` (int, optional): Time window (default: 60)

### `get_severity_stats`
Get syslog message counts grouped by severity.

**Parameters:**
- `host` (string, optional): Filter by host
- `since_minutes` (int, optional): Time window (default: 60)

### `get_recent_errors`
Get recent error and critical syslog messages.

**Parameters:**
- `host` (string, optional): Filter by host
- `since_minutes` (int, optional): Time window (default: 30)
- `limit` (int, optional): Max results (default: 50)

## Security

- Dedicated `mcp_readonly` identity (not the default superuser)
- Allowlisted parameterized templates only; no `query_clickhouse` / raw SQL tool
- Bind defaults to loopback; non-loopback requires `Authorization: Bearer <MCP_API_TOKEN>`

## Usage with gnp-stack

When running alongside gnp-stack:
- Docker network: `CLICKHOUSE_URL=http://clickhouse:8123`
- External access: `CLICKHOUSE_URL=http://<clickhouse-host>:8123`

## Example Troubleshooting Queries

```python
# Recent errors from a specific device
query_syslog(host="core-01", severity_filter="error", since_minutes=60)

# All syslog from the last 5 minutes
query_syslog(since_minutes=5, limit=200)

# Search for specific message content
query_syslog(message_contains="interface down", since_minutes=30)

# Top talkers in the window: use get_syslog_hosts
get_syslog_hosts(since_minutes=60)
```
