"""
Prometheus MCP Server
=====================
A FastMCP server for querying Prometheus metrics during network troubleshooting.
Read-only access to Prometheus API for metrics queries.

Environment Variables:
    PROMETHEUS_URL: Prometheus server URL (default: http://localhost:9090)
"""

import os
import re
from typing import Any, Dict, Optional

import httpx
from fastmcp import FastMCP

# Configuration from environment
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "8007"))

# Dangerous patterns to reject (security)
DANGEROUS_PATTERNS = re.compile(r'\b(delete|drop|truncate|insert|update|alter)\b', re.IGNORECASE)

# Initialize FastMCP server
mcp = FastMCP(
    name="Prometheus MCP Server",
    instructions="""Prometheus MCP Server for network metrics queries.
    
This server provides read-only access to Prometheus for querying network metrics
collected by gnp-stack (SNMP, interface counters, device health, etc.).

Available tools:
- query_prometheus: Execute instant PromQL queries
- query_prometheus_range: Execute range PromQL queries over time
- list_metric_names: List available metric names
- get_targets: List monitored targets/devices
- suggest_queries: Get suggested PromQL queries for a device

Example queries:
- Interface traffic: rate(ifHCInOctets{instance="198.18.170.200"}[5m])
- Interface errors: increase(ifInErrors{instance="core-01"}[1h])
- Device up status: up{job="snmp"}
"""
)


def _make_request(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Make a request to Prometheus API."""
    url = f"{PROMETHEUS_URL}/api/v1/{endpoint}"
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        return {"status": "error", "error": f"HTTP {e.response.status_code}: {e.response.text}"}
    except httpx.RequestError as e:
        return {"status": "error", "error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _validate_query(query: str) -> Optional[str]:
    """Validate PromQL query for dangerous patterns."""
    if DANGEROUS_PATTERNS.search(query):
        return "Query contains forbidden keywords (delete, drop, truncate, insert, update, alter)"
    return None


def _format_instant_result(data: Dict[str, Any]) -> str:
    """Format instant query result for readability."""
    if data.get("status") != "success":
        return f"Error: {data.get('error', 'Unknown error')}"
    
    result = data.get("data", {})
    result_type = result.get("resultType", "unknown")
    results = result.get("result", [])
    
    if not results:
        return "No data returned"
    
    lines = [f"Result type: {result_type}", f"Count: {len(results)}", ""]
    
    for r in results[:20]:  # Limit to 20 results
        metric = r.get("metric", {})
        value = r.get("value", [])
        
        labels = ", ".join(f'{k}="{v}"' for k, v in metric.items())
        if len(value) >= 2:
            timestamp, val = value[0], value[1]
            ts_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"{{{labels}}} => {val} @ {ts_str}")
        else:
            lines.append(f"{{{labels}}} => {value}")
    
    if len(results) > 20:
        lines.append(f"... and {len(results) - 20} more results")
    
    return "\n".join(lines)


def _format_range_result(data: Dict[str, Any]) -> str:
    """Format range query result for readability."""
    if data.get("status") != "success":
        return f"Error: {data.get('error', 'Unknown error')}"
    
    result = data.get("data", {})
    results = result.get("result", [])
    
    if not results:
        return "No data returned"
    
    lines = [f"Time series count: {len(results)}", ""]
    
    for r in results[:10]:  # Limit to 10 series
        metric = r.get("metric", {})
        values = r.get("values", [])
        
        labels = ", ".join(f'{k}="{v}"' for k, v in metric.items())
        lines.append(f"Series: {{{labels}}}")
        lines.append(f"  Points: {len(values)}")
        
        if values:
            first_ts = datetime.fromtimestamp(values[0][0]).strftime("%H:%M:%S")
            last_ts = datetime.fromtimestamp(values[-1][0]).strftime("%H:%M:%S")
            first_val, last_val = values[0][1], values[-1][1]
            lines.append(f"  Range: {first_ts} ({first_val}) -> {last_ts} ({last_val})")
        lines.append("")
    
    if len(results) > 10:
        lines.append(f"... and {len(results) - 10} more series")
    
    return "\n".join(lines)


@mcp.tool()
def query_prometheus(query: str, time: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute an instant PromQL query against Prometheus.
    
    Args:
        query: PromQL query string (e.g., 'up{job="snmp"}', 'rate(ifHCInOctets[5m])')
        time: Optional Unix timestamp or RFC3339 for the query evaluation time
    
    Returns:
        Query result with metrics data or error message
    """
    # Validate query
    error = _validate_query(query)
    if error:
        return {"success": False, "error": error}
    
    params = {"query": query}
    if time:
        params["time"] = time
    
    result = _make_request("query", params)
    
    return {
        "success": result.get("status") == "success",
        "raw": result,
        "formatted": _format_instant_result(result)
    }


@mcp.tool()
def query_prometheus_range(
    query: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    step: str = "15s"
) -> Dict[str, Any]:
    """
    Execute a range PromQL query against Prometheus.
    
    Args:
        query: PromQL query string
        start: Start time (Unix timestamp or RFC3339). Default: 1 hour ago
        end: End time (Unix timestamp or RFC3339). Default: now
        step: Query resolution step (e.g., '15s', '1m', '5m'). Default: 15s
    
    Returns:
        Query result with time series data or error message
    """
    # Validate query
    error = _validate_query(query)
    if error:
        return {"success": False, "error": error}
    
    # Default time range: last hour
    import time as time_module
    now = time_module.time()
    
    params = {
        "query": query,
        "start": start or str(int(now - 3600)),
        "end": end or str(int(now)),
        "step": step
    }
    
    result = _make_request("query_range", params)
    
    return {
        "success": result.get("status") == "success",
        "raw": result,
        "formatted": _format_range_result(result)
    }


@mcp.tool()
def list_metric_names(filter_pattern: Optional[str] = None) -> Dict[str, Any]:
    """
    List available metric names in Prometheus.
    
    Args:
        filter_pattern: Optional regex pattern to filter metric names (e.g., 'if.*' for interface metrics)
    
    Returns:
        List of metric names
    """
    result = _make_request("label/__name__/values", {})
    
    if result.get("status") != "success":
        return {"success": False, "error": result.get("error", "Failed to fetch metric names")}
    
    names = result.get("data", [])
    
    if filter_pattern:
        try:
            pattern = re.compile(filter_pattern, re.IGNORECASE)
            names = [n for n in names if pattern.search(n)]
        except re.error as e:
            return {"success": False, "error": f"Invalid regex pattern: {e}"}
    
    return {
        "success": True,
        "count": len(names),
        "metrics": names[:100],  # Limit to 100
        "truncated": len(names) > 100
    }


@mcp.tool()
def get_targets() -> Dict[str, Any]:
    """
    Get list of monitored targets from Prometheus.
    
    Returns:
        List of active and inactive targets with their labels
    """
    result = _make_request("targets", {})
    
    if result.get("status") != "success":
        return {"success": False, "error": result.get("error", "Failed to fetch targets")}
    
    data = result.get("data", {})
    active = data.get("activeTargets", [])
    dropped = data.get("droppedTargets", [])
    
    active_summary = []
    for t in active:
        labels = t.get("labels", {})
        active_summary.append({
            "instance": labels.get("instance", "unknown"),
            "job": labels.get("job", "unknown"),
            "health": t.get("health", "unknown"),
            "lastScrape": t.get("lastScrape", ""),
            "labels": labels
        })
    
    return {
        "success": True,
        "active_count": len(active),
        "dropped_count": len(dropped),
        "active_targets": active_summary
    }


@mcp.tool()
def suggest_queries(device: str) -> Dict[str, Any]:
    """
    Suggest useful PromQL queries for a specific device.
    
    Args:
        device: Device identifier (hostname, IP, or instance label)
    
    Returns:
        List of suggested PromQL queries for network troubleshooting
    """
    suggestions = [
        {
            "name": "Device Up Status",
            "query": f'up{{instance=~".*{device}.*"}}',
            "description": "Check if the device is being scraped successfully"
        },
        {
            "name": "Interface Traffic In (bytes/sec)",
            "query": f'rate(ifHCInOctets{{instance=~".*{device}.*"}}[5m])',
            "description": "Incoming traffic rate on all interfaces"
        },
        {
            "name": "Interface Traffic Out (bytes/sec)",
            "query": f'rate(ifHCOutOctets{{instance=~".*{device}.*"}}[5m])',
            "description": "Outgoing traffic rate on all interfaces"
        },
        {
            "name": "Interface Errors In",
            "query": f'increase(ifInErrors{{instance=~".*{device}.*"}}[1h])',
            "description": "Input errors in the last hour"
        },
        {
            "name": "Interface Errors Out",
            "query": f'increase(ifOutErrors{{instance=~".*{device}.*"}}[1h])',
            "description": "Output errors in the last hour"
        },
        {
            "name": "Interface Discards In",
            "query": f'increase(ifInDiscards{{instance=~".*{device}.*"}}[1h])',
            "description": "Input packet discards in the last hour"
        },
        {
            "name": "Interface Discards Out",
            "query": f'increase(ifOutDiscards{{instance=~".*{device}.*"}}[1h])',
            "description": "Output packet discards in the last hour"
        },
        {
            "name": "Interface Operational Status",
            "query": f'ifOperStatus{{instance=~".*{device}.*"}}',
            "description": "Operational status of interfaces (1=up, 2=down)"
        },
        {
            "name": "CPU Utilization",
            "query": f'cpmCPUTotal5minRev{{instance=~".*{device}.*"}}',
            "description": "CPU utilization (Cisco devices)"
        },
        {
            "name": "Memory Utilization",
            "query": f'ciscoMemoryPoolUsed{{instance=~".*{device}.*"}} / ciscoMemoryPoolFree{{instance=~".*{device}.*"}} * 100',
            "description": "Memory utilization percentage (Cisco devices)"
        }
    ]
    
    return {
        "success": True,
        "device": device,
        "suggestions": suggestions,
        "note": "Adjust metric names based on your SNMP MIBs and Prometheus configuration"
    }


if __name__ == "__main__":
    print(f"🚀 Starting Prometheus MCP Server")
    print(f"📊 Prometheus URL: {PROMETHEUS_URL}")
    print(f"🔌 Listening on: {MCP_HOST}:{MCP_PORT}")
    print(f"")
    print(f"📋 Available tools:")
    print(f"   - query_prometheus: Execute instant PromQL queries")
    print(f"   - query_prometheus_range: Execute range queries")
    print(f"   - list_metric_names: List available metrics")
    print(f"   - get_targets: List monitored targets")
    print(f"   - suggest_queries: Get suggested queries for a device")
    
    mcp.run(transport="streamable-http", host=MCP_HOST, port=MCP_PORT)
