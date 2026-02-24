# Prometheus MCP Server

A FastMCP server that provides read-only access to Prometheus for querying network metrics during troubleshooting.

## Features

- **Instant Queries**: Execute PromQL queries at a specific point in time
- **Range Queries**: Query metrics over a time range for trend analysis
- **Metric Discovery**: List available metrics and filter by pattern
- **Target Discovery**: List monitored devices/targets
- **Query Suggestions**: Get pre-built PromQL queries for common network troubleshooting scenarios

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `PROMETHEUS_URL` | Prometheus server URL | `http://localhost:9090` |
| `MCP_HOST` | Server bind address | `0.0.0.0` |
| `MCP_PORT` | Server port | `8007` |

## Tools

### `query_prometheus`
Execute an instant PromQL query.

**Parameters:**
- `query` (string, required): PromQL query string
- `time` (string, optional): Unix timestamp or RFC3339 for evaluation time

**Example:**
```
query_prometheus(query='up{job="snmp"}')
```

### `query_prometheus_range`
Execute a range PromQL query over time.

**Parameters:**
- `query` (string, required): PromQL query string
- `start` (string, optional): Start time (Unix or RFC3339)
- `end` (string, optional): End time (Unix or RFC3339)
- `step` (string, optional): Resolution step (default: "15s")

**Example:**
```
query_prometheus_range(query='rate(ifHCInOctets{instance="core-01"}[5m])', step="1m")
```

### `list_metric_names`
List available metric names in Prometheus.

**Parameters:**
- `filter_pattern` (string, optional): Regex to filter metric names

**Example:**
```
list_metric_names(filter_pattern="if.*")
```

### `get_targets`
Get list of monitored targets from Prometheus.

### `suggest_queries`
Get suggested PromQL queries for a specific device.

**Parameters:**
- `device` (string, required): Device hostname, IP, or instance label

## Security

- Read-only access only (no write or admin APIs)
- Queries containing dangerous keywords (delete, drop, etc.) are rejected
- No authentication secrets exposed in tool parameters

## Usage with gnp-stack

When running alongside gnp-stack:
- Docker network: `PROMETHEUS_URL=http://prometheus:9090`
- External access: `PROMETHEUS_URL=http://198.18.134.22:9090`

## Example Queries for Network Troubleshooting

```promql
# Check if device is being monitored
up{instance=~".*core-01.*"}

# Interface traffic rate (bytes/sec)
rate(ifHCInOctets{instance="198.18.170.200"}[5m])

# Interface errors in last hour
increase(ifInErrors{instance="core-01"}[1h])

# Packet discards
increase(ifInDiscards[1h]) > 0
```
