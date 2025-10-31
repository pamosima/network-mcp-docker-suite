"""
Cisco ISE MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to Cisco Identity Services Engine (ISE) API functionality.
This server allows AI assistants and other MCP clients to interact with Cisco ISE for network access control,
policy management, and security operations.

Features:
- Dynamic tool generation from ISE REST API endpoints
- Identity and device management
- Policy enforcement and compliance monitoring
- Network access control operations
- Session management and monitoring
- Certificate and profiling services
- Read-only operations for security

Environment Variables:
- ISE_HOST: Required. Your Cisco ISE server hostname or IP
- ISE_USERNAME: Required. Your ISE username with API access
- ISE_PASSWORD: Required. Your ISE password
- ISE_VERSION: Optional. ISE API version. Defaults to 1.0
- ISE_VERIFY_SSL: Optional. SSL verification. Defaults to False
- MCP_PORT: Optional. Port for MCP server. Defaults to 8005
- MCP_HOST: Optional. Host for MCP server. Defaults to localhost

Author: Patrick Mosimann
Based on: https://github.com/automateyournetwork/ISE_MCP
"""

import os
import json
import requests
import urllib3
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from fastmcp import FastMCP

# Disable SSL warnings if verify is False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
ISE_HOST = os.getenv("ISE_HOST")
ISE_USERNAME = os.getenv("ISE_USERNAME")
ISE_PASSWORD = os.getenv("ISE_PASSWORD")
ISE_VERSION = os.getenv("ISE_VERSION", "1.0")
ISE_VERIFY_SSL = os.getenv("ISE_VERIFY_SSL", "False").lower() == "true"
mcp_host = os.getenv("MCP_HOST", "localhost")
mcp_port = int(os.getenv("MCP_PORT", "8005"))

# Validate required environment variables
if not all([ISE_HOST, ISE_USERNAME, ISE_PASSWORD]):
    raise ValueError("ISE_HOST, ISE_USERNAME, and ISE_PASSWORD environment variables are required")

print(f"🌐 ISE Server: {ISE_HOST}")
print(f"👤 ISE User: {ISE_USERNAME}")
print(f"🔐 SSL Verification: {ISE_VERIFY_SSL}")
print(f"📡 API Version: {ISE_VERSION}")
print(f"🚀 Starting MCP server on {mcp_host}:{mcp_port}")

class CiscoISEAPI:
    """Cisco ISE REST API client"""
    
    def __init__(self, host: str, username: str, password: str, version: str = "1.0", verify_ssl: bool = False):
        self.host = host.rstrip('/')
        self.username = username
        self.password = password
        self.version = version
        self.verify_ssl = verify_ssl
        self.base_url = f"https://{self.host}/ers/config"
        
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Network-MCP-Server/1.0 pamosima"
        })
        self.session.verify = verify_ssl
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request to ISE ERS API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ ISE API Error: {e}")
            raise

# Initialize ISE API client
ise_api = CiscoISEAPI(ISE_HOST, ISE_USERNAME, ISE_PASSWORD, ISE_VERSION, ISE_VERIFY_SSL)

# Initialize FastMCP
mcp = FastMCP("Cisco ISE MCP Server")

# ISE API Endpoints Configuration
ISE_ENDPOINTS = {
    "network_devices": {
        "path": "networkdevice",
        "description": "Network devices registered in ISE",
        "filterable": ["name", "ipAddress", "description"]
    },
    "identity_groups": {
        "path": "identitygroup",
        "description": "Identity groups for user categorization",
        "filterable": ["name", "description"]
    },
    "endpoint_identity_groups": {
        "path": "endpointgroup",
        "description": "Endpoint identity groups for device categorization",
        "filterable": ["name", "description"]
    },
    "authorization_profiles": {
        "path": "authorizationprofile",
        "description": "Authorization profiles for policy enforcement",
        "filterable": ["name", "description"]
    },
    "network_access_policies": {
        "path": "networkaccess/policyset",
        "description": "Network access policy sets",
        "filterable": ["name", "description"]
    },
    "endpoints": {
        "path": "endpoint",
        "description": "Endpoints (devices) known to ISE",
        "filterable": ["name", "mac", "description"]
    },
    "internal_users": {
        "path": "internaluser",
        "description": "Internal users configured in ISE",
        "filterable": ["name", "email", "description"]
    },
    "guest_users": {
        "path": "guestuser",
        "description": "Guest users in ISE",
        "filterable": ["name", "guestType", "sponsorUserName"]
    },
    "active_sessions": {
        "path": "session",
        "description": "Active network access sessions",
        "filterable": ["userName", "endPointMACAddress", "nasIPAddress"]
    },
    "profiler_profiles": {
        "path": "profilerprofile",
        "description": "Profiler profiles for device classification",
        "filterable": ["name", "description"]
    },
    "security_groups": {
        "path": "sgt",
        "description": "Security Group Tags (SGTs) for TrustSec",
        "filterable": ["name", "description"]
    },
    "sxp_connections": {
        "path": "sxpconnections",
        "description": "SXP connections for IP-SGT mapping distribution",
        "filterable": ["ipAddress", "sxpPeer"]
    },
    "tacacs_command_sets": {
        "path": "tacacscommandsets",
        "description": "TACACS+ command sets for device administration",
        "filterable": ["name", "description"]
    },
    "tacacs_profiles": {
        "path": "tacacsprofile",
        "description": "TACACS+ profiles for device administration",
        "filterable": ["name", "description"]
    },
    "admin_users": {
        "path": "adminuser",
        "description": "Administrative users in ISE",
        "filterable": ["name", "email", "firstName", "lastName"]
    }
}

@mcp.tool()
def ise_get_network_devices(
    filter_expression: Optional[str] = None,
    page: int = 1,
    size: int = 20
) -> Dict[str, Any]:
    """
    Get network devices registered in ISE
    
    Args:
        filter_expression: Filter in format 'field.OPERATION.value' (e.g., 'name.CONTAINS.switch')
        page: Page number for pagination (default: 1)
        size: Number of results per page (default: 20, max: 100)
    
    Returns:
        Dict containing network device information
    """
    params = {"page": page, "size": min(size, 100)}
    if filter_expression:
        params["filter"] = filter_expression
    
    return ise_api.get("networkdevice", params=params)

@mcp.tool()
def ise_get_identity_groups(
    filter_expression: Optional[str] = None,
    page: int = 1,
    size: int = 20
) -> Dict[str, Any]:
    """
    Get identity groups for user categorization
    
    Args:
        filter_expression: Filter in format 'field.OPERATION.value' (e.g., 'name.CONTAINS.employee')
        page: Page number for pagination (default: 1)
        size: Number of results per page (default: 20, max: 100)
    
    Returns:
        Dict containing identity group information
    """
    params = {"page": page, "size": min(size, 100)}
    if filter_expression:
        params["filter"] = filter_expression
    
    return ise_api.get("identitygroup", params=params)

@mcp.tool()
def ise_get_endpoint_groups(
    filter_expression: Optional[str] = None,
    page: int = 1,
    size: int = 20
) -> Dict[str, Any]:
    """
    Get endpoint identity groups for device categorization
    
    Args:
        filter_expression: Filter in format 'field.OPERATION.value' (e.g., 'name.CONTAINS.printer')
        page: Page number for pagination (default: 1)
        size: Number of results per page (default: 20, max: 100)
    
    Returns:
        Dict containing endpoint group information
    """
    params = {"page": page, "size": min(size, 100)}
    if filter_expression:
        params["filter"] = filter_expression
    
    return ise_api.get("endpointgroup", params=params)

@mcp.tool()
def ise_get_authorization_profiles(
    filter_expression: Optional[str] = None,
    page: int = 1,
    size: int = 20
) -> Dict[str, Any]:
    """
    Get authorization profiles for policy enforcement
    
    Args:
        filter_expression: Filter in format 'field.OPERATION.value' (e.g., 'name.CONTAINS.permit')
        page: Page number for pagination (default: 1)
        size: Number of results per page (default: 20, max: 100)
    
    Returns:
        Dict containing authorization profile information
    """
    params = {"page": page, "size": min(size, 100)}
    if filter_expression:
        params["filter"] = filter_expression
    
    return ise_api.get("authorizationprofile", params=params)

@mcp.tool()
def ise_get_network_access_policies(
    filter_expression: Optional[str] = None,
    page: int = 1,
    size: int = 20
) -> Dict[str, Any]:
    """
    Get network access policy sets
    
    Args:
        filter_expression: Filter in format 'field.OPERATION.value' (e.g., 'name.CONTAINS.wireless')
        page: Page number for pagination (default: 1)
        size: Number of results per page (default: 20, max: 100)
    
    Returns:
        Dict containing network access policy information
    """
    params = {"page": page, "size": min(size, 100)}
    if filter_expression:
        params["filter"] = filter_expression
    
    return ise_api.get("networkaccess/policyset", params=params)

@mcp.tool()
def ise_get_endpoints(
    filter_expression: Optional[str] = None,
    page: int = 1,
    size: int = 20
) -> Dict[str, Any]:
    """
    Get endpoints (devices) known to ISE
    
    Args:
        filter_expression: Filter in format 'field.OPERATION.value' (e.g., 'mac.EQUALS.00:50:56:C0:00:01')
        page: Page number for pagination (default: 1)
        size: Number of results per page (default: 20, max: 100)
    
    Returns:
        Dict containing endpoint device information
    """
    params = {"page": page, "size": min(size, 100)}
    if filter_expression:
        params["filter"] = filter_expression
    
    return ise_api.get("endpoint", params=params)

@mcp.tool()
def ise_get_internal_users(
    filter_expression: Optional[str] = None,
    page: int = 1,
    size: int = 20
) -> Dict[str, Any]:
    """
    Get internal users configured in ISE
    
    Args:
        filter_expression: Filter in format 'field.OPERATION.value' (e.g., 'name.CONTAINS.admin')
        page: Page number for pagination (default: 1)
        size: Number of results per page (default: 20, max: 100)
    
    Returns:
        Dict containing internal user information
    """
    params = {"page": page, "size": min(size, 100)}
    if filter_expression:
        params["filter"] = filter_expression
    
    return ise_api.get("internaluser", params=params)

@mcp.tool()
def ise_get_guest_users(
    filter_expression: Optional[str] = None,
    page: int = 1,
    size: int = 20
) -> Dict[str, Any]:
    """
    Get guest users in ISE
    
    Args:
        filter_expression: Filter in format 'field.OPERATION.value' (e.g., 'sponsorUserName.CONTAINS.sponsor')
        page: Page number for pagination (default: 1)
        size: Number of results per page (default: 20, max: 100)
    
    Returns:
        Dict containing guest user information
    """
    params = {"page": page, "size": min(size, 100)}
    if filter_expression:
        params["filter"] = filter_expression
    
    return ise_api.get("guestuser", params=params)

@mcp.tool()
def ise_get_active_sessions(
    filter_expression: Optional[str] = None,
    page: int = 1,
    size: int = 20
) -> Dict[str, Any]:
    """
    Get active network access sessions
    
    Args:
        filter_expression: Filter in format 'field.OPERATION.value' (e.g., 'userName.CONTAINS.john')
        page: Page number for pagination (default: 1)
        size: Number of results per page (default: 20, max: 100)
    
    Returns:
        Dict containing active session information
    """
    params = {"page": page, "size": min(size, 100)}
    if filter_expression:
        params["filter"] = filter_expression
    
    return ise_api.get("session", params=params)

@mcp.tool()
def ise_get_profiler_profiles(
    filter_expression: Optional[str] = None,
    page: int = 1,
    size: int = 20
) -> Dict[str, Any]:
    """
    Get profiler profiles for device classification
    
    Args:
        filter_expression: Filter in format 'field.OPERATION.value' (e.g., 'name.CONTAINS.cisco')
        page: Page number for pagination (default: 1)
        size: Number of results per page (default: 20, max: 100)
    
    Returns:
        Dict containing profiler profile information
    """
    params = {"page": page, "size": min(size, 100)}
    if filter_expression:
        params["filter"] = filter_expression
    
    return ise_api.get("profilerprofile", params=params)

@mcp.tool()
def ise_get_security_groups(
    filter_expression: Optional[str] = None,
    page: int = 1,
    size: int = 20
) -> Dict[str, Any]:
    """
    Get Security Group Tags (SGTs) for TrustSec
    
    Args:
        filter_expression: Filter in format 'field.OPERATION.value' (e.g., 'name.CONTAINS.employee')
        page: Page number for pagination (default: 1)
        size: Number of results per page (default: 20, max: 100)
    
    Returns:
        Dict containing Security Group Tag information
    """
    params = {"page": page, "size": min(size, 100)}
    if filter_expression:
        params["filter"] = filter_expression
    
    return ise_api.get("sgt", params=params)

@mcp.tool()
def ise_get_admin_users(
    filter_expression: Optional[str] = None,
    page: int = 1,
    size: int = 20
) -> Dict[str, Any]:
    """
    Get administrative users in ISE
    
    Args:
        filter_expression: Filter in format 'field.OPERATION.value' (e.g., 'name.CONTAINS.admin')
        page: Page number for pagination (default: 1)
        size: Number of results per page (default: 20, max: 100)
    
    Returns:
        Dict containing administrative user information
    """
    params = {"page": page, "size": min(size, 100)}
    if filter_expression:
        params["filter"] = filter_expression
    
    return ise_api.get("adminuser", params=params)

@mcp.tool()
def ise_search_endpoint_by_mac(mac_address: str) -> Dict[str, Any]:
    """
    Search for a specific endpoint by MAC address
    
    Args:
        mac_address: MAC address to search for (e.g., '00:50:56:C0:00:01')
    
    Returns:
        Dict containing endpoint information for the specified MAC address
    """
    filter_expr = f"mac.EQUALS.{mac_address}"
    return ise_api.get("endpoint", params={"filter": filter_expr})

@mcp.tool()
def ise_search_user_sessions(username: str) -> Dict[str, Any]:
    """
    Search for active sessions by username
    
    Args:
        username: Username to search for
    
    Returns:
        Dict containing active session information for the specified user
    """
    filter_expr = f"userName.EQUALS.{username}"
    return ise_api.get("session", params={"filter": filter_expr})

@mcp.tool()
def ise_get_device_compliance_status(mac_address: str) -> Dict[str, Any]:
    """
    Get compliance status for a device by MAC address
    
    Args:
        mac_address: MAC address of the device to check
    
    Returns:
        Dict containing compliance and profiling information for the device
    """
    # Get endpoint information
    endpoint_filter = f"mac.EQUALS.{mac_address}"
    endpoint_data = ise_api.get("endpoint", params={"filter": endpoint_filter})
    
    return {
        "mac_address": mac_address,
        "endpoint_data": endpoint_data,
        "compliance_status": "Retrieved endpoint data - check profiledBy and groupId fields for compliance"
    }

@mcp.tool()
def ise_get_sxp_connections(
    filter_expression: Optional[str] = None,
    page: int = 1,
    size: int = 20
) -> Dict[str, Any]:
    """
    Get SXP connections for IP-SGT mapping distribution (TrustSec)
    
    Args:
        filter_expression: Filter in format 'field.OPERATION.value' (e.g., 'ipAddress.CONTAINS.192.168')
        page: Page number for pagination (default: 1)
        size: Number of results per page (default: 20, max: 100)
    
    Returns:
        Dict containing SXP connection information for TrustSec
    """
    params = {"page": page, "size": min(size, 100)}
    if filter_expression:
        params["filter"] = filter_expression
    
    return ise_api.get("sxpconnections", params=params)

@mcp.tool()
def ise_get_tacacs_command_sets(
    filter_expression: Optional[str] = None,
    page: int = 1,
    size: int = 20
) -> Dict[str, Any]:
    """
    Get TACACS+ command sets for device administration authorization
    
    Args:
        filter_expression: Filter in format 'field.OPERATION.value' (e.g., 'name.CONTAINS.network')
        page: Page number for pagination (default: 1)
        size: Number of results per page (default: 20, max: 100)
    
    Returns:
        Dict containing TACACS+ command set information
    """
    params = {"page": page, "size": min(size, 100)}
    if filter_expression:
        params["filter"] = filter_expression
    
    return ise_api.get("tacacscommandsets", params=params)

@mcp.tool()
def ise_get_tacacs_profiles(
    filter_expression: Optional[str] = None,
    page: int = 1,
    size: int = 20
) -> Dict[str, Any]:
    """
    Get TACACS+ profiles for device administration authentication
    
    Args:
        filter_expression: Filter in format 'field.OPERATION.value' (e.g., 'name.CONTAINS.admin')
        page: Page number for pagination (default: 1)
        size: Number of results per page (default: 20, max: 100)
    
    Returns:
        Dict containing TACACS+ profile information
    """
    params = {"page": page, "size": min(size, 100)}
    if filter_expression:
        params["filter"] = filter_expression
    
    return ise_api.get("tacacsprofile", params=params)

if __name__ == "__main__":
    print("🚀 Starting Cisco ISE MCP Server...")
    
    # Test ISE API connectivity
    try:
        network_devices = ise_api.get("networkdevice", params={"size": 1})
        print("✅ Successfully connected to ISE ERS API")
        print(f"📊 ISE Server Version: {ISE_VERSION}")
    except Exception as e:
        print(f"❌ Failed to connect to ISE API: {e}")
        print("💡 Please check your ISE credentials, host connectivity, and ERS API status")
        exit(1)
    
    # Start the MCP server
    mcp.run(transport="http", host=mcp_host, port=mcp_port)
