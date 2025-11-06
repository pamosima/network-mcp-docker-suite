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
- CATC_VERIFY_SSL: Optional. SSL certificate verification. Defaults to false (use true for production with valid certs)
- MCP_PORT: Optional. Port for MCP server. Defaults to 8002
- MCP_HOST: Optional. Host for MCP server. Defaults to localhost

Author: Patrick Mosimann
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
CATC_VERIFY_SSL = os.getenv("CATC_VERIFY_SSL", "false").lower() in ("true", "1", "yes")
mcp_host = os.getenv("MCP_HOST", "localhost")
mcp_port = int(os.getenv("MCP_PORT", "8002"))

# Validate required environment variables
if not CATC_URL:
    raise ValueError("CATC_URL environment variable is required")
if not CATC_USERNAME:
    raise ValueError("CATC_USERNAME environment variable is required")
if not CATC_PASSWORD:
    raise ValueError("CATC_PASSWORD environment variable is required")

print(f"🌐 Catalyst Center URL: {CATC_URL}")
print(f"👤 Username: {CATC_USERNAME}")
print(f"🔒 SSL verification: {'enabled' if CATC_VERIFY_SSL else 'disabled'}")
print(f"🚀 Starting MCP server on {mcp_host}:{mcp_port}")

class CatalystCenterAPI:
    """Cisco Catalyst Center API client"""
    
    def __init__(self, base_url: str, username: str, password: str, verify_ssl: bool = False):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.token = None
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        
        # Disable SSL warnings only if SSL verification is disabled
        if not self.verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
    def authenticate(self) -> bool:
        """Authenticate with Catalyst Center and get token"""
        auth_url = f"{self.base_url}/dna/system/api/v1/auth/token"
        
        # Create basic auth header
        credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {credentials}",
            "User-Agent": "Network-MCP-Server/1.0 pamosima"
        }
        
        try:
            response = self.session.post(auth_url, headers=headers, verify=self.verify_ssl)
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
            response = self.session.get(url, headers=headers, params=params, verify=self.verify_ssl)
            if response.status_code == 401:
                # Token expired, re-authenticate
                if self.authenticate():
                    headers = self._get_headers()
                    response = self.session.get(url, headers=headers, params=params, verify=self.verify_ssl)
            
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
            response = self.session.post(url, headers=headers, json=data, verify=self.verify_ssl)
            if response.status_code == 401:
                # Token expired, re-authenticate
                if self.authenticate():
                    headers = self._get_headers()
                    response = self.session.post(url, headers=headers, json=data, verify=self.verify_ssl)
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ API Error: {e}")
            raise

# Initialize API client
catc_api = CatalystCenterAPI(CATC_URL, CATC_USERNAME, CATC_PASSWORD, verify_ssl=CATC_VERIFY_SSL)

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
def get_assurance_issues(
    priority: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    issue_id: Optional[str] = None,
    network_device_id: Optional[str] = None,
    site_id: Optional[str] = None,
    category: Optional[str] = None,
    device_type: Optional[str] = None,
    name: Optional[str] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    limit: int = 25,
    offset: int = 1,
    is_global: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Get detailed assurance issues from Catalyst Center
    
    Returns all details of each issue along with suggested actions for given set of filters.
    Supports wildcard search (*) for string parameters.
    Reference: https://developer.cisco.com/docs/dna-center/2-3-7-9/issues-get-the-details-of-issues-for-given-set-of-filters/
    
    Args:
        priority: Priority filter (P1, P2, P3, P4). Examples: 'P1' or 'P1&priority=P2'
        status: Status filter (active, resolved). Examples: 'active' or 'active&status=resolved'
        severity: Severity filter (high, medium, low)
        issue_id: Specific issue ID to retrieve
        network_device_id: Network device UUID to filter issues by device
        site_id: Site ID/UUID to filter issues by site
        category: Issue category (availability, onboarding, performance, connectivity, etc.)
        device_type: Device type (Wireless Controller, Switches and Hubs, Routers, etc.)
        name: Issue name (supports wildcard *)
        start_time: Start time in UNIX epoch milliseconds (inclusive)
        end_time: End time in UNIX epoch milliseconds (inclusive)
        limit: Maximum number of issues to return (default: 25)
        offset: Starting point within all records, 1-based (default: 1)
        is_global: If True, only global issues. If False, all issues. If None, not filtered.
    
    Returns:
        Dict containing detailed assurance issue information with suggested actions
    """
    # Build the full URL for the data API endpoint
    url = f"{catc_api.base_url}/dna/data/api/v1/assuranceIssues"
    headers = catc_api._get_headers()
    
    # Build query parameters according to API spec
    params = {
        "limit": limit,
        "offset": offset
    }
    
    if priority:
        params['priority'] = priority
    if status:
        params['status'] = status
    if severity:
        params['severity'] = severity
    if issue_id:
        params['issueId'] = issue_id
    if network_device_id:
        params['networkDeviceId'] = network_device_id
    if site_id:
        params['siteId'] = site_id
    if category:
        params['category'] = category
    if device_type:
        params['deviceType'] = device_type
    if name:
        params['name'] = name
    if start_time:
        params['startTime'] = start_time
    if end_time:
        params['endTime'] = end_time
    if is_global is not None:
        params['isGlobal'] = str(is_global).lower()
    
    try:
        response = catc_api.session.get(url, headers=headers, params=params, verify=catc_api.verify_ssl)
        if response.status_code == 401:
            # Token expired, re-authenticate
            if catc_api.authenticate():
                headers = catc_api._get_headers()
                response = catc_api.session.get(url, headers=headers, params=params, verify=catc_api.verify_ssl)
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ API Error: {e}")
        raise

@mcp.tool()
def resolve_issues(issue_ids: List[str]) -> Dict[str, Any]:
    """
    Resolve the given list of issues in Catalyst Center
    
    This tool marks one or more issues as resolved in Catalyst Center.
    You can get issue IDs from the get_assurance_issues tool.
    Reference: https://developer.cisco.com/docs/dna-center/resolve-the-given-lists-of-issues/
    
    Args:
        issue_ids: List of issue IDs to resolve (e.g., ['issue-uuid-1', 'issue-uuid-2'])
    
    Returns:
        Dict containing the resolution operation result
    
    Example:
        # First, get issues to find their IDs
        issues = get_assurance_issues(status="active", priority="P1")
        issue_ids = [issue['issueId'] for issue in issues['response']]
        
        # Then resolve specific issues
        result = resolve_issues(issue_ids=issue_ids)
    """
    if not issue_ids or len(issue_ids) == 0:
        return {
            "error": "No issue IDs provided",
            "message": "Please provide at least one issue ID to resolve"
        }
    
    # Build the full URL for the resolve endpoint
    url = f"{catc_api.base_url}/dna/intent/api/v1/assuranceIssues/resolve"
    headers = catc_api._get_headers()
    
    # Build the request payload - Catalyst Center expects an array of issue IDs
    payload = {
        "issueIds": issue_ids
    }
    
    try:
        response = catc_api.session.post(url, headers=headers, json=payload, verify=catc_api.verify_ssl)
        if response.status_code == 401:
            # Token expired, re-authenticate
            if catc_api.authenticate():
                headers = catc_api._get_headers()
                response = catc_api.session.post(url, headers=headers, json=payload, verify=catc_api.verify_ssl)
        
        response.raise_for_status()
        result = response.json()
        
        # Extract successful and failed issue IDs from response
        successful_ids = result.get('response', {}).get('successfulIssueIds', [])
        failed_ids = result.get('response', {}).get('failureIssueIds', [])
        
        return {
            "status": "success",
            "message": f"Resolved {len(successful_ids)} issue(s), {len(failed_ids)} failed",
            "successful_issue_ids": successful_ids,
            "failed_issue_ids": failed_ids,
            "response": result
        }
    except requests.exceptions.HTTPError as e:
        error_message = f"Failed to resolve issues: {e}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                error_message = f"Failed to resolve issues: {error_detail}"
            except:
                error_message = f"Failed to resolve issues: {e.response.text}"
        
        print(f"❌ API Error: {error_message}")
        return {
            "status": "error",
            "message": error_message,
            "issue_ids": issue_ids
        }
    except Exception as e:
        error_message = f"Unexpected error: {e}"
        print(f"❌ {error_message}")
        return {
            "status": "error",
            "message": error_message,
            "issue_ids": issue_ids
        }

if __name__ == "__main__":
    print("🚀 Starting Catalyst Center MCP Server...")
    
    # Test authentication
    if catc_api.authenticate():
        print("✅ Successfully authenticated with Catalyst Center")
    else:
        print("❌ Failed to authenticate with Catalyst Center")
        exit(1)
    
    # Start the MCP server
    mcp.run(transport="http", host=mcp_host, port=mcp_port)
