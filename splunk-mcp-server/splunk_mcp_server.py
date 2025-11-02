"""
Splunk MCP Server - FastMCP Wrapper

A Model Context Protocol (MCP) server that wraps Splunk's MCP backend using fastmcp.
This provides proper MCP protocol support with HTTP transport for MCP client compatibility.

Features:
- SSL certificate handling for self-signed certs
- Bearer token authentication  
- Proper MCP protocol via fastmcp
- Tool forwarding to Splunk backend

Environment Variables:
- SPLUNK_HOST: Required. Splunk server hostname/IP
- SPLUNK_PORT: Required. Splunk server port (default: 8089)
- SPLUNK_API_KEY: Required. Splunk Bearer token
- SPLUNK_VERIFY_SSL: Optional. Verify SSL certificates (default: false)
- MCP_PORT: Optional. Port for this MCP server (default: 8006)
- MCP_HOST: Optional. Host for this MCP server (default: 0.0.0.0)

Author: Patrick Mosimann
"""

import httpx
import os
import logging
import json
from pathlib import Path
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ---- Environment Variables ----
def load_dotenv_file(env_file: str = ".env") -> bool:
    """Load environment variables from a .env file"""
    env_path = Path(env_file)
    
    if not env_path.exists():
        logger.warning(f"⚠️  .env file not found at {env_path.absolute()}")
        logger.info(f"📋 Using environment variables or defaults")
        return False
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    os.environ[key] = value
        
        logger.info(f"✅ Loaded environment from {env_file}")
        return True
    except Exception as e:
        logger.error(f"❌ Error loading .env file: {e}")
        return False

# Load .env file first
load_dotenv_file()

# Get Splunk configuration from environment
splunk_host = os.getenv("SPLUNK_HOST")
splunk_port = os.getenv("SPLUNK_PORT", "8089")
splunk_api_key = os.getenv("SPLUNK_API_KEY")
splunk_verify_ssl = os.getenv("SPLUNK_VERIFY_SSL", "false").lower() == "true"

# Get MCP server configuration
mcp_port = int(os.getenv("MCP_PORT", "8006"))
mcp_host = os.getenv("MCP_HOST", "0.0.0.0")

# Validate required configuration
if not splunk_host:
    logger.error("❌ SPLUNK_HOST not configured!")
    logger.error("📋 Please set SPLUNK_HOST in .env file")
    exit(1)

if not splunk_api_key or splunk_api_key.startswith('your_actual_'):
    logger.error("❌ SPLUNK_API_KEY not configured properly!")
    logger.error("📋 Please set your Splunk API key in .env file")
    exit(1)

# Build Splunk backend URL
splunk_backend_url = f"https://{splunk_host}:{splunk_port}/services/mcp"

logger.info(f"✅ Splunk backend: {splunk_backend_url}")
logger.info(f"✅ API key loaded: {splunk_api_key[:8]}...{splunk_api_key[-4:]}")
logger.info(f"✅ SSL verification: {splunk_verify_ssl}")
logger.info(f"🌐 MCP Server will run on: http://{mcp_host}:{mcp_port}")

# Create HTTP client for Splunk backend
http_client = httpx.AsyncClient(
    verify=splunk_verify_ssl,
    timeout=60.0,
    follow_redirects=True
)

# Create FastMCP server
mcp = FastMCP("Splunk MCP Server")

# Helper function to call Splunk backend
async def call_splunk_mcp(method: str, params: dict = None):
    """Call Splunk MCP backend with JSON-RPC"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }
    
    try:
        response = await http_client.post(
            splunk_backend_url,
            json=payload,
            headers={
                "Authorization": f"Bearer {splunk_api_key}",
                "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
        result = response.json()
        
        if "error" in result:
            raise Exception(f"Splunk MCP error: {result['error']}")
        
        return result.get("result", {})
    except Exception as e:
        logger.error(f"Error calling Splunk MCP: {e}")
        raise

# Define Splunk tools as MCP tools
@mcp.tool()
async def get_splunk_info() -> dict:
    """Get comprehensive Splunk instance information including version, licensing, and deployment details"""
    return await call_splunk_mcp("tools/call", {
        "name": "get_splunk_info",
        "arguments": {}
    })

@mcp.tool()
async def get_indexes() -> dict:
    """List all Splunk indexes with their properties"""
    return await call_splunk_mcp("tools/call", {
        "name": "get_indexes",
        "arguments": {}
    })

@mcp.tool()
async def get_index_info(index_name: str) -> dict:
    """Get detailed information about a specific Splunk index
    
    Args:
        index_name: Name of the index to query
    """
    return await call_splunk_mcp("tools/call", {
        "name": "get_index_info",
        "arguments": {"index_name": index_name}
    })

@mcp.tool()
async def get_user_list() -> dict:
    """Get list of Splunk users"""
    return await call_splunk_mcp("tools/call", {
        "name": "get_user_list",
        "arguments": {}
    })

@mcp.tool()
async def get_user_info() -> dict:
    """Get current user information"""
    return await call_splunk_mcp("tools/call", {
        "name": "get_user_info",
        "arguments": {}
    })

@mcp.tool()
async def run_splunk_query(
    query: str,
    earliest_time: str = "-24h",
    latest_time: str = "now",
    max_results: int = 100
) -> dict:
    """Execute a Splunk SPL (Search Processing Language) query
    
    Args:
        query: SPL query string (e.g., "search index=_internal | stats count by sourcetype")
        earliest_time: Start time for search (default: -24h)
        latest_time: End time for search (default: now)
        max_results: Maximum number of results to return (default: 100)
    """
    return await call_splunk_mcp("tools/call", {
        "name": "run_splunk_query",
        "arguments": {
            "query": query,
            "earliest_time": earliest_time,
            "latest_time": latest_time,
            "max_results": max_results
        }
    })

@mcp.tool()
async def get_metadata(
    metadata_type: str,
    index: str = None,
    earliest_time: str = "-24h",
    latest_time: str = "now"
) -> dict:
    """Retrieve metadata about hosts, sources, or sourcetypes
    
    Args:
        metadata_type: Type of metadata (hosts, sources, or sourcetypes)
        index: Optional index name to filter results
        earliest_time: Start time (default: -24h)
        latest_time: End time (default: now)
    """
    return await call_splunk_mcp("tools/call", {
        "name": "get_metadata",
        "arguments": {
            "metadata_type": metadata_type,
            "index": index,
            "earliest_time": earliest_time,
            "latest_time": latest_time
        }
    })

@mcp.tool()
async def get_kv_store_collections() -> dict:
    """Get KV Store collection statistics"""
    return await call_splunk_mcp("tools/call", {
        "name": "get_kv_store_collections",
        "arguments": {}
    })

@mcp.tool()
async def get_knowledge_objects(object_type: str = None) -> dict:
    """Retrieve knowledge objects like saved searches, alerts, dashboards, etc.
    
    Args:
        object_type: Optional type filter (savedsearches, alerts, dashboards, etc.)
    """
    return await call_splunk_mcp("tools/call", {
        "name": "get_knowledge_objects",
        "arguments": {"object_type": object_type} if object_type else {}
    })

if __name__ == "__main__":
    logger.info("🚀 Splunk MCP Server starting...")
    logger.info(f"📡 Backend: {splunk_backend_url}")
    logger.info(f"🔑 SSL Verification: {splunk_verify_ssl}")
    logger.info(f"🛠️  Tools: 9 Splunk tools available")
    
    mcp.run(transport="streamable-http", host=mcp_host, port=mcp_port)
