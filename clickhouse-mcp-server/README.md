# ClickHouse MCP Server

A FastMCP server that provides read-only access to ClickHouse for querying syslog and log data during network troubleshooting.

## Features

- **Syslog Queries**: Query syslog messages with flexible filters
- **Host Discovery**: List devices that have sent syslog messages
- **Severity Analysis**: Get message counts by severity level
- **Custom Queries**: Execute custom SELECT queries (with security validation)

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `CLICKHOUSE_URL` | ClickHouse HTTP interface URL | `http://localhost:8123` |
| `CLICKHOUSE_USER` | ClickHouse username (if required) | (empty) |
| `CLICKHOUSE_PASSWORD` | ClickHouse password (if required) | (empty) |
| `CLICKHOUSE_DATABASE` | Default database | `default` |
| `MCP_HOST` | Server bind address | `0.0.0.0` |
| `MCP_PORT` | Server port | `8008` |

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
Query syslog messages with filters (recommended for most use cases).

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

### `query_clickhouse`
Execute a custom SELECT query against ClickHouse.

**Parameters:**
- `sql` (string, required): SQL SELECT query

**Security:**
- Only SELECT queries are allowed
- INSERT, UPDATE, DELETE, DROP, and DDL statements are rejected

**Example:**
```
query_clickhouse(sql="SELECT host, count() FROM syslog GROUP BY host ORDER BY count() DESC LIMIT 10")
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

- Read-only access only (SELECT statements only)
- Dangerous SQL keywords are blocked (INSERT, UPDATE, DELETE, DROP, etc.)
- Input values are escaped to prevent SQL injection
- No authentication secrets exposed in tool parameters

## Usage with gnp-stack

When running alongside gnp-stack:
- Docker network: `CLICKHOUSE_URL=http://clickhouse:8123`
- External access: `CLICKHOUSE_URL=http://198.18.134.22:8123`

## Example Troubleshooting Queries

```python
# Recent errors from a specific device
query_syslog(host="core-01", severity_filter="error", since_minutes=60)

# All syslog from the last 5 minutes
query_syslog(since_minutes=5, limit=200)

# Search for specific message content
query_syslog(message_contains="interface down", since_minutes=30)

# Custom query for top talkers
query_clickhouse(sql="""
    SELECT host, count() as msgs
    FROM syslog
    WHERE timestamp >= now() - INTERVAL 1 HOUR
    GROUP BY host
    ORDER BY msgs DESC
    LIMIT 20
""")
```
