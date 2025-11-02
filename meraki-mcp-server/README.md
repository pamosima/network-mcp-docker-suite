# Cisco Meraki MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to Cisco Meraki Dashboard API functionality for cloud network management, monitoring, and configuration operations with enterprise-grade security.

## Overview

This MCP server provides **comprehensive** API-based access to Cisco Meraki Dashboard capabilities, enabling:

- **Cloud Network Management**: Complete Meraki Dashboard API access for networks, devices, and organizations
- **Device Operations**: Monitor and manage MR (wireless), MS (switch), MX (security), and MV (camera) devices
- **Network Analytics**: Client analytics, traffic analysis, and usage monitoring
- **Configuration Management**: SSID management, firewall rules, and network policies  
- **Organization Management**: Multi-organization support with role-based access control
- **Real-Time Monitoring**: Network health, device status, and performance metrics
- **HTTP Transport**: Modern MCP transport for MCP clients (Cursor, LibreChat, etc.)

## Features

### Available Tools

**Organization & Network Management:**
- **`get_organizations`**: List organizations accessible to the user
- **`get_organization_networks`**: List networks within an organization
- **`get_network_devices`**: List devices in a specific network
- **`get_organization_devices`**: List all devices across an organization

**Device Management & Monitoring:**
- **`get_device_statuses`**: Get operational status of network devices
- **`get_device_uplink_statuses`**: Monitor WAN uplink connectivity
- **`get_network_clients`**: List and monitor network clients
- **`get_device_clients`**: Get clients connected to specific devices

**Wireless Operations:**
- **`get_network_ssids`**: List and manage wireless SSIDs
- **`get_network_wireless_settings`**: Access wireless network configuration
- **`get_wireless_client_connectivity_events`**: Monitor wireless client events

**Security & Firewall:**
- **`get_network_appliance_firewall_l3_firewall_rules`**: Manage Layer 3 firewall rules
- **`get_network_appliance_firewall_l7_firewall_rules`**: Manage Layer 7 application firewall
- **`get_network_appliance_security_events`**: Monitor security events and threats

**Analytics & Reporting:**
- **`get_organization_api_requests`**: Monitor API usage and rate limits
- **`get_network_traffic_analysis`**: Analyze network traffic patterns
- **`get_organization_licensing_coterm_licenses`**: Monitor licensing status

### Role-Based Access Control

- **`noc`**: Network Operations Center - monitoring + firmware upgrades
- **`sysadmin`**: System Administrator - read-only access
- **`all`**: Full API access (complete Meraki Dashboard API)

### Security Features

- 🔐 **API Key Security** - Meraki API key loaded from environment variables only
- 🔐 **Role-Based Access** - Configurable access levels (noc/sysadmin/all)
- 🔐 **Rate Limit Aware** - Respects Meraki API rate limits
- 🔐 **SSL/HTTPS** - Secure communication with Meraki Dashboard
- 🔐 **Input Validation** - Parameter validation for all API calls

## Configuration

### Environment Variables

```bash
# Meraki API Configuration
MERAKI_KEY=your_actual_meraki_api_key_here    # Required: Meraki Dashboard API key
MERAKI_BASE_URL=https://api.meraki.com/api/v1 # Optional: Meraki API base URL
MCP_ROLE=noc                                   # Optional: Access control role

# MCP Server Configuration  
MCP_HOST=localhost                             # Optional: Host for MCP server
MCP_PORT=8000                                  # Optional: Port for MCP server
```

### Access Roles

| Role | Description | Capabilities |
|------|-------------|--------------|
| **`noc`** | Network Operations Center | Device monitoring, firmware upgrades, network health |
| **`sysadmin`** | System Administrator | Read-only access to all resources |
| **`all`** | Full Access | Complete Meraki Dashboard API access |

## Usage Examples

### Organization Management

```python
# List all accessible organizations
organizations = get_organizations()

# Get networks in an organization  
networks = get_organization_networks(organization_id="123456")

# List all devices across organization
devices = get_organization_devices(organization_id="123456")
```

### Device Monitoring

```python
# Check device operational status
device_status = get_device_statuses(network_id="N_1234567890")

# Monitor WAN uplink connectivity
uplink_status = get_device_uplink_statuses(network_id="N_1234567890")

# List connected clients
clients = get_network_clients(network_id="N_1234567890")
```

### Wireless Operations

```python
# Manage wireless SSIDs
ssids = get_network_ssids(network_id="N_1234567890")

# Monitor wireless settings
wireless_settings = get_network_wireless_settings(network_id="N_1234567890")

# Track client connectivity events  
events = get_wireless_client_connectivity_events(network_id="N_1234567890")
```

### Security Management

```python
# Review firewall rules
l3_rules = get_network_appliance_firewall_l3_firewall_rules(network_id="N_1234567890")
l7_rules = get_network_appliance_firewall_l7_firewall_rules(network_id="N_1234567890")

# Monitor security events
security_events = get_network_appliance_security_events(network_id="N_1234567890")
```

## Docker Deployment

### Build and Run

```bash
# Build the container
docker build -t meraki-mcp-server .

# Run with environment file
docker run -d --name meraki-mcp-server \
  --env-file .env \
  -p 8000:8000 \
  meraki-mcp-server
```

### Docker Compose

```yaml
services:
  meraki-mcp-server:
    build: .
    container_name: meraki-mcp-server
    environment:
      - MERAKI_KEY=${MERAKI_KEY}
      - MCP_ROLE=noc
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8000
    ports:
      - "8000:8000"
    restart: unless-stopped
```

### Logs and Debugging

```bash
# View container logs
docker logs meraki-mcp-server

# Enable debug logging
docker run -e LOG_LEVEL=DEBUG meraki-mcp-server
```

## Integration

### MCP Client Configuration

**Cursor IDE (`~/.cursor/mcp.json`):**
```json
{
  "mcpServers": {
    "Meraki-MCP-Server": {
      "transport": "http",
      "url": "http://localhost:8000/mcp",
      "timeout": 60000
    }
  }
}
```

**LibreChat (`librechat.yaml`):**
```yaml
mcpServers:
  Meraki-MCP-Server:
    type: streamable-http
    url: http://meraki-mcp-server:8000/mcp
    timeout: 60000
```

## Troubleshooting

### Common Issues

**Invalid API Key:**
```bash
# Check API key format and permissions
curl -L -H "X-Cisco-Meraki-API-Key: YOUR_KEY" \
  "https://api.meraki.com/api/v1/organizations"
```

**Rate Limiting:**
```bash
# Monitor API usage
get_organization_api_requests(organization_id="123456")
```

**Network Connectivity:**
```bash
# Test Meraki Dashboard connectivity
curl -I https://api.meraki.com/api/v1/organizations
```

### Performance Optimization

- **Role-Based Access**: Use appropriate role (`noc` vs `all`) to reduce API calls
- **Rate Limit Awareness**: Server automatically handles Meraki API rate limits
- **Caching**: Results cached appropriately to reduce API calls
- **Pagination**: Large datasets automatically paginated

## API Reference

This server provides access to **60+ Meraki Dashboard API endpoints** including:

- **Organizations**: Management and licensing
- **Networks**: Configuration and monitoring  
- **Devices**: Status, clients, and management
- **Wireless**: SSIDs, settings, and analytics
- **Security**: Firewall rules and events
- **Analytics**: Traffic analysis and reporting

For complete API documentation, see: [Meraki Dashboard API Documentation](https://developer.cisco.com/meraki/api-latest/)

## Security Considerations

### Production Deployment

1. **API Key Security**: Store Meraki API key in secure secrets management
2. **Network Security**: Use HTTPS and restrict network access
3. **Access Control**: Configure appropriate MCP_ROLE for users
4. **Monitoring**: Monitor API usage and rate limits
5. **Rotation**: Regularly rotate Meraki API keys

### Rate Limits

- **Meraki API**: 5 requests per second per organization
- **Server Handling**: Automatic rate limit compliance
- **Best Practices**: Use appropriate roles to minimize API calls

## Support

For issues and questions:

1. **Check Logs**: `docker logs meraki-mcp-server`  
2. **Verify API Key**: Test with Meraki Dashboard API directly
3. **Monitor Usage**: Check API request limits and organization access
4. **Network Connectivity**: Ensure access to `api.meraki.com`

## Contributing

This MCP server is part of the [Network MCP Docker Suite](../README.md). Contributions welcome!

## License

Licensed under the Cisco Sample Code License, Version 1.1. See [LICENSE](../LICENSE) for details.
