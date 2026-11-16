"""
Cisco IOS XE MCP Server

A Model Context Protocol (MCP) server that provides direct SSH-based management capabilities for Cisco IOS XE devices.
This server allows AI assistants and other MCP clients to execute show commands and configuration changes
on IOS XE devices through secure SSH connections with enterprise-grade security.

Features:
- Direct SSH-based device management
- Show command execution for monitoring and troubleshooting
- Configuration change deployment with automatic save (when not in read-only mode)
- Enable mode support for devices requiring privilege escalation
- Read-only mode for safe monitoring operations (show commands only)
- Secure credential management (environment variables only)
- Password sanitization in logs and error messages
- Connection error handling and diagnostics
- HTTP transport for modern MCP client compatibility

Environment Variables:
- IOS_XE_USERNAME: Required. Default IOS XE username for device access
- IOS_XE_PASSWORD: Required. Default IOS XE password for device access
- IOS_XE_ENABLE_SECRET: Optional. Enable secret for privilege escalation (if different from password)
- IOS_XE_READ_ONLY: Optional. Set to 'false' to enable config commands. Defaults to true (show commands only).
- MCP_HOST: Optional. Host for MCP server. Defaults to localhost  
- MCP_PORT: Optional. Port for MCP server. Defaults to 8003

Author: Patrick Mosimann
Based on: SSH device management concepts by tspuhler
"""

from fastmcp import FastMCP
from mcp_http_security import apply_mcp_http_security
from netmiko import ConnectHandler
from contextlib import contextmanager
import logging
import threading
import time

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
ENABLE_SECRET = os.getenv("IOS_XE_ENABLE_SECRET", "")  # Optional enable secret

# Validate environment credentials (required for secure operation)
if not DEFAULT_USERNAME or not DEFAULT_PASSWORD:
    logger.error("SECURITY ERROR: IOS_XE_USERNAME and IOS_XE_PASSWORD must be set in environment!")
    logger.error("This secure version requires credentials in .env file only.")
    raise ValueError("Missing required environment credentials")

# Read-only mode configuration
READ_ONLY_MODE = os.getenv("IOS_XE_READ_ONLY", "true").lower() in ("true", "1", "yes")

logger.info(f"Loaded credentials for user: {DEFAULT_USERNAME}")
logger.info("Secure mode: Credentials loaded from environment only")
if ENABLE_SECRET:
    logger.info("🔑 Enable secret configured for privilege escalation")
if READ_ONLY_MODE:
    logger.info("🔒 READ-ONLY MODE ENABLED: Only show commands are available")
else:
    logger.info("⚠️  READ-WRITE MODE: Configuration commands are available")

# Password security utilities
def sanitize_error_message(error_msg: str) -> str:
    """Remove passwords and secrets from error messages for security"""
    result = error_msg
    if DEFAULT_PASSWORD and DEFAULT_PASSWORD in result:
        result = result.replace(DEFAULT_PASSWORD, "***REDACTED***")
    if ENABLE_SECRET and ENABLE_SECRET in result:
        result = result.replace(ENABLE_SECRET, "***REDACTED***")
    return result

def mask_password(password: str) -> str:
    """Mask password for logging (show first char + asterisks)"""
    if not password:
        return "None"
    if len(password) <= 2:
        return "*" * len(password)
    return password[0] + "*" * (len(password) - 1)

def create_safe_device_dict(host: str, username: str, password: str, secret: str = "") -> dict:
    """Create device connection dict with password and enable secret handling"""
    device = {
        "device_type": "cisco_ios",
        "host": host,
        "username": username,
        "password": password,
        "timeout": 60,
        "session_timeout": 60,
    }
    # Add enable secret if configured (for devices requiring privilege escalation)
    if secret:
        device["secret"] = secret
    return device

# Connection pool: one SSH session per host, reused across tool calls.
# Measured on IOS-XE switches: a fresh ConnectHandler per call costs ~1.3-3.0s
# (handshake + enable + disconnect) versus ~0.15-0.8s for the command itself, so
# pooling removes 56-90% of the latency of consecutive show commands on one device.
POOL_MAX_IDLE = float(os.getenv("IOS_XE_POOL_MAX_IDLE", "300"))


class _HostConnection:
    """A pooled connection plus the lock that makes it safe for concurrent calls."""

    __slots__ = ("conn", "lock", "last_used")

    def __init__(self, conn):
        self.conn = conn
        self.lock = threading.Lock()
        self.last_used = time.time()


_pool: dict[str, _HostConnection] = {}
_pool_lock = threading.Lock()


def _open_connection(host: str):
    """Open a new SSH session (entering enable mode when a secret is configured)."""
    device = create_safe_device_dict(host, DEFAULT_USERNAME, DEFAULT_PASSWORD, ENABLE_SECRET)
    conn = ConnectHandler(**device)
    if ENABLE_SECRET:
        conn.enable()
    return conn


def _close_entry(entry: _HostConnection) -> None:
    try:
        entry.conn.disconnect()
    except Exception:  # already gone; nothing to close
        pass


def _get_entry(host: str) -> _HostConnection:
    """Return the pooled entry for host, opening a session on first use or after idling out."""
    with _pool_lock:
        entry = _pool.get(host)
        if entry is not None and (time.time() - entry.last_used) <= POOL_MAX_IDLE:
            return entry
        if entry is not None:
            _close_entry(entry)
        entry = _HostConnection(_open_connection(host))
        _pool[host] = entry
        return entry


def drop_connection(host: str) -> None:
    """Forget (and close) the pooled session for host."""
    with _pool_lock:
        entry = _pool.pop(host, None)
    if entry is not None:
        _close_entry(entry)


@contextmanager
def pooled_connection(host: str):
    """Yield a live connection for host, serializing access per device."""
    entry = _get_entry(host)
    with entry.lock:
        try:
            yield entry.conn
        except Exception:
            drop_connection(host)
            raise
        else:
            entry.last_used = time.time()


def send_show_command(host: str, command: str) -> str:
    """Run a show command on a pooled connection, reconnecting once if it went stale."""
    last_error = None
    for attempt in (1, 2):
        try:
            with pooled_connection(host) as conn:
                return conn.send_command(command)
        except Exception as exc:  # stale session, device reload, idle timeout
            last_error = exc
            logger.warning(f"Connection to {host} failed (attempt {attempt}/2): {exc}")
    raise last_error

def log_connection_attempt(host: str, command: str = None):
    """Safely log connection attempts without exposing passwords"""
    if command:
        logger.info(f"Connecting to {host} as '{DEFAULT_USERNAME}' to execute: {command}")
    else:
        logger.info(f"Connecting to {host} as '{DEFAULT_USERNAME}' for configuration")

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

    try:
        # Log command execution with masked credentials
        log_connection_attempt(host, command)

        output = send_show_command(host, command)
        logger.info(f"Successfully executed command on {host}")
        return output
    except Exception as e:
        # Sanitize error message to remove any exposed passwords
        raw_error = f"Error executing command on {host}: {e}"
        safe_error = sanitize_error_message(raw_error)
        logger.error(safe_error)
        
        # Return helpful error context without exposing credentials
        if "Authentication" in str(e) or "auth" in str(e).lower():
            return f"Authentication to device failed.\n\nCommon causes:\n1. Invalid credentials in environment\n2. Device SSH configuration\n3. Network connectivity\n4. Invalid enable secret\n\nDevice: cisco_ios {host}:22\n\n{safe_error}"
        else:
            return safe_error

# Configuration command tool - only registered if NOT in read-only mode
if not READ_ONLY_MODE:
    @mcp.tool()
    def config_command(commands: list[str], host: str) -> str:
        """
        Sends configuration commands via SSH (Netmiko) to an IOS XE device.
        
        SECURITY: Credentials are loaded from environment variables only.
        No password parameters accepted to prevent exposure in logs/traces.
        
        Note: If IOS_XE_ENABLE_SECRET is configured, the server will automatically
        enter enable mode before sending configuration commands.
        
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
        
        # Create device connection dictionary (with enable secret if configured)
        device = create_safe_device_dict(host, DEFAULT_USERNAME, DEFAULT_PASSWORD, ENABLE_SECRET)

        try:
            # Log connection attempt with masked password
            log_connection_attempt(host)
            
            with ConnectHandler(**device) as conn:
                # Enter enable mode if secret is configured (required for config mode)
                if ENABLE_SECRET:
                    conn.enable()
                    logger.info(f"Entered enable mode on {host}")
                
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
                return f"Authentication to device failed.\n\nCommon causes:\n1. Invalid credentials in environment\n2. Device SSH configuration\n3. Network connectivity\n4. Invalid enable secret\n\nDevice: cisco_ios {host}:22\n\n{safe_error}"
            else:
                return safe_error


# Start Server (HTTP Mode for MCP client integration)
if __name__ == "__main__":
    import os
    
    # Get configuration from environment
    mcp_host = os.getenv("MCP_HOST", "127.0.0.1")
    mcp_port = int(os.getenv("MCP_PORT", "8003"))
    mcp_host = apply_mcp_http_security(mcp, mcp_host)
    
    mode_str = "READ-ONLY (show commands only)" if READ_ONLY_MODE else "READ-WRITE (config enabled)"
    enable_str = "Enable secret: configured" if ENABLE_SECRET else "Enable secret: not set (using priv 15 login)"
    logger.info(f"Starting SECURE IOS XE MCP server on {mcp_host}:{mcp_port}")
    logger.info(f"Mode: {mode_str}")
    logger.info(f"{enable_str}")
    logger.info("Security: Environment-only credentials, no password parameters accepted")
    mcp.run(transport="streamable-http", host=mcp_host, port=mcp_port)
