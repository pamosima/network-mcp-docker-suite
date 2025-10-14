"""
NetBox MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to NetBox DCIM/IPAM functionality.
This server allows AI assistants and other MCP clients to interact with NetBox for network
documentation and infrastructure management.

Features:
- Complete CRUD operations for NetBox objects
- Device and infrastructure management
- IP address management (IPAM)
- Site and location tracking
- Circuit and provider management
- Bulk operations support

Environment Variables:
- NETBOX_URL: Required. Your NetBox instance URL
- NETBOX_TOKEN: Required. Your NetBox API token
- MCP_PORT: Optional. Port for SSE server. Defaults to 8001
- MCP_HOST: Optional. Host for SSE server. Defaults to localhost

Author: Generated for LibreChat Integration
"""

import abc
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
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    os.environ[key] = value
        
        print(f"✅ Loaded environment from {env_file}")
        return True
    except Exception as e:
        print(f"❌ Error loading .env file: {e}")
        return False

# Load .env file first
load_dotenv_file()

# Get configuration from environment
netbox_url = os.getenv("NETBOX_URL")
netbox_token = os.getenv("NETBOX_TOKEN")
sse_port = int(os.getenv("MCP_PORT", "8001"))
sse_host = os.getenv("MCP_HOST", "localhost")

# Validate required configuration
if not netbox_url:
    print("❌ NETBOX_URL not configured!")
    print("📋 Please set your NetBox URL in .env file")
    print("   Example: NETBOX_URL=https://netbox.example.com")
    exit(1)

if not netbox_token:
    print("❌ NETBOX_TOKEN not configured!")
    print("📋 Please set your NetBox API token in .env file")
    print("   Example: NETBOX_TOKEN=your_token_here")
    exit(1)

print(f"✅ NetBox URL: {netbox_url}")
print(f"✅ NetBox token configured")
print(f"🌐 SSE Server will run on: http://{sse_host}:{sse_port}")

class NetBoxClientBase(abc.ABC):
    """
    Abstract base class for NetBox client implementations.
    
    This class defines the interface for CRUD operations that can be implemented
    either via the REST API or directly via the ORM in a NetBox plugin.
    """
    
    @abc.abstractmethod
    def get(self, endpoint: str, id: Optional[int] = None, params: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Retrieve one or more objects from NetBox."""
        pass
    
    @abc.abstractmethod
    def create(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new object in NetBox."""
        pass
    
    @abc.abstractmethod
    def update(self, endpoint: str, id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing object in NetBox."""
        pass
    
    @abc.abstractmethod
    def delete(self, endpoint: str, id: int) -> bool:
        """Delete an object from NetBox."""
        pass
    
    @abc.abstractmethod
    def bulk_create(self, endpoint: str, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple objects in NetBox."""
        pass
    
    @abc.abstractmethod
    def bulk_update(self, endpoint: str, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update multiple objects in NetBox."""
        pass
    
    @abc.abstractmethod
    def bulk_delete(self, endpoint: str, ids: List[int]) -> bool:
        """Delete multiple objects from NetBox."""
        pass


class NetBoxRestClient(NetBoxClientBase):
    """NetBox client implementation using the REST API."""
    
    def __init__(self, url: str, token: str, verify_ssl: bool = True):
        """Initialize the REST API client."""
        self.base_url = url.rstrip('/')
        self.api_url = f"{self.base_url}/api"
        self.token = token
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
    
    def _build_url(self, endpoint: str, id: Optional[int] = None) -> str:
        """Build the full URL for an API request."""
        endpoint = endpoint.strip('/')
        if id is not None:
            return f"{self.api_url}/{endpoint}/{id}/"
        return f"{self.api_url}/{endpoint}/"
    
    def get(self, endpoint: str, id: Optional[int] = None, params: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Retrieve one or more objects from NetBox via the REST API."""
        url = self._build_url(endpoint, id)
        response = self.session.get(url, params=params, verify=self.verify_ssl)
        response.raise_for_status()
        
        data = response.json()
        if id is None and 'results' in data:
            return data['results']
        return data
    
    def create(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new object in NetBox via the REST API."""
        url = self._build_url(endpoint)
        response = self.session.post(url, json=data, verify=self.verify_ssl)
        response.raise_for_status()
        return response.json()
    
    def update(self, endpoint: str, id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing object in NetBox via the REST API."""
        url = self._build_url(endpoint, id)
        response = self.session.patch(url, json=data, verify=self.verify_ssl)
        response.raise_for_status()
        return response.json()
    
    def delete(self, endpoint: str, id: int) -> bool:
        """Delete an object from NetBox via the REST API."""
        url = self._build_url(endpoint, id)
        response = self.session.delete(url, verify=self.verify_ssl)
        response.raise_for_status()
        return response.status_code == 204
    
    def bulk_create(self, endpoint: str, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple objects in NetBox via the REST API."""
        url = f"{self._build_url(endpoint)}bulk/"
        response = self.session.post(url, json=data, verify=self.verify_ssl)
        response.raise_for_status()
        return response.json()
    
    def bulk_update(self, endpoint: str, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update multiple objects in NetBox via the REST API."""
        url = f"{self._build_url(endpoint)}bulk/"
        response = self.session.patch(url, json=data, verify=self.verify_ssl)
        response.raise_for_status()
        return response.json()
    
    def bulk_delete(self, endpoint: str, ids: List[int]) -> bool:
        """Delete multiple objects from NetBox via the REST API."""
        url = f"{self._build_url(endpoint)}bulk/"
        data = [{"id": id} for id in ids]
        response = self.session.delete(url, json=data, verify=self.verify_ssl)
        response.raise_for_status()
        return response.status_code == 204


# Initialize NetBox client
client = NetBoxRestClient(
    url=netbox_url,
    token=netbox_token,
    verify_ssl=True
)

print("[DEBUG] Creating comprehensive NetBox MCP server...")

# Create MCP server instance early
mcp = FastMCP("NetBox API Server")

# ---- DCIM Tools ----
@mcp.tool()
def get_sites(limit: int = 50, params: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Get sites from NetBox DCIM. Optionally filter with params."""
    try:
        query_params = {"limit": limit}
        if params:
            query_params.update(params)
        return {"success": True, "data": client.get("dcim/sites", params=query_params)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def get_site_by_id(site_id: int) -> Dict[str, Any]:
    """Get a specific site by ID."""
    try:
        return {"success": True, "data": client.get("dcim/sites", id=site_id)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def create_site(name: str, slug: str, status: str = "active", description: str = "") -> Dict[str, Any]:
    """Create a new site in NetBox."""
    try:
        site_data = {
            "name": name,
            "slug": slug,
            "status": status,
            "description": description
        }
        return {"success": True, "data": client.create("dcim/sites", site_data)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def get_devices(limit: int = 50, site_id: Optional[int] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get devices from NetBox DCIM. Optionally filter by site or other params."""
    try:
        query_params = {"limit": limit}
        if site_id:
            query_params["site_id"] = site_id
        if params:
            query_params.update(params)
        return {"success": True, "data": client.get("dcim/devices", params=query_params)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def get_device_by_id(device_id: int) -> Dict[str, Any]:
    """Get a specific device by ID."""
    try:
        return {"success": True, "data": client.get("dcim/devices", id=device_id)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def create_device(name: str, device_type_id: int, site_id: int, status: str = "active") -> Dict[str, Any]:
    """Create a new device in NetBox."""
    try:
        device_data = {
            "name": name,
            "device_type": device_type_id,
            "site": site_id,
            "status": status
        }
        return {"success": True, "data": client.create("dcim/devices", device_data)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def get_device_types(limit: int = 50, manufacturer_id: Optional[int] = None) -> Dict[str, Any]:
    """Get device types from NetBox DCIM."""
    try:
        query_params = {"limit": limit}
        if manufacturer_id:
            query_params["manufacturer_id"] = manufacturer_id
        return {"success": True, "data": client.get("dcim/device-types", params=query_params)}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ---- IPAM Tools ----
@mcp.tool()
def get_ip_addresses(limit: int = 50, vrf_id: Optional[int] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get IP addresses from NetBox IPAM."""
    try:
        query_params = {"limit": limit}
        if vrf_id:
            query_params["vrf_id"] = vrf_id
        if params:
            query_params.update(params)
        return {"success": True, "data": client.get("ipam/ip-addresses", params=query_params)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def create_ip_address(address: str, status: str = "active", description: str = "") -> Dict[str, Any]:
    """Create a new IP address in NetBox."""
    try:
        ip_data = {
            "address": address,
            "status": status,
            "description": description
        }
        return {"success": True, "data": client.create("ipam/ip-addresses", ip_data)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def get_prefixes(limit: int = 50, vrf_id: Optional[int] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get prefixes from NetBox IPAM."""
    try:
        query_params = {"limit": limit}
        if vrf_id:
            query_params["vrf_id"] = vrf_id
        if params:
            query_params.update(params)
        return {"success": True, "data": client.get("ipam/prefixes", params=query_params)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def get_vlans(limit: int = 50, site_id: Optional[int] = None) -> Dict[str, Any]:
    """Get VLANs from NetBox IPAM."""
    try:
        query_params = {"limit": limit}
        if site_id:
            query_params["site_id"] = site_id
        return {"success": True, "data": client.get("ipam/vlans", params=query_params)}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ---- Search and Query Tools ----
@mcp.tool()
def search_objects(endpoint: str, query: str, limit: int = 25) -> Dict[str, Any]:
    """Search for objects in NetBox using the 'q' parameter."""
    try:
        params = {"q": query, "limit": limit}
        return {"success": True, "data": client.get(endpoint, params=params)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def update_object(endpoint: str, object_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing object in NetBox."""
    try:
        return {"success": True, "data": client.update(endpoint, object_id, data)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def delete_object(endpoint: str, object_id: int) -> Dict[str, Any]:
    """Delete an object from NetBox."""
    try:
        success = client.delete(endpoint, object_id)
        return {"success": success, "message": f"Object {object_id} deleted" if success else "Deletion failed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# MCP server instance was created early in the file with decorators handling tool registration

# ---- Server Startup ----
if __name__ == "__main__":
    print(f"🚀 NetBox MCP Server starting...")
    print(f"🔗 NetBox URL: {netbox_url}")
    print(f"🛠️  Available tools: 14 (DCIM, IPAM, CRUD operations)")
    print(f"🌐 Server starting on: http://{sse_host}:{sse_port}")
    print(f"📡 SSE endpoint: http://{sse_host}:{sse_port}/sse")
    print(f"✅ Server ready for MCP client connections via SSE.")
    print(f"")
    print(f"📋 Available NetBox operations:")
    print(f"   🏢 DCIM: Sites, Devices, Device Types")
    print(f"   🌐 IPAM: IP Addresses, Prefixes, VLANs")
    print(f"   🔍 Search & Query: Universal search across objects")
    print(f"   ✏️  CRUD: Create, Read, Update, Delete operations")
    
    # Start the MCP server in SSE mode
    try:
        mcp.run(transport="http", host=sse_host, port=sse_port)
    except Exception as e:
        print(f"❌ Failed to start SSE server: {e}")
        print(f"💡 Trying alternative SSE startup method...")
        # Alternative method if the above doesn't work
        import uvicorn
        app = mcp.create_app()
        uvicorn.run(app, host=sse_host, port=sse_port, log_level="info")
