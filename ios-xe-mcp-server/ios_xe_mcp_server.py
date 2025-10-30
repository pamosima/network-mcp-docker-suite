"""
Cisco IOS XE MCP Server

A Model Context Protocol (MCP) server that provides direct SSH-based management capabilities for Cisco IOS XE devices.
This server allows AI assistants and other MCP clients to execute show commands and configuration changes
on IOS XE devices through secure SSH connections with enterprise-grade security.

Features:
- Direct SSH-based device management
- Show command execution for monitoring and troubleshooting
- Configuration change deployment with automatic save
- Secure credential management (environment variables only)
- Password sanitization in logs and error messages
- Connection error handling and diagnostics
- Read and write operations with proper authentication
- HTTP transport for modern MCP client compatibility

Environment Variables:
- IOS_XE_USERNAME: Required. Default IOS XE username for device access
- IOS_XE_PASSWORD: Required. Default IOS XE password for device access
- MCP_HOST: Optional. Host for MCP server. Defaults to localhost  
- MCP_PORT: Optional. Port for MCP server. Defaults to 8003

Author: Patrick Mosimann
Based on: SSH device management concepts by tspuhler
"""

from fastmcp import FastMCP
from netmiko import ConnectHandler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load default credentials from environment
import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

DEFAULT_USERNAME = os.getenv("IOS_XE_USERNAME")
DEFAULT_PASSWORD = os.getenv("IOS_XE_PASSWORD")

# Validate environment credentials (required for secure operation)
if not DEFAULT_USERNAME or not DEFAULT_PASSWORD:
    logger.error("SECURITY ERROR: IOS_XE_USERNAME and IOS_XE_PASSWORD must be set in environment!")
    logger.error("This secure version requires credentials in .env file only.")
    raise ValueError("Missing required environment credentials")

logger.info(f"Loaded credentials for user: {DEFAULT_USERNAME}")
logger.info("Secure mode: Credentials loaded from environment only")

# Password security utilities
def sanitize_error_message(error_msg: str) -> str:
    """Remove passwords from error messages for security"""
    if DEFAULT_PASSWORD and DEFAULT_PASSWORD in error_msg:
        return error_msg.replace(DEFAULT_PASSWORD, "***REDACTED***")
    return error_msg

def mask_password(password: str) -> str:
    """Mask password for logging (show first char + asterisks)"""
    if not password:
        return "None"
    if len(password) <= 2:
        return "*" * len(password)
    return password[0] + "*" * (len(password) - 1)

def create_safe_device_dict(host: str, username: str, password: str) -> dict:
    """Create device connection dict with password handling"""
    return {
        "device_type": "cisco_ios",
        "host": host,
        "username": username,
        "password": password,
        "timeout": 60,
        "session_timeout": 60,
    }

def log_connection_attempt(host: str, command: str = None):
    """Safely log connection attempts without exposing passwords"""
    masked_pwd = mask_password(DEFAULT_PASSWORD)
    if command:
        logger.info(f"Connecting to {host} as '{DEFAULT_USERNAME}' (pwd: {masked_pwd}) to execute: {command}")
    else:
        logger.info(f"Connecting to {host} as '{DEFAULT_USERNAME}' (pwd: {masked_pwd}) for configuration")

# Define MCP Server
mcp = FastMCP("ios-xe-mcp-server")

@mcp.tool()
def show_command(command: str, host: str) -> str:
    """
    Executes a 'show' command via SSH (Netmiko) on an IOS XE device.
    
    SECURITY: Credentials are loaded from environment variables only.
    No password parameters accepted to prevent exposure in logs/traces.
    
    Args:
        command: Show command to execute (e.g., 'show ip interface brief')
        host: IP address or hostname of the IOS XE device
        
    Returns:
        Command output as string or error message
    """
    # Validate required parameters
    if not host:
        return "Error: host parameter is required"
    
    # Create device connection dictionary
    device = create_safe_device_dict(host, DEFAULT_USERNAME, DEFAULT_PASSWORD)

    try:
        # Log connection attempt with masked password
        log_connection_attempt(host, command)
        
        with ConnectHandler(**device) as conn:
            output = conn.send_command(command)
        logger.info(f"Successfully executed command on {host}")
        return output
    except Exception as e:
        # Sanitize error message to remove any exposed passwords
        raw_error = f"Error executing command on {host}: {e}"
        safe_error = sanitize_error_message(raw_error)
        logger.error(safe_error)
        
        # Return helpful error context without exposing credentials
        if "Authentication" in str(e) or "auth" in str(e).lower():
            return f"Authentication to device failed.\n\nCommon causes:\n1. Invalid credentials in environment\n2. Device SSH configuration\n3. Network connectivity\n\nDevice: cisco_ios {host}:22\n\n{safe_error}"
        else:
            return safe_error

@mcp.tool()
def config_command(commands: list[str], host: str) -> str:
    """
    Sends configuration commands via SSH (Netmiko) to an IOS XE device.
    
    SECURITY: Credentials are loaded from environment variables only.
    No password parameters accepted to prevent exposure in logs/traces.
    
    Args:
        commands: List of configuration commands (e.g., ['interface gi0/1', 'no shutdown'])
        host: IP address or hostname of the IOS XE device
        
    Returns:
        Configuration result as string or error message
    """
    # Validate required parameters
    if not host:
        return "Error: host parameter is required"
    if not commands or not isinstance(commands, list):
        return "Error: commands must be a non-empty list"
    
    # Create device connection dictionary  
    device = create_safe_device_dict(host, DEFAULT_USERNAME, DEFAULT_PASSWORD)

    try:
        # Log connection attempt with masked password
        log_connection_attempt(host)
        
        with ConnectHandler(**device) as conn:
            # Enter configuration mode and send commands
            output = conn.send_config_set(commands)
            # Save configuration
            save_output = conn.send_command("write memory")
        
        result = f"Configuration successfully applied to {host}:\n{output}\n\nSave result:\n{save_output}"
        logger.info(f"Successfully applied configuration to {host}")
        return result
    except Exception as e:
        # Sanitize error message to remove any exposed passwords
        raw_error = f"Error during configuration on {host}: {e}"
        safe_error = sanitize_error_message(raw_error)
        logger.error(safe_error)
        
        # Return helpful error context without exposing credentials
        if "Authentication" in str(e) or "auth" in str(e).lower():
            return f"Authentication to device failed.\n\nCommon causes:\n1. Invalid credentials in environment\n2. Device SSH configuration\n3. Network connectivity\n\nDevice: cisco_ios {host}:22\n\n{safe_error}"
        else:
            return safe_error


# Start Server (HTTP Mode for MCP client integration)
if __name__ == "__main__":
    import os
    
    # Get configuration from environment
    mcp_host = os.getenv("MCP_HOST", "0.0.0.0")
    mcp_port = int(os.getenv("MCP_PORT", "8003"))
    
    logger.info(f"Starting SECURE IOS XE MCP server on {mcp_host}:{mcp_port}")
    logger.info("Security: Environment-only credentials, no password parameters accepted")
    mcp.run(transport="http", host=mcp_host, port=mcp_port)
