# IOS XE MCP Server for LibreChat integration
# ============================================
# MCP Server implementation for Cisco IOS XE device management
# Provides SSH-based device configuration and monitoring capabilities

from fastmcp import FastMCP
from netmiko import ConnectHandler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define MCP Server
mcp = FastMCP("ios-xe-mcp-server")

@mcp.tool()
def show_command(host: str, username: str, password: str, command: str) -> str:
    """
    Executes a 'show' command via SSH (Netmiko) on an IOS XE device.
    
    Args:
        host: IP address or hostname of the IOS XE device
        username: SSH login username
        password: SSH login password  
        command: Show command to execute (e.g., 'show ip interface brief')
        
    Returns:
        Command output as string or error message
    """
    device = {
        "device_type": "cisco_ios",
        "host": host,
        "username": username,
        "password": password,
        "timeout": 60,
        "session_timeout": 60,
    }

    try:
        logger.info(f"Connecting to {host} to execute: {command}")
        with ConnectHandler(**device) as conn:
            output = conn.send_command(command)
        logger.info(f"Successfully executed command on {host}")
        return output
    except Exception as e:
        error_msg = f"Error executing command on {host}: {e}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def config_command(host: str, username: str, password: str, commands: list[str]) -> str:
    """
    Sends configuration commands via SSH (Netmiko) to an IOS XE device.
    
    Args:
        host: IP address or hostname of the IOS XE device
        username: SSH login username
        password: SSH login password
        commands: List of configuration commands (e.g., ['interface gi0/1', 'no shutdown'])
        
    Returns:
        Configuration result as string or error message
    """
    device = {
        "device_type": "cisco_ios",
        "host": host,
        "username": username,
        "password": password,
        "timeout": 60,
        "session_timeout": 60,
    }

    try:
        logger.info(f"Connecting to {host} to apply {len(commands)} configuration commands")
        with ConnectHandler(**device) as conn:
            # Enter configuration mode and send commands
            output = conn.send_config_set(commands)
            # Save configuration
            save_output = conn.send_command("write memory")
        
        result = f"Configuration successfully applied to {host}:\n{output}\n\nSave result:\n{save_output}"
        logger.info(f"Successfully applied configuration to {host}")
        return result
    except Exception as e:
        error_msg = f"Error during configuration on {host}: {e}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def show_version(host: str, username: str, password: str) -> str:
    """
    Retrieves version information from an IOS XE device.
    
    Args:
        host: IP address or hostname of the IOS XE device
        username: SSH login username
        password: SSH login password
        
    Returns:
        Version information as string or error message
    """
    return show_command(host, username, password, "show version")

@mcp.tool()
def show_interfaces(host: str, username: str, password: str) -> str:
    """
    Retrieves interface status from an IOS XE device.
    
    Args:
        host: IP address or hostname of the IOS XE device
        username: SSH login username
        password: SSH login password
        
    Returns:
        Interface information as string or error message
    """
    return show_command(host, username, password, "show ip interface brief")

@mcp.tool()
def show_routing_table(host: str, username: str, password: str) -> str:
    """
    Retrieves routing table from an IOS XE device.
    
    Args:
        host: IP address or hostname of the IOS XE device
        username: SSH login username  
        password: SSH login password
        
    Returns:
        Routing table as string or error message
    """
    return show_command(host, username, password, "show ip route")

@mcp.tool()
def show_running_config(host: str, username: str, password: str) -> str:
    """
    Retrieves running configuration from an IOS XE device.
    
    Args:
        host: IP address or hostname of the IOS XE device
        username: SSH login username
        password: SSH login password
        
    Returns:
        Running configuration as string or error message
    """
    return show_command(host, username, password, "show running-config")

# Start Server (SSE Mode for LibreChat integration)
if __name__ == "__main__":
    import os
    
    # Get configuration from environment
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8003"))
    
    logger.info(f"Starting IOS XE MCP server on {host}:{port}")
    mcp.run(transport="sse", host=host, port=port)
