"""
ThousandEyes MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to Cisco ThousandEyes v7 API functionality.
This server allows AI assistants and other MCP clients to interact with ThousandEyes for network
monitoring, performance analysis, and troubleshooting.

Features:
- Network performance monitoring and analysis
- Test management and results retrieval
- Agent monitoring and path visualization
- Dashboard and widget data access
- Alert and event detection
- Read-only operations for security

Environment Variables:
- TE_TOKEN: Required. Your ThousandEyes API v7 Bearer token
- TE_BASE_URL: Optional. ThousandEyes API base URL. Defaults to https://api.thousandeyes.com/v7
- MCP_PORT: Optional. Port for MCP server. Defaults to 8004
- MCP_HOST: Optional. Host for MCP server. Defaults to localhost

Author: Patrick Mosimann
Based on: https://github.com/CiscoDevNet/thousandeyes-mcp-community
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import requests
from fastmcp import FastMCP

# ---- Environment Variables ----
def load_dotenv_file(env_file: str = ".env") -> bool:
    """Load environment variables from a .env file"""
    env_path = Path(env_file)
    
    if not env_path.exists():
        print(f"⚠️  .env file not found at {env_path.absolute()}")
        print(f"📋 Using environment variables or defaults")
        return False
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip().strip('\'"')
                    os.environ[key.strip()] = value
        print(f"✅ Loaded environment variables from {env_path}")
        return True
    except Exception as e:
        print(f"❌ Error loading .env file: {e}")
        return False

# Load environment variables
load_dotenv_file()

# Configuration
TE_TOKEN = os.getenv("TE_TOKEN")
TE_BASE_URL = os.getenv("TE_BASE_URL", "https://api.thousandeyes.com/v7")
mcp_host = os.getenv("MCP_HOST", "localhost")
mcp_port = int(os.getenv("MCP_PORT", "8004"))

# Validate required environment variables
if not TE_TOKEN:
    raise ValueError("TE_TOKEN environment variable is required")

print(f"🌐 ThousandEyes API URL: {TE_BASE_URL}")
print(f"🔑 Token configured: {TE_TOKEN[:8]}...{TE_TOKEN[-4:] if len(TE_TOKEN) > 12 else '***'}")
print(f"🚀 Starting MCP server on {mcp_host}:{mcp_port}")

class ThousandEyesAPI:
    """ThousandEyes API v7 client"""
    
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Network-MCP-Server/1.0 pamosima"
        })
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request to ThousandEyes API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ API Error: {e}")
            raise

# Initialize API client
te_api = ThousandEyesAPI(TE_BASE_URL, TE_TOKEN)

# Initialize FastMCP
mcp = FastMCP("ThousandEyes MCP Server")

@mcp.tool()
def te_list_tests(aid: Optional[int] = None, name_contains: Optional[str] = None, test_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Lists tests (filter by name/type/Account Group)
    
    Args:
        aid: Account Group ID to filter by
        name_contains: Filter tests by name containing this string
        test_type: Filter by test type (e.g., 'http-server', 'page-load', 'web-transactions')
    
    Returns:
        Dict containing test information
    """
    params = {}
    if aid:
        params['aid'] = aid
    if name_contains:
        params['testName'] = name_contains
    if test_type:
        params['type'] = test_type
        
    return te_api.get("/tests", params=params)

@mcp.tool()
def te_list_agents(agent_types: Optional[str] = None, aid: Optional[int] = None) -> Dict[str, Any]:
    """
    Lists enterprise / enterprise-cluster / cloud agents
    
    Args:
        agent_types: Comma-separated list of agent types ('enterprise', 'enterprise-cluster', 'cloud')
        aid: Account Group ID to filter by
    
    Returns:
        Dict containing agent information
    """
    params = {}
    if agent_types:
        params['agentTypes'] = agent_types
    if aid:
        params['aid'] = aid
        
    return te_api.get("/agents", params=params)

@mcp.tool()
def te_get_test_results(
    test_id: int, 
    test_type: str, 
    window: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    aid: Optional[int] = None,
    agent_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get test results (e.g., network, page-load, web-transactions; not dns-server)
    
    Args:
        test_id: Test ID to get results for
        test_type: Type of test ('network', 'page-load', 'web-transactions', etc.)
        window: Time window (e.g., '1h', '6h', '1d', '1w')
        start: Start time in ISO format (alternative to window)
        end: End time in ISO format (alternative to window)
        aid: Account Group ID
        agent_id: Specific agent ID to filter results
    
    Returns:
        Dict containing test results
    """
    params = {}
    if window:
        params['window'] = window
    if start:
        params['from'] = start
    if end:
        params['to'] = end
    if aid:
        params['aid'] = aid
    if agent_id:
        params['agentId'] = agent_id
        
    return te_api.get(f"/test-results/{test_id}/{test_type}", params=params)

@mcp.tool()
def te_get_path_vis(
    test_id: int,
    window: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    aid: Optional[int] = None,
    agent_id: Optional[int] = None,
    direction: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get path visualization data
    
    Args:
        test_id: Test ID to get path visualization for
        window: Time window (e.g., '1h', '6h', '1d', '1w')
        start: Start time in ISO format (alternative to window)
        end: End time in ISO format (alternative to window)
        aid: Account Group ID
        agent_id: Specific agent ID to filter results
        direction: Direction of path visualization ('to-target', 'from-target')
    
    Returns:
        Dict containing path visualization data
    """
    params = {}
    if window:
        params['window'] = window
    if start:
        params['from'] = start
    if end:
        params['to'] = end
    if aid:
        params['aid'] = aid
    if agent_id:
        params['agentId'] = agent_id
    if direction:
        params['direction'] = direction
        
    return te_api.get(f"/test-results/{test_id}/path-vis", params=params)

@mcp.tool()
def te_list_dashboards(aid: Optional[int] = None, title_contains: Optional[str] = None) -> Dict[str, Any]:
    """
    Lists dashboards
    
    Args:
        aid: Account Group ID to filter by
        title_contains: Filter dashboards by title containing this string
    
    Returns:
        Dict containing dashboard information
    """
    params = {}
    if aid:
        params['aid'] = aid
    if title_contains:
        params['title'] = title_contains
        
    return te_api.get("/dashboards", params=params)

@mcp.tool()
def te_get_dashboard(dashboard_id: str, aid: Optional[int] = None) -> Dict[str, Any]:
    """
    Get dashboard details including widget list
    
    Args:
        dashboard_id: Dashboard ID to retrieve
        aid: Account Group ID
    
    Returns:
        Dict containing dashboard details and widget list
    """
    params = {}
    if aid:
        params['aid'] = aid
        
    return te_api.get(f"/dashboards/{dashboard_id}", params=params)

@mcp.tool()
def te_get_dashboard_widget(
    dashboard_id: str,
    widget_id: str,
    window: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    aid: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get widget data for a dashboard
    
    Args:
        dashboard_id: Dashboard ID
        widget_id: Widget ID within the dashboard
        window: Time window (e.g., '1h', '6h', '1d', '1w')
        start: Start time in ISO format (alternative to window)
        end: End time in ISO format (alternative to window)
        aid: Account Group ID
    
    Returns:
        Dict containing widget data
    """
    params = {}
    if window:
        params['window'] = window
    if start:
        params['from'] = start
    if end:
        params['to'] = end
    if aid:
        params['aid'] = aid
        
    return te_api.get(f"/dashboards/{dashboard_id}/widgets/{widget_id}", params=params)

@mcp.tool()
def te_get_users() -> Dict[str, Any]:
    """
    Lists users in the ThousandEyes account
    
    Returns:
        Dict containing user information
    """
    return te_api.get("/users")

@mcp.tool()
def te_get_account_groups() -> Dict[str, Any]:
    """
    Lists account groups available to the authenticated organization
    
    Returns:
        Dict containing account group information
    """
    return te_api.get("/account-groups")

@mcp.tool()
def te_list_alerts(
    window: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    aid: Optional[int] = None,
    test_id: Optional[int] = None,
    alert_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Lists alerts from ThousandEyes
    
    Args:
        window: Time window (e.g., '1h', '6h', '1d', '1w')
        start: Start time in ISO format (alternative to window)
        end: End time in ISO format (alternative to window) 
        aid: Account Group ID
        test_id: Filter alerts for specific test
        alert_type: Filter by alert type
    
    Returns:
        Dict containing alert information
    """
    params = {}
    if window:
        params['window'] = window
    if start:
        params['from'] = start
    if end:
        params['to'] = end
    if aid:
        params['aid'] = aid
    if test_id:
        params['testId'] = test_id
    if alert_type:
        params['type'] = alert_type
        
    return te_api.get("/alerts", params=params)

if __name__ == "__main__":
    print("🚀 Starting ThousandEyes MCP Server...")
    
    # Test API connectivity
    try:
        account_groups = te_api.get("/account-groups")
        print("✅ Successfully connected to ThousandEyes API")
        print(f"📊 Account Groups available: {len(account_groups.get('accountGroups', []))}")
    except Exception as e:
        print(f"❌ Failed to connect to ThousandEyes API: {e}")
        print("💡 Please check your TE_TOKEN and network connectivity")
        exit(1)
    
    # Start the MCP server
    mcp.run(transport="http", host=mcp_host, port=mcp_port)
