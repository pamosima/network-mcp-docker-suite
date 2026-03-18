"""
ClickHouse MCP Server
=====================
A FastMCP server for querying syslog and other data in ClickHouse.
Read-only access for network troubleshooting.

Environment Variables:
    CLICKHOUSE_URL: ClickHouse HTTP interface URL (default: http://localhost:8123)
    CLICKHOUSE_USER: ClickHouse username (optional)
    CLICKHOUSE_PASSWORD: ClickHouse password (optional)
    CLICKHOUSE_DATABASE: Default database (default: default)
"""

import os
import re
from typing import Any, Dict, Optional, List

import httpx
from fastmcp import FastMCP

# Configuration from environment
CLICKHOUSE_URL = os.getenv("CLICKHOUSE_URL", "http://localhost:8123")
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")
CLICKHOUSE_DATABASE = os.getenv("CLICKHOUSE_DATABASE", "default")
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "8008"))

# SQL validation patterns
FORBIDDEN_KEYWORDS = re.compile(
    r'\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|GRANT|REVOKE|ATTACH|DETACH|RENAME|OPTIMIZE|KILL)\b',
    re.IGNORECASE
)

# Allowed tables for query_clickhouse (security allowlist)
ALLOWED_TABLES = {"syslog", "default.syslog"}

# Initialize FastMCP server
mcp = FastMCP(
    name="ClickHouse MCP Server",
    instructions="""ClickHouse MCP Server for syslog and log queries.
    
This server provides read-only access to ClickHouse for querying syslog data
collected by gnp-stack from network devices.

Available tools:
- query_syslog: Query syslog messages with filters (recommended)
- query_clickhouse: Execute custom SELECT queries (advanced)
- get_syslog_hosts: List hosts that have sent syslog messages
- get_severity_stats: Get syslog message counts by severity

Syslog table schema (default.syslog):
- timestamp: DateTime64(3) - Message timestamp
- host: String - Source device hostname/IP
- facility: String - Syslog facility
- severity: String - Syslog severity level
- program: String - Program/process name
- message: String - Log message content
- raw: String - Original raw syslog message
- received_at: DateTime64(3) - When message was received
"""
)


def _execute_query(sql: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute a query against ClickHouse HTTP interface."""
    try:
        headers = {"Content-Type": "text/plain"}
        query_params = {"default_format": "JSONEachRow"}
        
        if CLICKHOUSE_USER:
            query_params["user"] = CLICKHOUSE_USER
        if CLICKHOUSE_PASSWORD:
            query_params["password"] = CLICKHOUSE_PASSWORD
        if CLICKHOUSE_DATABASE:
            query_params["database"] = CLICKHOUSE_DATABASE
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                CLICKHOUSE_URL,
                params=query_params,
                content=sql,
                headers=headers
            )
            response.raise_for_status()
            
            # Parse JSONEachRow format
            lines = response.text.strip().split("\n")
            rows = []
            for line in lines:
                if line:
                    import json
                    rows.append(json.loads(line))
            
            return {"success": True, "rows": rows, "count": len(rows)}
            
    except httpx.HTTPStatusError as e:
        return {"success": False, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
    except httpx.RequestError as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _validate_select_query(sql: str) -> Optional[str]:
    """Validate that a query is a safe SELECT statement."""
    # Check for forbidden keywords
    if FORBIDDEN_KEYWORDS.search(sql):
        return "Query contains forbidden SQL keywords. Only SELECT queries are allowed."
    
    # Must start with SELECT (after stripping whitespace)
    if not sql.strip().upper().startswith("SELECT"):
        return "Query must be a SELECT statement"
    
    # Check for multiple statements (basic check)
    if ";" in sql.strip()[:-1]:  # Allow trailing semicolon
        return "Multiple SQL statements are not allowed"
    
    return None


def _format_syslog_rows(rows: List[Dict]) -> str:
    """Format syslog rows as readable text."""
    if not rows:
        return "No syslog messages found"
    
    lines = [f"Found {len(rows)} syslog messages:\n"]
    
    for row in rows:
        ts = row.get("timestamp", "")
        host = row.get("host", "unknown")
        severity = row.get("severity", "")
        program = row.get("program", "")
        message = row.get("message", "")
        
        # Truncate long messages
        if len(message) > 200:
            message = message[:200] + "..."
        
        lines.append(f"[{ts}] {host} {severity} {program}: {message}")
    
    return "\n".join(lines)


@mcp.tool()
def query_syslog(
    host: Optional[str] = None,
    since_minutes: int = 15,
    severity_filter: Optional[str] = None,
    program_filter: Optional[str] = None,
    message_contains: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Query syslog messages from ClickHouse with filters.
    
    Args:
        host: Filter by device hostname or IP (partial match supported)
        since_minutes: Time window in minutes (default: 15)
        severity_filter: Filter by severity (e.g., 'error', 'warning', 'critical')
        program_filter: Filter by program name (partial match)
        message_contains: Search for text in message content
        limit: Maximum number of results (default: 100, max: 1000)
    
    Returns:
        Syslog messages matching the filters
    """
    # Sanitize limit
    limit = min(max(1, limit), 1000)
    since_minutes = max(1, since_minutes)
    
    # Build WHERE clauses with parameterized values
    conditions = [f"timestamp >= now() - INTERVAL {since_minutes} MINUTE"]
    
    if host:
        # Escape single quotes in host
        safe_host = host.replace("'", "\\'")
        conditions.append(f"host ILIKE '%{safe_host}%'")
    
    if severity_filter:
        safe_severity = severity_filter.replace("'", "\\'")
        conditions.append(f"lower(severity) = lower('{safe_severity}')")
    
    if program_filter:
        safe_program = program_filter.replace("'", "\\'")
        conditions.append(f"program ILIKE '%{safe_program}%'")
    
    if message_contains:
        safe_message = message_contains.replace("'", "\\'")
        conditions.append(f"message ILIKE '%{safe_message}%'")
    
    where_clause = " AND ".join(conditions)
    
    sql = f"""
        SELECT 
            timestamp,
            host,
            facility,
            severity,
            program,
            message
        FROM {CLICKHOUSE_DATABASE}.syslog
        WHERE {where_clause}
        ORDER BY timestamp DESC
        LIMIT {limit}
    """
    
    result = _execute_query(sql)
    
    if not result["success"]:
        return result
    
    return {
        "success": True,
        "count": result["count"],
        "filters": {
            "host": host,
            "since_minutes": since_minutes,
            "severity": severity_filter,
            "program": program_filter,
            "message_contains": message_contains
        },
        "rows": result["rows"],
        "formatted": _format_syslog_rows(result["rows"])
    }


@mcp.tool()
def query_clickhouse(sql: str) -> Dict[str, Any]:
    """
    Execute a custom SELECT query against ClickHouse.
    
    Args:
        sql: SQL SELECT query (only SELECT statements allowed)
    
    Returns:
        Query results as rows
    
    Security:
        - Only SELECT queries are allowed
        - INSERT, UPDATE, DELETE, DROP, and DDL statements are rejected
    """
    # Validate the query
    error = _validate_select_query(sql)
    if error:
        return {"success": False, "error": error}
    
    result = _execute_query(sql)
    
    if not result["success"]:
        return result
    
    return {
        "success": True,
        "count": result["count"],
        "rows": result["rows"][:500],  # Limit rows returned
        "truncated": result["count"] > 500
    }


@mcp.tool()
def get_syslog_hosts(since_minutes: int = 60) -> Dict[str, Any]:
    """
    List hosts that have sent syslog messages.
    
    Args:
        since_minutes: Time window to search (default: 60)
    
    Returns:
        List of hosts with message counts
    """
    since_minutes = max(1, since_minutes)
    
    sql = f"""
        SELECT 
            host,
            count() as message_count,
            max(timestamp) as last_seen
        FROM {CLICKHOUSE_DATABASE}.syslog
        WHERE timestamp >= now() - INTERVAL {since_minutes} MINUTE
        GROUP BY host
        ORDER BY message_count DESC
        LIMIT 100
    """
    
    result = _execute_query(sql)
    
    if not result["success"]:
        return result
    
    return {
        "success": True,
        "since_minutes": since_minutes,
        "host_count": result["count"],
        "hosts": result["rows"]
    }


@mcp.tool()
def get_severity_stats(host: Optional[str] = None, since_minutes: int = 60) -> Dict[str, Any]:
    """
    Get syslog message counts grouped by severity.
    
    Args:
        host: Optional host filter
        since_minutes: Time window to search (default: 60)
    
    Returns:
        Message counts per severity level
    """
    since_minutes = max(1, since_minutes)
    
    conditions = [f"timestamp >= now() - INTERVAL {since_minutes} MINUTE"]
    
    if host:
        safe_host = host.replace("'", "\\'")
        conditions.append(f"host ILIKE '%{safe_host}%'")
    
    where_clause = " AND ".join(conditions)
    
    sql = f"""
        SELECT 
            severity,
            count() as count
        FROM {CLICKHOUSE_DATABASE}.syslog
        WHERE {where_clause}
        GROUP BY severity
        ORDER BY count DESC
    """
    
    result = _execute_query(sql)
    
    if not result["success"]:
        return result
    
    # Build summary
    total = sum(row.get("count", 0) for row in result["rows"])
    
    return {
        "success": True,
        "host": host,
        "since_minutes": since_minutes,
        "total_messages": total,
        "by_severity": result["rows"]
    }


@mcp.tool()
def get_recent_errors(
    host: Optional[str] = None,
    since_minutes: int = 30,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get recent error and critical syslog messages.
    
    Args:
        host: Optional host filter
        since_minutes: Time window to search (default: 30)
        limit: Maximum number of results (default: 50)
    
    Returns:
        Error and critical severity messages
    """
    since_minutes = max(1, since_minutes)
    limit = min(max(1, limit), 500)
    
    conditions = [
        f"timestamp >= now() - INTERVAL {since_minutes} MINUTE",
        "lower(severity) IN ('error', 'err', 'critical', 'crit', 'alert', 'emerg')"
    ]
    
    if host:
        safe_host = host.replace("'", "\\'")
        conditions.append(f"host ILIKE '%{safe_host}%'")
    
    where_clause = " AND ".join(conditions)
    
    sql = f"""
        SELECT 
            timestamp,
            host,
            facility,
            severity,
            program,
            message
        FROM {CLICKHOUSE_DATABASE}.syslog
        WHERE {where_clause}
        ORDER BY timestamp DESC
        LIMIT {limit}
    """
    
    result = _execute_query(sql)
    
    if not result["success"]:
        return result
    
    return {
        "success": True,
        "count": result["count"],
        "host": host,
        "since_minutes": since_minutes,
        "rows": result["rows"],
        "formatted": _format_syslog_rows(result["rows"])
    }


if __name__ == "__main__":
    print(f"🚀 Starting ClickHouse MCP Server")
    print(f"🗄️  ClickHouse URL: {CLICKHOUSE_URL}")
    print(f"📁 Database: {CLICKHOUSE_DATABASE}")
    print(f"🔌 Listening on: {MCP_HOST}:{MCP_PORT}")
    print(f"")
    print(f"📋 Available tools:")
    print(f"   - query_syslog: Query syslog with filters")
    print(f"   - query_clickhouse: Execute custom SELECT queries")
    print(f"   - get_syslog_hosts: List hosts sending syslog")
    print(f"   - get_severity_stats: Message counts by severity")
    print(f"   - get_recent_errors: Get recent error messages")
    
    mcp.run(transport="streamable-http", host=MCP_HOST, port=MCP_PORT)
