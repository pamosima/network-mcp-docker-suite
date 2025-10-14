# IOS XE MCP Server

A Model Context Protocol (MCP) server for managing Cisco IOS XE devices via SSH using Netmiko.

## Overview

This MCP server provides direct SSH-based management capabilities for Cisco IOS XE devices, enabling:

- **Device Configuration**: Send configuration commands to IOS XE devices
- **Monitoring Commands**: Execute show commands for device monitoring
- **Secure Authentication**: Per-request credential handling (no stored passwords)
- **Enhanced Security**: SSH-based communication with timeout controls

## Features

### Available Tools

- **`show_command`**: Execute any show command on an IOS XE device
- **`config_command`**: Send configuration commands to an IOS XE device

### Security Features

- ✅ No stored credentials - provided per API call
- ✅ SSH timeout controls
- ✅ Error handling and logging
- ✅ Non-root container execution
- ✅ Automatic configuration saving

## Usage Examples

### Show Commands

```python
# Execute show command
result = show_command(
    host="192.168.1.1",
    username="admin",
    password="cisco123", 
    command="show version"
)

# Get interface status
result = show_command(
    host="192.168.1.1",
    username="admin",
    password="cisco123",
    command="show ip interface brief"
)

# Execute custom show command
result = show_command(
    host="192.168.1.1",
    username="admin",
    password="cisco123", 
    command="show ip route summary"
)
```

### Configuration Commands

```python
# Configure interface
result = config_command(
    host="192.168.1.1",
    username="admin",
    password="cisco123",
    commands=[
        "interface GigabitEthernet0/1",
        "description Connected to Server",
        "no shutdown"
    ]
)

# Configure routing
result = config_command(
    host="192.168.1.1",
    username="admin", 
    password="cisco123",
    commands=[
        "ip route 10.1.0.0 255.255.0.0 192.168.1.254"
    ]
)
```

## Configuration

### Environment Variables

The server supports extensive configuration through environment variables. Copy `.env.example` to `.env` and customize as needed:

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

#### Optional Device Defaults

| Variable | Description | Example | Notes |
|----------|-------------|---------|-------|
| `IOS_XE_HOST` | Default device IP | `192.168.1.1` | Used when not specified in API calls |
| `IOS_XE_USERNAME` | Default SSH username | `admin` | Used when not specified in API calls |
| `IOS_XE_PASSWORD` | Default SSH password | `cisco123` | Used when not specified in API calls |
| `SSH_TIMEOUT` | SSH connection timeout | `60` | Seconds |
| `DEFAULT_DEVICE_TYPE` | Netmiko device type | `cisco_ios` | Usually `cisco_ios` for IOS XE |

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

### Authentication Security

- **No Credential Storage**: Device credentials are never stored in the server
- **Per-Request Auth**: Each API call requires fresh credentials
- **SSH Only**: Secure encrypted communication to devices
- **Timeout Controls**: SSH connections have configurable timeouts

### Network Security

- Server runs on configurable port (default 8003)
- Supports Docker network isolation
- SSH connections use standard port 22
- All device communication is encrypted

### Container Security

- Runs as non-root user
- Security options enabled (`no-new-privileges`)
- Resource limits configured
- Minimal attack surface

## Troubleshooting

### Common Issues

**SSH Connection Failures**
```bash
# Check network connectivity
ping <device-ip>

# Verify SSH service
telnet <device-ip> 22

# Check device SSH configuration
show ip ssh
```

**Authentication Errors**
```bash
# Verify credentials on device
show users
show privilege

# Check AAA configuration if using domain authentication
show run | section aaa
```

**Timeout Issues**
```bash
# Increase timeout in device configuration
device_config = {
    "timeout": 120,
    "session_timeout": 120
}
```

### Debug Logging

Enable detailed logging by setting `LOG_LEVEL=DEBUG` in environment variables.

```bash
# View detailed logs
docker-compose logs -f ios-xe-mcp-server
```

## API Reference

### Tool: show_command

Execute a show command on an IOS XE device.

**Parameters:**
- `host` (string): Device IP address or hostname
- `username` (string): SSH username
- `password` (string): SSH password  
- `command` (string): Show command to execute

**Returns:** Command output as string

### Tool: config_command

Send configuration commands to an IOS XE device.

**Parameters:**
- `host` (string): Device IP address or hostname
- `username` (string): SSH username
- `password` (string): SSH password
- `commands` (list): Configuration commands to send

**Returns:** Configuration results and save status

## License

This project is licensed under the Cisco Sample Code License, Version 1.1.
