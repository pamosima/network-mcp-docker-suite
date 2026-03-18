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
- MCP_PORT: Optional. Port for MCP server. Defaults to 8001
- MCP_HOST: Optional. Host for MCP server. Defaults to localhost

Author: Patrick Mosimann
"""

import abc
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
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
netbox_verify_ssl = os.getenv("NETBOX_VERIFY_SSL", "true").lower() in ("true", "1", "yes")
mcp_port = int(os.getenv("MCP_PORT", "8001"))
mcp_host = os.getenv("MCP_HOST", "localhost")

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
print(f"🔒 SSL verification: {'enabled' if netbox_verify_ssl else 'disabled'}")
print(f"🌐 MCP Server will run on: http://{mcp_host}:{mcp_port}")

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
    verify_ssl=netbox_verify_ssl
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
def create_device(name: str, device_type_id: int, site_id: int, role_id: int, status: str = "active", location_id: Optional[int] = None, serial: Optional[str] = None) -> Dict[str, Any]:
    """Create a new device in NetBox."""
    try:
        device_data = {
            "name": name,
            "device_type": device_type_id,
            "site": site_id,
            "role": role_id,
            "status": status
        }
        if location_id:
            device_data["location"] = location_id
        if serial:
            device_data["serial"] = serial
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

@mcp.tool()
def get_device_roles(limit: int = 50) -> Dict[str, Any]:
    """Get device roles from NetBox DCIM."""
    try:
        query_params = {"limit": limit}
        return {"success": True, "data": client.get("dcim/device-roles", params=query_params)}
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

# ---- Custom Scripts Tools ----
@mcp.tool()
def get_object_choices(endpoint: str, limit: int = 50) -> Dict[str, Any]:
    """
    Get a list of available objects for selection (for ObjectVar parameters).
    
    This tool shows ALL available options for object selection, making it easy
    to pick the right one without guessing names. Much better UX than searching!
    
    Use this to show users what tenants, regions, sites, etc. are available
    before asking them to choose.
    
    Args:
        endpoint: NetBox API endpoint (e.g., "dcim/tenants", "dcim/regions", "dcim/sites")
        limit: Maximum number of objects to return (default: 50)
    
    Returns:
        Dict with list of available objects with their IDs and names
    
    Example:
        # Show all available tenants
        tenants = get_object_choices("dcim/tenants")
        # Display to user: "1: Acme Corp, 2: TechCo, 3: GlobalNet"
        # User picks: "Acme Corp"
        # Use ID: 1
        
        # Show all available regions
        regions = get_object_choices("dcim/regions")
        # Display: "1: North America, 2: Europe, 3: Asia Pacific"
        
        # Show all sites
        sites = get_object_choices("dcim/sites")
    """
    try:
        params = {"limit": limit}
        results = client.get(endpoint, params=params)
        
        # Handle both list and dict responses
        if isinstance(results, list):
            objects = results
        elif isinstance(results, dict) and 'results' in results:
            objects = results['results']
        else:
            objects = []
        
        # Extract relevant fields for selection
        choices = []
        for obj in objects:
            choice = {
                "id": obj.get("id"),
                "name": obj.get("name") or obj.get("display"),
                "display": obj.get("display"),
                "description": obj.get("description", ""),
            }
            choices.append(choice)
        
        return {
            "success": True,
            "endpoint": endpoint,
            "count": len(choices),
            "choices": choices,
            "message": f"Found {len(choices)} available options. User can select by name or ID."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def get_script_job_status(job_id: int) -> Dict[str, Any]:
    """
    Get the status and results of a custom script execution job.
    
    After executing a custom script, use this to check if it completed successfully,
    retrieve output logs, and see any errors that occurred.
    
    Args:
        job_id: The job ID returned from execute_custom_script()
    
    Returns:
        Dict with job status, completion state, logs, and results
    
    Example:
        # Check if script completed
        status = get_script_job_status(job_id=42)
        print(status["data"]["status"])  # completed, pending, running, failed
    """
    try:
        job = client.get("core/jobs", id=job_id)
        return {
            "success": True,
            "data": job,
            "status": job.get("status", {}).get("value") if isinstance(job, dict) else None,
            "completed": job.get("completed") if isinstance(job, dict) else None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def list_script_jobs(limit: int = 50, script_name: Optional[str] = None) -> Dict[str, Any]:
    """
    List recent custom script execution jobs.
    
    View history of script executions, their status, and when they ran.
    Useful for tracking automation workflows and troubleshooting failures.
    
    Args:
        limit: Maximum number of jobs to return (default: 50)
        script_name: Optional filter by specific script name
    
    Returns:
        Dict with list of recent script execution jobs
    """
    try:
        params = {"limit": limit, "object_type": "extras.script"}
        if script_name:
            params["name"] = script_name
        
        jobs = client.get("core/jobs", params=params)
        return {"success": True, "data": jobs}
    except Exception as e:
        return {"success": False, "error": str(e)}

# MCP server instance was created early in the file with decorators handling tool registration

# ---- Dynamic Custom Script Tool Registration ----
def register_custom_scripts_as_tools():
    """
    Fetch NetBox custom scripts at startup and register each as a dynamic MCP tool.
    
    This transforms each custom script into a first-class MCP tool, making them
    immediately discoverable and usable by AI agents without multi-step workflows.
    
    Example:
        Instead of: find_custom_script() → get_script_variables() → execute_custom_script()
        Agent sees: create_site_and_locations(tenant_id, region_id, site_name, ...)
    """
    try:
        print("🔄 Fetching custom scripts from NetBox...")
        response = client.get("extras/scripts")
        
        # Parse response
        if isinstance(response, list):
            scripts = response
        elif isinstance(response, dict) and 'results' in response:
            scripts = response['results']
        else:
            print("⚠️  No custom scripts found")
            return 0
        
        registered_count = 0
        
        for script in scripts:
            if not script.get("is_executable"):
                continue
                
            script_id = script["id"]
            script_name = script["name"]
            script_description = script.get("description", f"NetBox custom script: {script_name}")
            script_vars = script.get("vars", {})
            
            # Convert script name to valid Python function name
            # "CreateSiteAndLocations" → "create_site_and_locations"
            tool_name = _to_snake_case(script_name)
            
            # Create the dynamic tool function
            dynamic_tool = _create_script_tool(
                script_id=script_id,
                script_name=script_name,
                tool_name=tool_name,
                description=script_description,
                variables=script_vars
            )
            
            # Register the tool with FastMCP
            mcp.tool()(dynamic_tool)
            
            registered_count += 1
            print(f"   ✅ Registered: {tool_name}()")
        
        print(f"✨ Registered {registered_count} custom scripts as dynamic tools")
        return registered_count
        
    except Exception as e:
        print(f"⚠️  Warning: Could not register custom scripts as tools: {e}")
        print(f"   Custom scripts can still be used via execute_custom_script()")
        return 0


def _to_snake_case(name: str) -> str:
    """Convert CamelCase or PascalCase to snake_case."""
    import re
    # Insert underscore before uppercase letters
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # Insert underscore before uppercase letters that follow lowercase
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()


def _create_script_tool(script_id: int, script_name: str, tool_name: str, 
                        description: str, variables: Dict[str, str]):
    """
    Create a dynamic tool function for a custom script with explicit parameters.
    
    FastMCP requires explicit parameters (not **kwargs), so we generate the function
    dynamically using exec() with the correct signature.
    
    Generates intelligent parameter descriptions based on variable names and types.
    """
    # Build parameter list and documentation
    param_list = []
    param_docs = []
    type_hints = {}
    
    for var_name, var_type in variables.items():
        # Generate intelligent description from variable name
        var_label = var_name.replace('_', ' ').title()
        
        if var_type == "ObjectVar":
            endpoint = _guess_endpoint_from_var_name(var_name)
            param_list.append(f"{var_name}: int")
            param_docs.append(
                f"        {var_name} (int): {var_label} ID. "
                f"Use get_object_choices('{endpoint}') to see available options."
            )
            type_hints[var_name] = int
        elif var_type == "StringVar":
            param_list.append(f"{var_name}: str")
            param_docs.append(f"        {var_name} (str): {var_label} as text")
            type_hints[var_name] = str
        elif var_type == "IntegerVar":
            param_list.append(f"{var_name}: int")
            param_docs.append(f"        {var_name} (int): {var_label} as integer")
            type_hints[var_name] = int
        elif var_type == "BooleanVar":
            param_list.append(f"{var_name}: bool")
            param_docs.append(f"        {var_name} (bool): {var_label} as boolean")
            type_hints[var_name] = bool
        else:
            param_list.append(f"{var_name}")
            param_docs.append(
                f"        {var_name}: {var_label}"
            )
    
    param_signature = ", ".join(param_list) if param_list else ""
    param_doc_str = "\n".join(param_docs) if param_docs else "        (no parameters)"
    
    # Build the docstring
    docstring = f'''"""{description}

NetBox Custom Script: {script_name}
Script ID: {script_id}

Parameters:
{param_doc_str}

Returns:
    Dict with execution result and job information

Example:
    # This is a dynamically generated tool from NetBox custom script
    result = {tool_name}(...)
"""'''
    
    # Create parameter names for kwargs dict
    param_names = list(variables.keys())
    param_dict_items = ", ".join([f'"{name}": {name}' for name in param_names])
    
    # Generate the function code dynamically
    func_code = f'''
def {tool_name}({param_signature}) -> Dict[str, Any]:
    {docstring}
    try:
        data = {{{param_dict_items}}} if {bool(param_names)} else {{}}
        payload = {{
            "data": data,
            "commit": True
        }}
        result = client.create(f"extras/scripts/{script_id}", payload)
        
        # Extract job information (same logic as execute_custom_script)
        job_info = None
        job_id = None
        
        if isinstance(result, dict):
            # Try to get job info from result structure
            if "result" in result and isinstance(result["result"], dict):
                job_info = result["result"]
                if "id" in job_info:
                    job_id = job_info.get("id")
                elif "url" in job_info:
                    # Extract ID from URL as fallback
                    job_url = job_info.get("url", "")
                    job_id = job_url.split("/")[-2] if "/" in job_url else None
            elif "job" in result:
                job_info = result["job"]
                job_id = job_info.get("id") if isinstance(job_info, dict) else None
            elif "id" in result:
                job_id = result.get("id")
        
        return {{
            "success": True,
            "script_id": {script_id},
            "script_name": "{script_name}",
            "job_id": job_id,
            "job_info": job_info,
            "result": result,
            "message": f"Script '{script_name}' executed successfully. Use get_script_job_status('{{job_id}}') to check status."
        }}
    except Exception as e:
        return {{
            "success": False,
            "error": str(e),
            "script_id": {script_id},
            "script_name": "{script_name}"
        }}
'''
    
    # Execute the function definition
    namespace = {
        "Dict": Dict,
        "Any": Any,
        "client": client,
    }
    exec(func_code, namespace)
    
    return namespace[tool_name]


def _guess_endpoint_from_var_name(var_name: str) -> str:
    """Guess the NetBox API endpoint from a variable name."""
    # Common mappings
    endpoint_map = {
        "tenant": "tenancy/tenants",
        "region": "dcim/regions",
        "site": "dcim/sites",
        "location": "dcim/locations",
        "device": "dcim/devices",
        "device_type": "dcim/device-types",
        "device_role": "dcim/device-roles",
        "rack": "dcim/racks",
        "vlan": "ipam/vlans",
        "vrf": "ipam/vrfs",
        "prefix": "ipam/prefixes",
        "ip_address": "ipam/ip-addresses",
        "interface": "dcim/interfaces",
        "cable": "dcim/cables",
        "circuit": "circuits/circuits",
        "provider": "circuits/providers",
    }
    
    var_lower = var_name.lower()
    
    # Check for exact matches first
    if var_lower in endpoint_map:
        return endpoint_map[var_lower]
    
    # Check for partial matches
    for key, endpoint in endpoint_map.items():
        if key in var_lower:
            return endpoint
    
    # Default fallback
    return f"dcim/{var_name.lower()}s"


# ---- Server Startup ----
if __name__ == "__main__":
    print(f"🚀 NetBox MCP Server starting...")
    print(f"🔗 NetBox URL: {netbox_url}")
    
    # Register custom scripts as dynamic tools
    dynamic_tools_count = register_custom_scripts_as_tools()
    
    # Calculate total tools (17 base tools + dynamic custom script tools)
    # Base tools: 8 DCIM + 4 IPAM + 4 Search/CRUD + 3 Script Utilities = 19 base tools
    total_tools = 19 + dynamic_tools_count
    
    print(f"🛠️  Available tools: {total_tools} ({dynamic_tools_count} dynamic custom scripts + 19 base tools)")
    print(f"🌐 Server starting on: http://{mcp_host}:{mcp_port}")
    print(f"🔗 HTTP endpoint: http://{mcp_host}:{mcp_port}")
    print(f"✅ Server ready for MCP client connections via HTTP.")
    print(f"")
    print(f"📋 Available NetBox operations:")
    print(f"   🏢 DCIM: Sites, Devices, Device Types")
    print(f"   🌐 IPAM: IP Addresses, Prefixes, VLANs")
    print(f"   🔍 Search & Query: Universal search across objects")
    print(f"   ✏️  CRUD: Create, Read, Update, Delete operations")
    print(f"   🔧 Custom Scripts: {dynamic_tools_count} dynamically registered + 3 utility tools")
    
    # Start the MCP server in HTTP mode
    try:
        mcp.run(transport="http", host=mcp_host, port=mcp_port)
    except Exception as e:
        print(f"❌ Failed to start HTTP server: {e}")
        print(f"💡 Trying alternative HTTP startup method...")
        # Alternative method if the above doesn't work
        import uvicorn
        app = mcp.create_app()
        uvicorn.run(app, host=mcp_host, port=mcp_port, log_level="info")
