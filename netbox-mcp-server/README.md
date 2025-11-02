# NetBox MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to NetBox DCIM/IPAM capabilities for infrastructure documentation, IP address management, and device lifecycle tracking with enterprise-grade security.

## Overview

This MCP server provides **complete** API-based access to NetBox capabilities, enabling:

- **DCIM (Data Center Infrastructure Management)**: Complete facility, rack, and device management
- **IPAM (IP Address Management)**: IP address spaces, prefixes, and VLAN management
- **Device Lifecycle Management**: Hardware inventory, device types, and lifecycle tracking
- **Network Documentation**: Comprehensive network topology and connection documentation
- **Cable Management**: Physical and logical connection tracking
- **Custom Fields**: Extensible data model with custom attributes
- **Multi-Tenancy**: Organization and tenant-based resource separation
- **HTTP Transport**: Modern MCP transport for MCP clients (Cursor, LibreChat, etc.)

## Features

### Available Tools

**Site & Location Management:**
- **`get_sites`**: List and manage data center sites and locations
- **`get_site_by_id`**: Get detailed information about specific sites
- **`create_site`**: Create new data center sites
- **`get_racks`**: List equipment racks and their configurations

**Device & Hardware Management:**
- **`get_devices`**: List network and compute devices
- **`get_device_by_id`**: Get detailed device information and specifications
- **`create_device`**: Add new devices to inventory
- **`get_device_types`**: List available device types and models
- **`get_manufacturers`**: List equipment manufacturers

**IP Address Management (IPAM):**
- **`get_ip_addresses`**: List and manage IP address assignments
- **`create_ip_address`**: Assign new IP addresses to devices/interfaces
- **`get_prefixes`**: List network prefixes and subnets
- **`get_vlans`**: List VLAN configurations and assignments
- **`get_vrfs`**: List Virtual Routing and Forwarding instances

**Network Topology:**
- **`get_interfaces`**: List device network interfaces
- **`get_cables`**: List physical cable connections
- **`get_connections`**: List logical network connections
- **`get_circuits`**: List WAN circuits and provider connections

**Documentation & Reporting:**
- **`search_objects`**: Universal search across all NetBox objects
- **`get_custom_fields`**: List custom field definitions
- **`update_object`**: Update existing NetBox objects
- **`delete_object`**: Remove objects from NetBox inventory

### Security Features

- 🔐 **Token-Based Authentication** - NetBox API token loaded from environment variables
- 🔐 **Read-Only Operations** - Safe operations with configurable write access
- 🔐 **SSL/HTTPS Support** - Secure communication with NetBox instance
- 🔐 **Input Validation** - Parameter validation for all API calls
- 🔐 **Rate Limiting** - Respects NetBox API rate limits

## Configuration

### Environment Variables

Create a `.env` file in the `netbox-mcp-server/` directory:

```bash
# Copy the environment template
cp .env.example .env
```

**Required Configuration:**
```bash
# NetBox API Configuration (Required)
NETBOX_URL=https://netbox.example.com        # Your NetBox instance URL
NETBOX_TOKEN=your_netbox_token_here          # NetBox API token with appropriate permissions

# MCP Server Configuration (Optional)
MCP_HOST=localhost                           # Host for MCP server (default: localhost)
MCP_PORT=8001                               # Port for MCP server (default: 8001)
```

### Getting NetBox API Token

1. **Login** to NetBox web interface
2. **Navigate** to your Profile (top right) → API Tokens
3. **Create** new token with appropriate permissions:
   - **Read**: For monitoring and documentation
   - **Write**: For device provisioning and updates  
   - **Delete**: For cleanup operations (use carefully)
4. **Copy** the token to your `.env` file

### Environment Variable Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NETBOX_URL` | NetBox instance URL (include https://) | - | ✅ Yes |
| `NETBOX_TOKEN` | NetBox API token | - | ✅ Yes |
| `MCP_HOST` | Host for MCP server | `localhost` | No |
| `MCP_PORT` | Port for MCP server | `8001` | No |

### NetBox API Token

1. **Login to NetBox** web interface
2. **Navigate to** Profile → API Tokens
3. **Create Token** with appropriate permissions:
   - **Read**: For monitoring and documentation
   - **Write**: For device provisioning and updates
   - **Delete**: For cleanup operations (use carefully)

## Usage Examples

### Site Management

```python
# List all data center sites
sites = get_sites()

# Get specific site details
site_detail = get_site_by_id(site_id=1)

# Create new data center site
new_site = create_site(
    name="DC-East-01", 
    slug="dc-east-01",
    status="active"
)
```

### Device Management

```python
# List all devices
devices = get_devices()

# Filter devices by site
devices_by_site = get_devices(site_id=1)

# Get specific device details
device_detail = get_device_by_id(device_id=123)

# Add new device to inventory
new_device = create_device(
    name="core-switch-01",
    device_type_id=5,
    site_id=1,
    status="active"
)
```

### IP Address Management

```python
# List IP address assignments
ip_addresses = get_ip_addresses()

# Filter by VRF
vrf_ips = get_ip_addresses(vrf_id=2)

# Assign new IP address
new_ip = create_ip_address(
    address="192.168.1.10/24",
    status="active",
    description="Core switch management"
)

# List network prefixes
prefixes = get_prefixes()

# List VLANs
vlans = get_vlans(site_id=1)
```

### Search & Documentation

```python
# Universal search across NetBox
search_results = search_objects(
    endpoint="devices",
    query="cisco"
)

# List available device types
device_types = get_device_types()

# Get manufacturer information
manufacturers = get_manufacturers()
```

## Docker Deployment

### Build and Run

```bash
# Build the container
docker build -t netbox-mcp-server .

# Run with environment file
docker run -d --name netbox-mcp-server \
  --env-file .env \
  -p 8001:8001 \
  netbox-mcp-server
```

### Docker Compose

Add to your `docker-compose.yml` file:

```yaml
services:
  netbox-mcp-server:
    build: ./netbox-mcp-server
    container_name: netbox-mcp-server
    env_file:
      - ./netbox-mcp-server/.env
    environment:
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8001
    ports:
      - "8001:8001"
    restart: unless-stopped
    networks:
      - default
```

**Or use the main project's deployment:**
```bash
# From project root
./deploy.sh start netbox        # Deploy only NetBox server
./deploy.sh start docs          # Deploy NetBox + Catalyst Center
./deploy.sh start all           # Deploy all servers including NetBox
```

### Logs and Debugging

```bash
# View container logs
docker logs netbox-mcp-server

# Enable debug logging
docker run -e LOG_LEVEL=DEBUG netbox-mcp-server
```

## Integration

### MCP Client Configuration

**Cursor IDE (`~/.cursor/mcp.json`):**
```json
{
  "mcpServers": {
    "NetBox-MCP-Server": {
      "transport": "http",
      "url": "http://localhost:8001/mcp",
      "timeout": 60000
    }
  }
}
```

**LibreChat (`librechat.yaml`):**
```yaml
mcpServers:
  Netbox-MCP-Server:
    type: streamable-http
    url: http://netbox-mcp-server:8001/mcp
    timeout: 60000
```

## Common Use Cases

### Infrastructure Documentation

- **Asset Inventory**: Track all network devices, servers, and infrastructure
- **Cable Management**: Document physical connections and cable runs
- **IP Address Management**: Maintain accurate IP address assignments
- **Network Topology**: Visualize and document network architecture

### Capacity Planning

- **Rack Space**: Monitor rack utilization and plan expansions
- **IP Space**: Track IP address utilization and plan subnets
- **Power & Cooling**: Document power and cooling requirements
- **Growth Planning**: Historical data for infrastructure growth

### Compliance & Auditing

- **Asset Tracking**: Maintain accurate hardware inventory
- **Change Management**: Track infrastructure changes over time
- **Documentation**: Ensure network documentation is current
- **Reporting**: Generate compliance and audit reports

### Network Automation

- **Device Provisioning**: Automate device onboarding
- **IP Assignment**: Automated IP address management
- **Configuration Management**: Integration with automation tools
- **Monitoring Integration**: Feed data to monitoring systems

## Troubleshooting

### Common Issues

**Container Won't Start:**
```bash
# Check logs for errors
docker logs netbox-mcp-server

# Common causes:
# 1. Missing NETBOX_URL or NETBOX_TOKEN in .env file
# 2. Port 8001 already in use (check: lsof -i :8001)
# 3. Invalid NetBox URL format (must include https://)
```

**Connection Errors:**
```bash
# Test NetBox connectivity
curl -H "Authorization: Token YOUR_TOKEN" \
  "https://netbox.example.com/api/"

# Expected response: NetBox API information
# Error response: Connection timeout/refused or 401 Unauthorized
```

**Authentication Issues:**
```bash
# Verify API token permissions
curl -H "Authorization: Token YOUR_TOKEN" \
  "https://netbox.example.com/api/users/me/"

# Check token has required permissions (read/write/delete)
curl -H "Authorization: Token YOUR_TOKEN" \
  "https://netbox.example.com/api/users/tokens/"
```

**MCP Client Connection Issues:**
```bash
# Verify MCP endpoint is accessible
curl http://localhost:8001/mcp

# Should return MCP protocol response
# If connection refused, check container status:
docker ps | grep netbox-mcp-server
```

**SSL Certificate Issues:**
```bash
# Test SSL connectivity
openssl s_client -connect netbox.example.com:443 -servername netbox.example.com

# For self-signed certificates, you may need to configure trust
# Check container logs for SSL verification errors
```

### Performance Optimization

- **Pagination**: Use appropriate page sizes for large datasets
- **Filtering**: Apply filters to reduce data transfer
- **Caching**: Results cached appropriately to reduce API calls
- **Indexing**: Ensure NetBox database is properly indexed

## API Reference

This server provides access to **NetBox REST API v2.8+** including:

- **DCIM**: Sites, racks, devices, device types, manufacturers
- **IPAM**: IP addresses, prefixes, VRFs, VLANs, aggregates  
- **Circuits**: Providers, circuit types, circuits
- **Extras**: Custom fields, tags, webhooks
- **Tenancy**: Tenants, tenant groups
- **Users**: User accounts, groups, permissions

For complete API documentation, see: [NetBox REST API Documentation](https://netbox.readthedocs.io/en/stable/rest-api/)

## Security Considerations

### Production Deployment

1. **API Token Security**: Store NetBox tokens in secure secrets management
2. **Network Security**: Use HTTPS and restrict network access
3. **Access Control**: Configure appropriate NetBox user permissions
4. **Monitoring**: Monitor API usage and access patterns
5. **Backup**: Regular backup of NetBox database and configuration

### Best Practices

- **Token Rotation**: Regularly rotate NetBox API tokens
- **Least Privilege**: Grant minimum required permissions
- **Audit Logging**: Enable NetBox audit logging
- **SSL/TLS**: Use strong SSL/TLS configuration
- **Network Segmentation**: Isolate NetBox on management network

## Support

For issues and questions:

1. **Check Logs**: `docker logs netbox-mcp-server`
2. **Verify Token**: Test with NetBox API directly  
3. **Network Connectivity**: Ensure access to NetBox instance
4. **Permissions**: Verify API token has required permissions

## Contributing

This MCP server is part of the [Network MCP Docker Suite](../README.md). Contributions welcome!

## License

Licensed under the Cisco Sample Code License, Version 1.1. See [LICENSE](../LICENSE) for details.
