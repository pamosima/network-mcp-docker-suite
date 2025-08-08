"""
Meraki MCP Server

A Model Context Protocol (MCP) server that provides secure, role-based access to the Cisco Meraki Dashboard API.
This server allows AI assistants and other MCP clients to interact with Meraki networks while enforcing
proper access controls based on user roles.

Features:
- Role-based access control (NOC, SysAdmin, All)
- Automatic handling of Meraki API null values
- OpenAPI-based tool generation
- Secure API key authentication

Environment Variables:
- MERAKI_KEY: Required. Your Meraki Dashboard API key
- MCP_ROLE: Optional. Role for access control (noc|sysadmin|all). Defaults to 'noc'

Author: Kareem Iskander
"""

import httpx
import os
import json
import jsonschema
from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap, MCPType
from fastmcp.server.openapi import OpenAPITool

# ---- Environment Variables ----
api_key = os.getenv("MERAKI_KEY")


# Create an HTTP client for Meraki API
client = httpx.AsyncClient(
    base_url="https://api.meraki.com/api/v1",
    headers={"Authorization": f"Bearer {api_key}"}
)

# ---- Validation Patching ----
# Store original validate method for potential restoration
_original_validate = jsonschema.validate

# ---- Role-Based Route Configurations ----

# NOC (Network Operations Center) role routes
# Limited access for monitoring and basic firmware management
noc_routes = [
    RouteMap(methods=["GET"], pattern=r"^/organizations$", mcp_type=MCPType.TOOL),
    RouteMap(methods=["GET"], pattern=r"^/organizations/[^/]+/networks$", mcp_type=MCPType.TOOL),
    RouteMap(methods=["GET"], pattern=r"^/organizations/[^/]+/devices$", mcp_type=MCPType.TOOL),
    RouteMap(methods=["GET"], pattern=r"^/organizations/[^/]+/firmware/upgrades$", mcp_type=MCPType.TOOL),
    RouteMap(methods=["GET"], pattern=r"^/organizations/[^/]+/licenses/overview$", mcp_type=MCPType.TOOL),
    RouteMap(methods=["PUT"], pattern=r"^/networks/[^/]+/firmwareUpgrades$", mcp_type=MCPType.TOOL),
    # Deny all other endpoints (including PUT operations)
    RouteMap(pattern=r"^/.*", mcp_type=MCPType.EXCLUDE),
]

# SysAdmin role routes
# Read-only access for system administrators (no firmware upgrades)
sysadmin_routes = [
    # Organization and network discovery
    RouteMap(methods=["GET"], pattern=r"^/organizations$", mcp_type=MCPType.TOOL),
    RouteMap(methods=["GET"], pattern=r"^/organizations/[^/]+/networks$", mcp_type=MCPType.TOOL),
    RouteMap(methods=["GET"], pattern=r"^/organizations/[^/]+/devices$", mcp_type=MCPType.TOOL),
    RouteMap(methods=["GET"], pattern=r"^/organizations/[^/]+/licenses/overview$", mcp_type=MCPType.TOOL),
    RouteMap(methods=["GET"], pattern=r"^/organizations/[^/]+/firmware/upgrades$", mcp_type=MCPType.TOOL),
    RouteMap(pattern=r"^/.*", mcp_type=MCPType.EXCLUDE),
]

# Firehose role routes
# Full API access - no restrictions (empty list means allow all)
firehose_routes = []


def patched_validate(*args, **kwargs):
    """
    Patched validation function that skips all JSON schema validation.
    
    This function replaces jsonschema.validate to prevent validation errors
    when Meraki API returns null values for fields that the OpenAPI schema
    expects to be strings. The original validation would fail with:
    "Output validation error: None is not of type 'string'"
    
    By disabling validation entirely, we allow the MCP server to process
    Meraki API responses that contain null values without throwing errors.
    
    Args:
        *args: All positional arguments (ignored)
        **kwargs: All keyword arguments (ignored)
        
    Returns:
        None: Always returns None, effectively disabling validation
    """
    return None

# ---- Apply Validation Patches ----
# Replace jsonschema.validate globally to prevent Meraki API null value errors
jsonschema.validate = patched_validate

# Also patch the OpenAPITool class validation if it exists
if hasattr(OpenAPITool, 'validate_output'):
    OpenAPITool.validate_output = lambda self, *args, **kwargs: None

# ---- MCP Server Configuration ----

# Load the Meraki OpenAPI specification
# This file contains the complete API schema for all Meraki Dashboard endpoints
with open("openapi/spec3.json", "r") as f:
    openapi_spec = json.load(f)

# ---- Role Selection Logic ----
# Determine which route configuration to use based on MCP_ROLE environment variable
role = os.getenv("MCP_ROLE", "noc").lower()  # Default to "noc" if not set

if role == "sysadmin":
    selected_routes = sysadmin_routes
    print(f"Starting Meraki MCP Server in SysAdmin mode (read-only access)")
elif role == "all":
    selected_routes = firehose_routes
    print(f"Starting Meraki MCP Server in Firehose mode (full API access)")
else:
    selected_routes = noc_routes
    print(f"Starting Meraki MCP Server in NOC mode (limited operational access)")

# ---- MCP Server Creation ----
# Create the FastMCP server with OpenAPI specification and role-based routing
mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name="Meraki API Server",
    timeout=30,  # Set a timeout for API requests to prevent hanging
    route_maps=selected_routes
)

# ---- Server Startup ----
if __name__ == "__main__":
    print(f"Meraki MCP Server starting...")
    print(f"API Base URL: {client.base_url}")
    print(f"Role: {role.upper()}")
    print(f"Available endpoints: {len([r for r in selected_routes if r.mcp_type == MCPType.TOOL])}")
    print(f"Server ready for MCP client connections.")
    
    # Start the MCP server
    mcp.run()
