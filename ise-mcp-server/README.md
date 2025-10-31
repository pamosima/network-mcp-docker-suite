# Cisco ISE MCP Server

> **✅ Complete Implementation**: All 18 ISE ERS API endpoints from the [original ISE_MCP specification](https://github.com/automateyournetwork/ISE_MCP/blob/main/src/ise_mcp_server/config/urls.json) are fully implemented.

A Model Context Protocol (MCP) server that provides comprehensive access to Cisco Identity Services Engine (ISE) API functionality for network access control, policy management, and security operations with enterprise-grade security.

## Overview

This MCP server provides **secure** API-based access to Cisco ISE capabilities, enabling:

- **Identity and Access Management**: User and device identity management
- **Policy Enforcement**: Authorization profiles and network access policies
- **Security Operations**: TrustSec, profiling, and compliance monitoring  
- **Session Management**: Active session monitoring and control
- **Device Management**: Network device registration and endpoint tracking
- **Guest Management**: Guest user provisioning and sponsorship
- **Read-Only Security**: All operations are read-only for maximum security
- **HTTP Transport**: Modern MCP transport for MCP clients (Cursor, LibreChat, etc.)

## Features

### Available Tools

**Identity & User Management:**
- **`ise_get_internal_users`**: List internal users configured in ISE
- **`ise_get_guest_users`**: List guest users and sponsorship information
- **`ise_get_identity_groups`**: List user identity groups for categorization
- **`ise_get_admin_users`**: List administrative users in ISE

**Device & Endpoint Management:**
- **`ise_get_endpoints`**: List endpoints (devices) known to ISE
- **`ise_get_endpoint_groups`**: List endpoint identity groups
- **`ise_search_endpoint_by_mac`**: Find specific endpoint by MAC address
- **`ise_get_device_compliance_status`**: Check device compliance status
- **`ise_get_network_devices`**: List network devices (switches, APs, etc.)

**Policy & Authorization:**
- **`ise_get_authorization_profiles`**: List authorization profiles
- **`ise_get_network_access_policies`**: List network access policy sets
- **`ise_get_profiler_profiles`**: List profiler profiles for device classification

**Security & TrustSec:**
- **`ise_get_security_groups`**: List Security Group Tags (SGTs)
- **`ise_get_sxp_connections`**: List SXP connections for IP-SGT mapping distribution ⭐ NEW
- **`ise_get_active_sessions`**: Monitor active network access sessions
- **`ise_search_user_sessions`**: Find active sessions by username

**Device Administration (TACACS+):**
- **`ise_get_tacacs_command_sets`**: List TACACS+ command sets for authorization ⭐ NEW
- **`ise_get_tacacs_profiles`**: List TACACS+ profiles for authentication ⭐ NEW

### Security Features

- 🔐 **Read-Only Operations** - No write capabilities to prevent accidental changes
- 🔐 **Environment-Only Credentials** - ISE credentials loaded from environment variables only
- 🔐 **Secure Authentication** - Uses ISE ERS API with username/password authentication
- 🔐 **SSL Configuration** - Configurable SSL verification for production environments
- ✅ **ERS API Integration** - Uses official ISE External RESTful Services API
- ✅ **Rate Limit Respect** - Built-in respect for ISE API rate limits
- ✅ **Non-root container execution** - Minimal privilege operation

## Usage Examples

**SECURITY:** All credentials are loaded from environment variables only for maximum security.

### Identity and Access Management

```python
# List all internal users
users = ise_get_internal_users()

# Find users with specific criteria
admin_users = ise_get_internal_users(filter_expression="name.CONTAINS.admin")

# List identity groups
groups = ise_get_identity_groups()

# Get guest users
guests = ise_get_guest_users(filter_expression="guestType.EQUALS.Contractor")
```

### Device and Endpoint Monitoring

```python
# List all managed endpoints
endpoints = ise_get_endpoints()

# Find device by MAC address
device = ise_search_endpoint_by_mac(mac_address="00:50:56:C0:00:01")

# Check device compliance
compliance = ise_get_device_compliance_status(mac_address="00:50:56:C0:00:01")

# List network infrastructure devices
network_devices = ise_get_network_devices()
```

### Policy and Security Analysis

```python
# List authorization profiles
auth_profiles = ise_get_authorization_profiles()

# Get network access policies
policies = ise_get_network_access_policies()

# List Security Group Tags
sgts = ise_get_security_groups()

# Monitor active sessions
active_sessions = ise_get_active_sessions()
```

### Session and Compliance Monitoring

```python
# Find sessions for specific user
user_sessions = ise_search_user_sessions(username="john.doe")

# Monitor sessions by device
device_sessions = ise_get_active_sessions(
    filter_expression="endPointMACAddress.EQUALS.00:50:56:C0:00:01"
)

# Get profiler classifications
profiles = ise_get_profiler_profiles()
```

## Configuration

### Environment Variables

**REQUIRED:** The server requires ISE credentials in environment variables for security. Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
nano .env
```

#### Core Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| **`ISE_HOST`** | **ISE server hostname or IP** | - | **✅ YES** |
| **`ISE_USERNAME`** | **ISE username with ERS API access** | - | **✅ YES** |
| **`ISE_PASSWORD`** | **ISE user password** | - | **✅ YES** |
| `ISE_VERSION` | ISE API version | `1.0` | No |
| `ISE_VERIFY_SSL` | SSL certificate verification | `False` | No |
| `MCP_HOST` | Server bind address | `localhost` | No |
| `MCP_PORT` | Server port | `8005` | No |

### ISE Prerequisites

#### 1. Enable ERS API on ISE

1. **Log into ISE Admin Portal**
2. **Navigate to**: Administration → Settings → ERS Settings
3. **Enable ERS**: Check "Enable ERS for Read/Write"
4. **Configure HTTPS**: Ensure HTTPS is enabled
5. **Save Configuration**

#### 2. Create ISE User Account

**Option A: Use Existing Admin Account**
- Ensure account has ERS API permissions

**Option B: Create Dedicated Service Account**
1. **Navigate to**: Administration → Identity Management → Internal Users
2. **Add User**: Create new user with secure password
3. **Assign Groups**: Add to "ERS Admin" or "ERS Operator" group
4. **Enable Account**: Ensure account is enabled and not expired

#### 3. Network Connectivity

- Ensure network connectivity to ISE on HTTPS (port 443)
- Verify firewall rules allow API access
- Test basic connectivity: `curl -k https://your-ise-server/ers/config/op/systemconfig/iseversion`

### Example .env File

```bash
# Cisco ISE MCP Server Configuration
# =================================

# REQUIRED: ISE server and credentials
ISE_HOST=ise.company.com
ISE_USERNAME=ise-service-account
ISE_PASSWORD=SecurePassword123!

# Optional: API and server configuration  
ISE_VERSION=1.0
ISE_VERIFY_SSL=False
MCP_HOST=localhost
MCP_PORT=8005
```

## Deployment

### Using Docker Compose

The server is included in the main `docker-compose.yml`:

```bash
# Start only ISE MCP server
docker-compose up -d ise-mcp-server

# View logs
docker-compose logs -f ise-mcp-server

# Stop server
docker-compose stop ise-mcp-server
```

### Standalone Docker

```bash
# Build image
docker build -t ise-mcp-server .

# Run container
docker run -d \
  --name ise-mcp-server \
  -p 8005:8005 \
  -e ISE_HOST=ise.company.com \
  -e ISE_USERNAME=service-account \
  -e ISE_PASSWORD=SecurePassword123! \
  ise-mcp-server
```

### Development Mode

```bash
# Install dependencies
uv sync

# Run server directly
uv run python ise_mcp_server.py
```

## Integration Examples

### Example Prompts for AI Assistants

```
"Show me all endpoints that are currently non-compliant in ISE"

"List active sessions for user john.doe and show their authorization profile"

"Find all Cisco IP phones in ISE and their current compliance status"

"Show me all guest users that were sponsored by admin@company.com this week"

"Which devices are using the 'Quarantine' authorization profile right now?"
```

### MCP Client Configuration

For **Cursor IDE**, add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "ISE-MCP-Server": {
      "transport": "http",
      "url": "http://localhost:8005/mcp",
      "timeout": 60000
    }
  }
}
```

For **LibreChat**, add to `librechat.yaml`:

```yaml
mcpServers:
  ISE-MCP-Server:
    type: streamable-http
    url: http://ise-mcp-server:8005/mcp
    timeout: 60000
```

## Security Considerations

### API Security

- 🔐 **Read-Only Access**: All tools are read-only, no write operations possible
- 🔐 **Credential Security**: ISE credentials loaded from environment only
- 🔐 **HTTPS Communication**: All ISE API communication uses HTTPS
- 🔐 **No Credential Storage**: Credentials never written to disk or logs
- 🔐 **ERS API**: Uses official ISE External RESTful Services API

### Network Security

- Server runs on configurable port (default 8005)
- Supports Docker network isolation
- All API communication is encrypted (HTTPS to ISE)
- No credentials transmitted in API responses

### Container Security

- Runs as non-root user
- Security options enabled (`no-new-privileges`)
- Resource limits configured
- Minimal attack surface
- Environment variables isolated per container

## Troubleshooting

### Common Issues

**🔐 ERS API Not Enabled**
```bash
# Error: 404 or connection refused
# Solution: Enable ERS API in ISE
# Navigate to: Administration > Settings > ERS Settings
# Enable "Enable ERS for Read/Write"
```

**🔐 Authentication Errors**
```bash
# Error: 401 Unauthorized  
# Check your ISE_USERNAME and ISE_PASSWORD
# Verify account has ERS permissions
# Test: curl -u username:password -k https://ise-host/ers/config/op/systemconfig/iseversion
```

**🌐 Network Connectivity**
```bash
# Test connectivity to ISE
curl -k https://your-ise-host/ers/config/op/systemconfig/iseversion

# Check if corporate firewall is blocking HTTPS to ISE
# Verify ISE server is reachable on port 443
```

**📊 SSL Certificate Issues**
```bash
# If you get SSL errors, set ISE_VERIFY_SSL=False
# For production, obtain valid certificates and set ISE_VERIFY_SSL=True
```

### Debug Logging

Check server logs for detailed error information:

```bash
# View server logs
docker-compose logs -f ise-mcp-server

# Check ISE API connectivity test on startup
# Look for: "✅ Successfully connected to ISE ERS API"
```

## API Reference

### Tool: ise_search_endpoint_by_mac

Search for a specific endpoint by MAC address.

**Parameters:**
- `mac_address` (str): MAC address to search for (e.g., '00:50:56:C0:00:01')

**Returns:** Endpoint information including profiling and group assignment

### Tool: ise_get_active_sessions

Get active network access sessions.

**Parameters:**
- `filter_expression` (str, optional): Filter in format 'field.OPERATION.value'
- `page` (int, optional): Page number for pagination
- `size` (int, optional): Results per page (max 100)

**Returns:** Active session data with user, device, and authorization info

### ISE Filter Operations

All filterable tools support these ISE ERS API operations:
- `EQUALS` - Exact match
- `CONTAINS` - Substring match  
- `STARTSWITH` - Prefix match
- `ENDSWITH` - Suffix match

**Example filters:**
- `name.CONTAINS.printer` - Find devices with "printer" in name
- `mac.EQUALS.00:50:56:C0:00:01` - Find exact MAC address
- `userName.STARTSWITH.guest_` - Find guest users

### Security Features

All tools automatically:
- ✅ Use ISE ERS API authentication from environment
- ✅ Respect ISE API rate limits
- ✅ Provide read-only access only
- ✅ Use HTTPS for all communications
- ✅ Mask sensitive data in logs

## Attribution

Based on the [ISE MCP Server](https://github.com/automateyournetwork/ISE_MCP) project by **automateyournetwork** (John Capobianco) and **RobertBergman**.

"Cisco ISE" is a trademark of Cisco Systems, Inc. This project is **NOT** affiliated with Cisco Systems.

## License

This project is licensed under the Cisco Sample Code License, Version 1.1.
