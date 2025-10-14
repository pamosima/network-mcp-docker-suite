"""
Cisco Catalyst Center MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to Cisco Catalyst Center functionality.
This server allows AI assistants and other MCP clients to interact with Catalyst Center for network
management, monitoring, and automation.

Features:
- Network device management and monitoring
- Site and topology management
- Client tracking and analytics
- Network assurance and compliance
- Template and configuration management
- Event and issue management

Environment Variables:
- CATC_URL: Required. Your Catalyst Center URL (e.g., https://catalyst-center.example.com)
- CATC_USERNAME: Required. Your Catalyst Center username
- CATC_PASSWORD: Required. Your Catalyst Center password
- MCP_PORT: Optional. Port for SSE server. Defaults to 8002
- MCP_HOST: Optional. Host for SSE server. Defaults to localhost

Author: Generated for MCP Client Integration
"""

import os
import json
import base64
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
CATC_URL = os.getenv("CATC_URL")
CATC_USERNAME = os.getenv("CATC_USERNAME")
CATC_PASSWORD = os.getenv("CATC_PASSWORD")
MCP_HOST = os.getenv("MCP_HOST", "localhost")
MCP_PORT = int(os.getenv("MCP_PORT", "8002"))

# Validate required environment variables
if not CATC_URL:
    raise ValueError("CATC_URL environment variable is required")
if not CATC_USERNAME:
    raise ValueError("CATC_USERNAME environment variable is required")
if not CATC_PASSWORD:
    raise ValueError("CATC_PASSWORD environment variable is required")

print(f"🌐 Catalyst Center URL: {CATC_URL}")
print(f"👤 Username: {CATC_USERNAME}")
print(f"🚀 Starting MCP server on {MCP_HOST}:{MCP_PORT}")

class CatalystCenterAPI:
    """Cisco Catalyst Center API client"""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.token = None
        self.session = requests.Session()
        
        # Disable SSL warnings for lab environments
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
    def authenticate(self) -> bool:
        """Authenticate with Catalyst Center and get token"""
        auth_url = f"{self.base_url}/dna/system/api/v1/auth/token"
        
        # Create basic auth header
        credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {credentials}"
        }
        
        try:
            response = self.session.post(auth_url, headers=headers, verify=False)
            if response.status_code == 200:
                self.token = response.json().get("Token")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        if not self.token:
            if not self.authenticate():
                raise Exception("Failed to authenticate with Catalyst Center")
        
        return {
            "Content-Type": "application/json",
            "X-Auth-Token": self.token
        }
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request to Catalyst Center API"""
        url = f"{self.base_url}/dna/intent/api/v1{endpoint}"
        headers = self._get_headers()
        
        try:
            response = self.session.get(url, headers=headers, params=params, verify=False)
            if response.status_code == 401:
                # Token expired, re-authenticate
                if self.authenticate():
                    headers = self._get_headers()
                    response = self.session.get(url, headers=headers, params=params, verify=False)
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ API Error: {e}")
            raise
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request to Catalyst Center API"""
        url = f"{self.base_url}/dna/intent/api/v1{endpoint}"
        headers = self._get_headers()
        
        try:
            response = self.session.post(url, headers=headers, json=data, verify=False)
            if response.status_code == 401:
                # Token expired, re-authenticate
                if self.authenticate():
                    headers = self._get_headers()
                    response = self.session.post(url, headers=headers, json=data, verify=False)
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ API Error: {e}")
            raise

# Initialize API client
catc_api = CatalystCenterAPI(CATC_URL, CATC_USERNAME, CATC_PASSWORD)

# Initialize FastMCP
mcp = FastMCP("Catalyst Center MCP Server")

@mcp.tool()
def get_network_devices(hostname: Optional[str] = None, device_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Get network devices from Catalyst Center
    
    Args:
        hostname: Optional device hostname to filter by
        device_type: Optional device type to filter by (e.g., 'Switches and Hubs', 'Routers')
    
    Returns:
        Dict containing device information
    """
    params = {}
    if hostname:
        params['hostname'] = hostname
    if device_type:
        params['type'] = device_type
        
    return catc_api.get("/network-device", params=params)

@mcp.tool()
def get_device_detail(device_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific device
    
    Args:
        device_id: The device ID/UUID
    
    Returns:
        Dict containing detailed device information
    """
    return catc_api.get(f"/network-device/{device_id}")

@mcp.tool()
def get_sites() -> Dict[str, Any]:
    """
    Get all sites from Catalyst Center
    
    Returns:
        Dict containing site information
    """
    return catc_api.get("/site")

@mcp.tool()
def get_site_topology(site_id: str) -> Dict[str, Any]:
    """
    Get topology for a specific site
    
    Args:
        site_id: The site ID/UUID
    
    Returns:
        Dict containing site topology information
    """
    return catc_api.get(f"/topology/site-topology", params={"siteId": site_id})

@mcp.tool()
def get_clients(limit: int = 100) -> Dict[str, Any]:
    """
    Get client information from Catalyst Center
    
    Args:
        limit: Maximum number of clients to return (default: 100)
    
    Returns:
        Dict containing client information
    """
    params = {"limit": limit}
    return catc_api.get("/client-health", params=params)

@mcp.tool()
def get_network_health() -> Dict[str, Any]:
    """
    Get overall network health information
    
    Returns:
        Dict containing network health metrics
    """
    return catc_api.get("/network-health")

@mcp.tool()
def get_device_health(device_id: str) -> Dict[str, Any]:
    """
    Get health information for a specific device
    
    Args:
        device_id: The device ID/UUID
    
    Returns:
        Dict containing device health information
    """
    return catc_api.get(f"/device-health/{device_id}")

@mcp.tool()
def get_issues(priority: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
    """
    Get network issues from Catalyst Center
    
    Args:
        priority: Optional priority filter (P1, P2, P3, P4)
        status: Optional status filter (ACTIVE, RESOLVED)
    
    Returns:
        Dict containing network issues
    """
    params = {}
    if priority:
        params['priority'] = priority
    if status:
        params['status'] = status
        
    return catc_api.get("/issues", params=params)

@mcp.tool()
def get_templates() -> Dict[str, Any]:
    """
    Get configuration templates from Catalyst Center
    
    Returns:
        Dict containing template information
    """
    return catc_api.get("/template-programmer/template")

@mcp.tool()
def get_compliance_detail(device_id: str) -> Dict[str, Any]:
    """
    Get compliance details for a specific device
    
    Args:
        device_id: The device ID/UUID
    
    Returns:
        Dict containing device compliance information
    """
    return catc_api.get(f"/compliance/{device_id}/detail")

@mcp.tool()
def get_events(category: Optional[str] = None, severity: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
    """
    Get events from Catalyst Center
    
    Args:
        category: Optional event category filter
        severity: Optional severity filter (INFO, WARN, ERROR, ALERT, CRITICAL)
        limit: Maximum number of events to return (default: 100)
    
    Returns:
        Dict containing event information
    """
    params = {"limit": limit}
    if category:
        params['category'] = category
    if severity:
        params['severity'] = severity
        
    return catc_api.get("/events", params=params)

if __name__ == "__main__":
    print("🚀 Starting Catalyst Center MCP Server...")
    
    # Test authentication
    if catc_api.authenticate():
        print("✅ Successfully authenticated with Catalyst Center")
    else:
        print("❌ Failed to authenticate with Catalyst Center")
        exit(1)
    
    # Start the MCP server
    mcp.run(transport="http", host=MCP_HOST, port=MCP_PORT)
