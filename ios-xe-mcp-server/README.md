# IOS XE MCP Server

A Model Context Protocol (MCP) server for managing Cisco IOS XE devices via SSH using Netmiko with enterprise-grade security.

## Overview

This MCP server provides **secure** SSH-based management capabilities for Cisco IOS XE devices, enabling:

- **Device Configuration**: Send configuration commands to IOS XE devices
- **Monitoring Commands**: Execute show commands for device monitoring  
- **Secure Authentication**: Environment-only credentials (no password parameters)
- **Password Protection**: Comprehensive password masking and sanitization
- **Enhanced Security**: SSH-based communication with timeout controls and error protection
- **HTTP Transport**: Modern MCP transport for MCP clients (Cursor, LibreChat, etc.)

## Features

### Available Tools

- **`show_command`**: Execute any show command on an IOS XE device (credentials from environment only)
- **`config_command`**: Send configuration commands to an IOS XE device (only available when `IOS_XE_READ_ONLY=false`)

### Read-Only Mode

For monitoring and troubleshooting workflows, you can enable **read-only mode** which only exposes the `show_command` tool:

```bash
# In .env
IOS_XE_READ_ONLY=true    # Only show commands available (recommended for AI troubleshooting)
IOS_XE_READ_ONLY=false   # Both show and config commands (default)
```

| Mode | `IOS_XE_READ_ONLY` | Available Tools |
|------|---------------------|-----------------|
| **Read-Only** | `true` | `show_command` only |
| **Read-Write** | `false` (default) | `show_command` + `config_command` |

**Use Cases:**
- **netops-stack troubleshooting:** Set `IOS_XE_READ_ONLY=true` - AI can only run show commands
- **Configuration automation:** Set `IOS_XE_READ_ONLY=false` - AI can push configs

### Security Features

- 🔐 **Environment-only credentials** - No password parameters accepted  
- 🔐 **Enable mode support** - Automatic privilege escalation with `IOS_XE_ENABLE_SECRET`
- 🔐 **Read-only mode** - Disable config commands for safe monitoring (`IOS_XE_READ_ONLY=true`)
- 🔐 **Password masking** - Passwords and secrets masked in all logs (`your_default_password` → `y*********`)
- 🔐 **Error sanitization** - Passwords and secrets removed from error messages (`***REDACTED***`)
- 🔐 **Startup validation** - Server fails securely if credentials missing
- ✅ **SSH timeout controls** - Configurable connection timeouts
- ✅ **Enhanced error handling** - Safe error reporting without credential exposure
- ✅ **Non-root container execution** - Minimal privilege operation
- ✅ **Automatic configuration saving** - Changes persisted automatically (when not read-only)

### Enable Mode Configuration

For devices that require privilege escalation (not configured for priv 15 login):

```bash
# Device requires enable password to enter privileged exec mode
IOS_XE_ENABLE_SECRET=your_enable_password
```

**When to use:**
- Device login drops you to user exec mode (`Router>`)
- You need to type `enable` and enter a password to get `Router#`

**When NOT needed:**
- Device login goes directly to privileged exec mode (`Router#`)
- User account is configured with `privilege 15`

## Usage Examples

**SECURITY:** All credentials are loaded from environment variables only. No password parameters are accepted for maximum security.

### Show Commands

```python
# Secure: Only host and command required (credentials from .env)
result = show_command("show version", "switch.company.com")
result = show_command("show ip interface brief", "switch.company.com") 
result = show_command("show ip route summary", "switch.company.com")

# Check BGP status
result = show_command("show ip bgp summary", "switch.company.com")
result = show_command("show bgp l2vpn evpn summary", "switch.company.com")

# Device information commands  
result = show_command("show ip protocols", "switch.company.com")
result = show_command("show running-config interface gi0/1", "switch.company.com")
```

### Configuration Commands

```python
# Secure: Only commands and host required (credentials from .env)
result = config_command([
    "interface GigabitEthernet0/1",
    "description Connected to Server", 
    "no shutdown"
], "switch.company.com")

# Network configuration
result = config_command([
    "ip route 10.1.0.0 255.255.0.0 10.1.1.1"
], "switch.company.com")

# Multiple interface configuration
result = config_command([
    "interface range GigabitEthernet0/1-4",
    "switchport mode access",
    "switchport access vlan 100"
], "switch.company.com")
```

### Security Logs Example

```log
INFO: Loaded credentials for user: admin
INFO: Secure mode: Credentials loaded from environment only
INFO: Connecting to switch.company.com as 'admin' (pwd: y*********) to execute: show ip bgp summary
INFO: Successfully executed command on switch.company.com
```

## Configuration

### Environment Variables

**REQUIRED:** The server requires credentials in environment variables for security. Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
nano .env
```

#### Core Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MCP_HOST` | Server bind address | `0.0.0.0` | No |
| `MCP_PORT` | Server port | `8003` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

#### Required Security Credentials

| Variable | Description | Example | Notes |
|----------|-------------|---------|-------|
| **`IOS_XE_USERNAME`** | **SSH username** | **`admin`** | **REQUIRED - Server fails without this** |
| **`IOS_XE_PASSWORD`** | **SSH password** | **`your_default_password`** | **REQUIRED - Server fails without this** |

#### Optional Settings

| Variable | Description | Example | Notes |
|----------|-------------|---------|-------|
| `IOS_XE_ENABLE_SECRET` | Enable secret for priv 15 | `enable_password` | Leave empty if login is already priv 15 |
| `IOS_XE_READ_ONLY` | Read-only mode | `true` / `false` | `true` = show commands only (default: `false`) |
| `SSH_TIMEOUT` | SSH connection timeout | `60` | Seconds |
| `DEFAULT_DEVICE_TYPE` | Netmiko device type | `cisco_ios` | Usually `cisco_ios` for IOS XE |

### Example .env File

```bash
# IOS XE MCP Server Configuration
# =====================================================

# REQUIRED: Device credentials (server fails without these)
IOS_XE_USERNAME=admin
IOS_XE_PASSWORD=your_default_password

# Enable Secret (optional - for devices requiring privilege escalation)
IOS_XE_ENABLE_SECRET=      # Leave empty if login is already priv 15

# Read-Only Mode (recommended for monitoring/troubleshooting)
IOS_XE_READ_ONLY=false    # Set to 'true' for show commands only

# Optional: Server configuration  
MCP_HOST=0.0.0.0
MCP_PORT=8003
LOG_LEVEL=INFO
```

See `.env.example` for a comprehensive list of all available configuration options including security settings, performance tuning, and multiple device scenarios.

### Device Requirements

- Cisco IOS XE device with SSH enabled
- Valid SSH credentials (username/password)
- Network connectivity from the MCP server to the device
- SSH port (22) accessible

## Deployment

### Using Docker Compose

The server is included in the main `docker-compose.yml`:

```bash
# Start only IOS XE MCP server
docker-compose up -d ios-xe-mcp-server

# View logs
docker-compose logs -f ios-xe-mcp-server

# Stop server
docker-compose stop ios-xe-mcp-server
```

### Standalone Docker

```bash
# Build image
docker build -t ios-xe-mcp-server .

# Run container
docker run -d \
  --name ios-xe-mcp-server \
  -p 8003:8003 \
  ios-xe-mcp-server
```

### Development Mode

```bash
# Install dependencies
uv sync

# Run server directly
uv run python ios_xe_mcp_server.py
```

## Security Considerations

### Secure Authentication

- 🔐 **Environment-Only Credentials**: Passwords never appear in function parameters or traces
- 🔐 **Startup Validation**: Server fails securely if credentials are missing from environment  
- 🔐 **Password Masking**: All passwords masked in logs (`your_default_password` → `y*********`)
- 🔐 **Error Sanitization**: Passwords automatically removed from error messages (`***REDACTED***`)
- 🔐 **No Credential Storage**: Device credentials loaded from environment only
- 🔐 **SSH Only**: Secure encrypted communication to devices
- 🔐 **Timeout Controls**: SSH connections have configurable timeouts

### Network Security

- Server runs on configurable port (default 8003)
- Supports Docker network isolation  
- SSH connections use standard port 22
- All device communication is encrypted
- No credentials transmitted in API calls

### Container Security

- Runs as non-root user
- Security options enabled (`no-new-privileges`)
- Resource limits configured
- Minimal attack surface
- Environment variables isolated per container

### Security Logs

All operations are logged securely without exposing credentials:

```log
# Read-Write Mode (default)
INFO: Loaded credentials for user: admin
INFO: Secure mode: Credentials loaded from environment only
INFO: ⚠️  READ-WRITE MODE: Configuration commands are available
INFO: Starting SECURE IOS XE MCP server on 0.0.0.0:8003
INFO: Mode: READ-WRITE (config enabled)

# Read-Only Mode (IOS_XE_READ_ONLY=true)
INFO: Loaded credentials for user: admin
INFO: Secure mode: Credentials loaded from environment only
INFO: 🔒 READ-ONLY MODE ENABLED: Only show commands are available
INFO: Starting SECURE IOS XE MCP server on 0.0.0.0:8003
INFO: Mode: READ-ONLY (show commands only)
```

## Troubleshooting

### Common Issues

**🔐 Environment Credential Errors**
```bash
# Server fails to start with missing credentials
ERROR: IOS_XE_USERNAME and IOS_XE_PASSWORD must be set in environment!

# Solution: Check .env file exists and has correct values
cat ios-xe-mcp-server/.env

# Verify environment variables are loaded
docker-compose exec ios-xe-mcp-server env | grep IOS_XE
```

**🔐 MCP Client Parameter Errors**  
```bash
# Error: Validation errors for call[show_command] - username/password unexpected
# This happens when using old function signatures

# Solution: Use new secure syntax (no credentials)
show_command("show version", "switch.company.com")  # ✅ Correct
show_command("show version", "switch.company.com", username="user", password="pass")  # ❌ Wrong
```

**SSH Connection Failures**
```bash
# Check network connectivity
ping <device-ip>

# Verify SSH service
telnet <device-ip> 22

# Check device SSH configuration
show ip ssh

# Verify credentials work manually
ssh admin@switch.company.com
```

**Authentication Errors**
```bash
# Check if credentials in .env match device
# Look for sanitized error messages (passwords are hidden)
Authentication to device failed.
Common causes:
1. Invalid credentials in environment
2. Device SSH configuration  
3. Network connectivity
```

**Timeout Issues**
```bash
# Increase timeout in environment variables
SSH_TIMEOUT=120

# Or check device response time
time ssh admin@switch.company.com "show version"
```

### Debug Logging

Enable detailed logging by setting `LOG_LEVEL=DEBUG` in environment variables.

```bash
# View detailed logs with password masking
docker-compose logs -f ios-xe-mcp-server

# Example secure log output:
# INFO: Connecting to switch.company.com as 'admin' (pwd: y*********) to execute: show version
```

### Security Validation

```bash
# Test that password masking works
docker-compose exec ios-xe-mcp-server uv run python -c "
from ios_xe_mcp_server import mask_password
print('Password masking test:', mask_password('your_default_password'))
"
# Output: Password masking test: y*********
```

## API Reference

### Tool: show_command

Execute a show command on an IOS XE device.

**🔐 SECURITY:** Credentials are loaded from environment variables only. No password parameters accepted.

**Parameters:**
- `command` (string): Show command to execute (e.g., `"show ip bgp summary"`)
- `host` (string): Device IP address or hostname (e.g., `"switch.company.com"`)

**Returns:** Command output as string

**Example:**
```python
result = show_command("show version", "switch.company.com")
```

### Tool: config_command

Send configuration commands to an IOS XE device.

**🔐 SECURITY:** Credentials are loaded from environment variables only. No password parameters accepted.

**⚠️ AVAILABILITY:** Only available when `IOS_XE_READ_ONLY=false` (default). Not registered in read-only mode.

**Parameters:**
- `commands` (list): List of configuration commands to send
- `host` (string): Device IP address or hostname

**Returns:** Configuration results and save status

**Example:**
```python
result = config_command([
    "interface GigabitEthernet0/1", 
    "no shutdown"
], "switch.company.com")
```

### Security Features

Both tools automatically:
- ✅ Load credentials from `IOS_XE_USERNAME` and `IOS_XE_PASSWORD` environment variables
- ✅ Mask passwords in logs (`y*********`)  
- ✅ Sanitize error messages (`***REDACTED***`)
- ✅ Validate environment setup on server startup
- ✅ Save configuration changes automatically

## License

This project is licensed under the Cisco Sample Code License, Version 1.1.
