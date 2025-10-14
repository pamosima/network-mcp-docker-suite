# IOS XE MCP Server - Ultra Secure Edition

A Model Context Protocol (MCP) server for managing Cisco IOS XE devices via SSH using Netmiko with enterprise-grade security.

## Overview

This MCP server provides **ultra-secure** SSH-based management capabilities for Cisco IOS XE devices, enabling:

- **Device Configuration**: Send configuration commands to IOS XE devices
- **Monitoring Commands**: Execute show commands for device monitoring  
- **Ultra-Secure Authentication**: Environment-only credentials (no password parameters)
- **Password Protection**: Comprehensive password masking and sanitization
- **Enhanced Security**: SSH-based communication with timeout controls and error protection
- **HTTP Transport**: Modern MCP transport for network clients and LibreChat integration

## Features

### Available Tools

- **`show_command`**: Execute any show command on an IOS XE device (credentials from environment only)
- **`config_command`**: Send configuration commands to an IOS XE device (credentials from environment only)

### Security Features

- 🔐 **Environment-only credentials** - No password parameters accepted  
- 🔐 **Password masking** - Passwords masked in all logs (`C1sco12345` → `C*********`)
- 🔐 **Error sanitization** - Passwords removed from error messages (`***REDACTED***`)
- 🔐 **Startup validation** - Server fails securely if credentials missing
- ✅ **SSH timeout controls** - Configurable connection timeouts
- ✅ **Enhanced error handling** - Safe error reporting without credential exposure
- ✅ **Non-root container execution** - Minimal privilege operation
- ✅ **Automatic configuration saving** - Changes persisted automatically

## Usage Examples

**SECURITY:** All credentials are loaded from environment variables only. No password parameters are accepted for maximum security.

### Show Commands

```python
# Ultra-secure: Only host and command required (credentials from .env)
result = show_command("show version", "192.168.1.1")
result = show_command("show ip interface brief", "10.1.1.1") 
result = show_command("show ip route summary", "10.13.254.84")

# Check BGP status (real example from Leaf-2)
result = show_command("show ip bgp summary", "10.13.254.84")
result = show_command("show bgp l2vpn evpn summary", "10.13.254.84")

# Device information commands  
result = show_command("show version", "10.13.254.84")
result = show_command("show ip protocols", "192.168.1.1")
```

### Configuration Commands

```python
# Ultra-secure: Only commands and host required (credentials from .env)
result = config_command([
    "interface GigabitEthernet0/1",
    "description Connected to Server", 
    "no shutdown"
], "192.168.1.1")

# Network configuration
result = config_command([
    "ip route 10.1.0.0 255.255.0.0 192.168.1.254"
], "10.1.1.1")

# Multiple interface configuration
result = config_command([
    "interface range GigabitEthernet0/1-4",
    "switchport mode access",
    "switchport access vlan 100"
], "10.13.254.84")
```

### Security Logs Example

```log
INFO: Loaded credentials for user: netadmin
INFO: Secure mode: Credentials loaded from environment only
INFO: Connecting to 10.13.254.84 as 'netadmin' (pwd: C*********) to execute: show ip bgp summary
INFO: Successfully executed command on 10.13.254.84
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

#### Optional Advanced Settings

| Variable | Description | Example | Notes |
|----------|-------------|---------|-------|
| `SSH_TIMEOUT` | SSH connection timeout | `60` | Seconds |
| `DEFAULT_DEVICE_TYPE` | Netmiko device type | `cisco_ios` | Usually `cisco_ios` for IOS XE |

### Example .env File

```bash
# IOS XE MCP Server Configuration - Ultra Secure Edition
# =====================================================

# REQUIRED: Device credentials (server fails without these)
IOS_XE_USERNAME=netadmin
IOS_XE_PASSWORD=C1sco12345

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

### Ultra-Secure Authentication

- 🔐 **Environment-Only Credentials**: Passwords never appear in function parameters or traces
- 🔐 **Startup Validation**: Server fails securely if credentials are missing from environment  
- 🔐 **Password Masking**: All passwords masked in logs (`C1sco12345` → `C*********`)
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
INFO: Loaded credentials for user: netadmin
INFO: Secure mode: Credentials loaded from environment only
INFO: Starting SECURE IOS XE MCP server on 0.0.0.0:8003
INFO: Security: Environment-only credentials, no password parameters accepted
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

# Solution: Use new ultra-secure syntax (no credentials)
show_command("show version", "10.13.254.84")  # ✅ Correct
show_command("show version", "10.13.254.84", username="user", password="pass")  # ❌ Wrong
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
ssh netadmin@10.13.254.84
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
time ssh netadmin@10.13.254.84 "show version"
```

### Debug Logging

Enable detailed logging by setting `LOG_LEVEL=DEBUG` in environment variables.

```bash
# View detailed logs with password masking
docker-compose logs -f ios-xe-mcp-server

# Example secure log output:
# INFO: Connecting to 10.13.254.84 as 'netadmin' (pwd: C*********) to execute: show version
```

### Security Validation

```bash
# Test that password masking works
docker-compose exec ios-xe-mcp-server uv run python -c "
from ios_xe_mcp_server import mask_password
print('Password masking test:', mask_password('C1sco12345'))
"
# Output: Password masking test: C*********
```

## API Reference

### Tool: show_command

Execute a show command on an IOS XE device.

**🔐 SECURITY:** Credentials are loaded from environment variables only. No password parameters accepted.

**Parameters:**
- `command` (string): Show command to execute (e.g., `"show ip bgp summary"`)
- `host` (string): Device IP address or hostname (e.g., `"10.13.254.84"`)

**Returns:** Command output as string

**Example:**
```python
result = show_command("show version", "10.13.254.84")
```

### Tool: config_command

Send configuration commands to an IOS XE device.

**🔐 SECURITY:** Credentials are loaded from environment variables only. No password parameters accepted.

**Parameters:**
- `commands` (list): List of configuration commands to send
- `host` (string): Device IP address or hostname

**Returns:** Configuration results and save status

**Example:**
```python
result = config_command([
    "interface GigabitEthernet0/1", 
    "no shutdown"
], "10.13.254.84")
```

### Security Features

Both tools automatically:
- ✅ Load credentials from `IOS_XE_USERNAME` and `IOS_XE_PASSWORD` environment variables
- ✅ Mask passwords in logs (`C*********`)  
- ✅ Sanitize error messages (`***REDACTED***`)
- ✅ Validate environment setup on server startup
- ✅ Save configuration changes automatically

## License

This project is licensed under the Cisco Sample Code License, Version 1.1.
