# ThousandEyes MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to Cisco ThousandEyes v7 API functionality for network monitoring, performance analysis, and troubleshooting with enterprise-grade security.

## Overview

This MCP server provides **secure** API-based access to ThousandEyes monitoring capabilities, enabling:

- **Network Performance Monitoring**: Access test results, agent data, and path visualization
- **Dashboard Integration**: Retrieve dashboard and widget data for reporting
- **Alert Management**: Monitor and analyze network alerts and events
- **Test Management**: List and analyze network, page-load, and web transaction tests
- **Agent Monitoring**: Enterprise, enterprise-cluster, and cloud agent management
- **Read-Only Security**: All operations are read-only for maximum security
- **HTTP Transport**: Modern MCP transport for MCP clients (Cursor, LibreChat, etc.)

## Features

### Available Tools

- **`te_list_tests`**: List tests with filtering by name, type, or account group
- **`te_list_agents`**: List enterprise, enterprise-cluster, and cloud agents
- **`te_get_test_results`**: Retrieve test results for network, page-load, web-transactions
- **`te_get_path_vis`**: Get path visualization data for network troubleshooting
- **`te_list_dashboards`**: List available dashboards
- **`te_get_dashboard`**: Get dashboard details including widget information
- **`te_get_dashboard_widget`**: Retrieve specific widget data from dashboards
- **`te_get_users`**: List users in the ThousandEyes account
- **`te_get_account_groups`**: List available account groups
- **`te_list_alerts`**: Retrieve alerts with filtering options

### Security Features

- 🔐 **Read-Only Operations** - No write capabilities to prevent accidental changes
- 🔐 **Environment-Only Credentials** - API tokens loaded from environment variables only
- 🔐 **Secure Token Handling** - Tokens masked in logs and never stored on disk
- 🔐 **Rate Limit Respect** - Built-in respect for ThousandEyes API rate limits
- ✅ **HTTPS Communication** - All API calls use encrypted HTTPS
- ✅ **Bearer Token Authentication** - Modern OAuth-style authentication
- ✅ **Non-root container execution** - Minimal privilege operation

## Usage Examples

**SECURITY:** All credentials are loaded from environment variables only for maximum security.

### Network Performance Analysis

```python
# List all network tests
tests = te_list_tests(test_type="network")

# Get recent network test results
results = te_get_test_results(test_id=12345, test_type="network", window="1h")

# Analyze path visualization for troubleshooting
path_data = te_get_path_vis(test_id=12345, window="1h")
```

### Dashboard and Widget Data

```python
# List available dashboards
dashboards = te_list_dashboards()

# Get dashboard details
dashboard = te_get_dashboard(dashboard_id="abc123")

# Retrieve specific widget data
widget_data = te_get_dashboard_widget(
    dashboard_id="abc123", 
    widget_id="widget456", 
    window="24h"
)
```

### Alert Monitoring

```python
# Get recent alerts
alerts = te_list_alerts(window="6h")

# Get alerts for specific test
test_alerts = te_list_alerts(test_id=12345, window="1d")
```

### Agent Management

```python
# List all agents
all_agents = te_list_agents()

# List only enterprise agents
enterprise_agents = te_list_agents(agent_types="enterprise")
```

## Configuration

### Environment Variables

**REQUIRED:** The server requires API credentials in environment variables for security. Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
nano .env
```

#### Core Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| **`TE_TOKEN`** | **ThousandEyes API v7 Bearer token** | - | **✅ YES** |
| `TE_BASE_URL` | ThousandEyes API base URL | `https://api.thousandeyes.com/v7` | No |
| `MCP_HOST` | Server bind address | `localhost` | No |
| `MCP_PORT` | Server port | `8004` | No |

### Getting Your ThousandEyes API Token

1. **Log into ThousandEyes Platform**
2. **Navigate to**: User Profile → API Tokens
3. **Create new token** with appropriate permissions
4. **Copy the Bearer token** to your `.env` file

### Example .env File

```bash
# ThousandEyes MCP Server Configuration
# =====================================

# REQUIRED: ThousandEyes API v7 Bearer token
TE_TOKEN=your_thousandeyes_api_bearer_token_here

# Optional: API and server configuration
TE_BASE_URL=https://api.thousandeyes.com/v7
MCP_HOST=localhost
MCP_PORT=8004
```

### API Requirements

- ThousandEyes **API v7** access
- Valid Bearer token with read permissions
- Network connectivity to `api.thousandeyes.com`

## Deployment

### Using Docker Compose

The server is included in the main `docker-compose.yml`:

```bash
# Start only ThousandEyes MCP server
docker-compose up -d thousandeyes-mcp-server

# View logs
docker-compose logs -f thousandeyes-mcp-server

# Stop server
docker-compose stop thousandeyes-mcp-server
```

### Standalone Docker

```bash
# Build image
docker build -t thousandeyes-mcp-server .

# Run container
docker run -d \
  --name thousandeyes-mcp-server \
  -p 8004:8004 \
  -e TE_TOKEN=your_token_here \
  thousandeyes-mcp-server
```

### Development Mode

```bash
# Install dependencies
uv sync

# Run server directly
uv run python thousandeyes_mcp_server.py
```

## Integration Examples

### Example Prompts for AI Assistants

```
"Show me network performance for our main website over the last 6 hours"

"Which agents are showing high packet loss to our API endpoints today?"

"Get the path visualization data for test 12345 around the time we had issues"

"Show me all alerts from the last 24 hours and group them by test type"

"What's the current status of our enterprise agents in Europe?"
```

### MCP Client Configuration

For **Cursor IDE**, add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "ThousandEyes-MCP-Server": {
      "transport": "http",
      "url": "http://localhost:8004/mcp",
      "timeout": 60000
    }
  }
}
```

For **LibreChat**, add to `librechat.yaml`:

```yaml
mcpServers:
  ThousandEyes-MCP-Server:
    type: streamable-http
    url: http://thousandeyes-mcp-server:8004/mcp
    timeout: 60000
```

## Security Considerations

### API Security

- 🔐 **Read-Only Access**: All tools are read-only, no write operations possible
- 🔐 **Token Security**: Bearer tokens loaded from environment only
- 🔐 **HTTPS Only**: All ThousandEyes API communication uses HTTPS
- 🔐 **No Token Storage**: Tokens never written to disk or logs
- 🔐 **Rate Limiting**: Respects ThousandEyes API rate limits

### Network Security

- Server runs on configurable port (default 8004)
- Supports Docker network isolation
- All API communication is encrypted
- No credentials transmitted in API responses

### Container Security

- Runs as non-root user
- Security options enabled (`no-new-privileges`)
- Resource limits configured
- Minimal attack surface
- Environment variables isolated per container

## Troubleshooting

### Common Issues

**🔐 API Token Errors**
```bash
# Server fails to start with invalid token
ERROR: Failed to connect to ThousandEyes API

# Solution: Check your TE_TOKEN
echo $TE_TOKEN
# Verify token in ThousandEyes Platform → User Profile → API Tokens
```

**🌐 Network Connectivity**
```bash
# Test connectivity to ThousandEyes API
curl -H "Authorization: Bearer $TE_TOKEN" https://api.thousandeyes.com/v7/account-groups

# Check if corporate firewall is blocking HTTPS to api.thousandeyes.com
```

**📊 API Rate Limits**
```bash
# If you get 429 errors, check your API usage:
# - Monitor requests per minute in ThousandEyes Platform
# - Consider implementing retry logic for high-volume use cases
```

### Debug Logging

Check server logs for detailed error information:

```bash
# View server logs
docker-compose logs -f thousandeyes-mcp-server

# Check API connectivity test on startup
# Look for: "✅ Successfully connected to ThousandEyes API"
```

## API Reference

### Tool: te_get_test_results

Get test results for network performance analysis.

**Parameters:**
- `test_id` (int): Test ID to retrieve results for
- `test_type` (str): Type of test ('network', 'page-load', 'web-transactions')
- `window` (str, optional): Time window ('1h', '6h', '1d', '1w')
- `start/end` (str, optional): ISO format timestamps (alternative to window)
- `aid` (int, optional): Account Group ID filter
- `agent_id` (int, optional): Specific agent ID filter

**Returns:** Test results with performance metrics

### Tool: te_get_path_vis

Get path visualization data for network troubleshooting.

**Parameters:**
- `test_id` (int): Test ID for path visualization
- `window` (str, optional): Time window ('1h', '6h', '1d', '1w')
- `agent_id` (int, optional): Specific agent ID
- `direction` (str, optional): 'to-target' or 'from-target'

**Returns:** Network path data showing hops and performance

### Security Features

All tools automatically:
- ✅ Use Bearer token authentication from environment
- ✅ Respect ThousandEyes API rate limits
- ✅ Provide read-only access only
- ✅ Use HTTPS for all communications
- ✅ Mask sensitive data in logs

## Attribution

Based on the [ThousandEyes MCP Community](https://github.com/CiscoDevNet/thousandeyes-mcp-community) project by Aditya Chellam and Kiran Kabdal.

"ThousandEyes" is a trademark of Cisco Systems, Inc. This project is **NOT** affiliated with Cisco/ThousandEyes.

## License

This project is licensed under the Cisco Sample Code License, Version 1.1.
