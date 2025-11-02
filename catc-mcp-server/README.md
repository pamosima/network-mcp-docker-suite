# Cisco Catalyst Center MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to Cisco Catalyst Center functionality for enterprise network management, site topology, client analytics, and network assurance with enterprise-grade security.

## Overview

This MCP server provides **complete** API-based access to Cisco Catalyst Center capabilities, enabling:

- **Enterprise Network Management**: Comprehensive device discovery, monitoring, and management
- **Site Topology Management**: Network site hierarchy and topology visualization
- **Client Analytics**: Detailed client connectivity and performance analytics
- **Network Assurance**: Proactive issue detection and network health monitoring
- **Device Configuration**: Template-based configuration management and deployment
- **Compliance Management**: Policy compliance monitoring and reporting
- **Inventory Management**: Complete network device inventory and lifecycle tracking
- **HTTP Transport**: Modern MCP transport for MCP clients (Cursor, LibreChat, etc.)

## Features

### Available Tools

**Network & Device Management:**
- **`get_network_devices`**: List and monitor all network devices
- **`get_device_detail`**: Get detailed device information and specifications
- **`get_device_health`**: Monitor device health metrics and status
- **`get_compliance_detail`**: Check device compliance against policies

**Site & Topology Management:**
- **`get_sites`**: List network sites in hierarchical structure
- **`get_site_topology`**: Get detailed site topology and device relationships
- **`get_network_health`**: Monitor overall network health metrics

**Client Analytics & Monitoring:**
- **`get_clients`**: List and monitor network clients
- **`get_client_health`**: Monitor client connectivity and performance
- **`get_client_detail`**: Get detailed client information and history

**Network Assurance & Issues:**
- **`get_assurance_issues`**: Get detailed network issues with suggested actions
- **`resolve_issues`**: Mark network issues as resolved
- **`get_network_events`**: Monitor network events and changes

**Configuration & Templates:**
- **`get_templates`**: List configuration templates
- **`get_template_details`**: Get detailed template configuration
- **`deploy_template`**: Deploy configuration templates to devices

**Inventory & Licensing:**
- **`get_device_inventory`**: Complete device inventory management
- **`get_license_usage`**: Monitor software licensing usage
- **`get_software_versions`**: Track device software versions

### Security Features

- 🔐 **Username/Password Authentication** - Cisco Catalyst Center credentials from environment
- 🔐 **Session Management** - Secure session handling with automatic renewal
- 🔐 **SSL/HTTPS Support** - Secure communication with Catalyst Center
- 🔐 **Input Validation** - Parameter validation for all API calls
- 🔐 **Rate Limiting** - Respects Catalyst Center API rate limits

## Configuration

### Environment Variables

Create a `.env` file in the `catc-mcp-server/` directory:

```bash
# Copy the environment template
cp .env.example .env
```

**Required Configuration:**
```bash
# Catalyst Center API Configuration (Required)
CATC_URL=https://catalyst-center.example.com  # Your Catalyst Center URL (include https://)
CATC_USERNAME=your_catalyst_center_username   # Catalyst Center username with API access
CATC_PASSWORD=your_catalyst_center_password   # Catalyst Center password

# MCP Server Configuration (Optional)
MCP_HOST=localhost                            # Host for MCP server (default: localhost)
MCP_PORT=8002                                # Port for MCP server (default: 8002)
```

### Catalyst Center Prerequisites

**User Requirements:**
1. **API Access**: Ensure API access is enabled in Catalyst Center
2. **RBAC Permissions**: User account needs appropriate permissions:
   - **Observer**: Read-only access to devices and networks
   - **Operator**: Device management and configuration
   - **Administrator**: Full system access (recommended for full functionality)

**Network Requirements:**
1. **Connectivity**: Ensure network connectivity from Docker host to Catalyst Center
2. **DNS Resolution**: Catalyst Center URL must be resolvable
3. **Certificate Trust**: For HTTPS connections (most deployments)

### Environment Variable Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CATC_URL` | Catalyst Center URL (include https://) | - | ✅ Yes |
| `CATC_USERNAME` | Catalyst Center username | - | ✅ Yes |
| `CATC_PASSWORD` | Catalyst Center password | - | ✅ Yes |
| `MCP_HOST` | Host for MCP server | `localhost` | No |
| `MCP_PORT` | Port for MCP server | `8002` | No |

### Catalyst Center Prerequisites

1. **API Access**: Ensure API access is enabled in Catalyst Center
2. **User Permissions**: User account needs appropriate RBAC permissions:
   - **Observer**: Read-only access to devices and networks
   - **Operator**: Device management and configuration
   - **Administrator**: Full system access
3. **Network Connectivity**: Ensure network connectivity to Catalyst Center

## Usage Examples

### Device Management

```python
# List all network devices
devices = get_network_devices()

# Filter devices by type
switches = get_network_devices(device_type="Switches and Hubs")

# Get detailed device information
device_detail = get_device_detail(device_id="abc123-def456-ghi789")

# Check device health
device_health = get_device_health(device_id="abc123-def456-ghi789")
```

### Site Management

```python
# List all sites
sites = get_sites()

# Get site topology
topology = get_site_topology(site_id="site-uuid-123")

# Monitor network health
health = get_network_health()
```

### Client Analytics

```python
# List network clients
clients = get_clients(limit=100)

# Get client connectivity details
client_detail = get_client_detail(mac_address="00:11:22:33:44:55")

# Monitor client health
client_health = get_client_health(client_mac="00:11:22:33:44:55")
```

### Network Assurance

```python
# Get active network issues
issues = get_assurance_issues(
    status="active",
    priority="P1",
    limit=50
)

# Get issues for specific device
device_issues = get_assurance_issues(
    network_device_id="device-uuid-123"
)

# Resolve specific issues
resolve_result = resolve_issues(
    issue_ids=["issue-uuid-1", "issue-uuid-2"]
)
```

### Configuration Management

```python
# List configuration templates
templates = get_templates()

# Get template details
template_detail = get_template_details(template_id="template-uuid-123")

# Deploy template to devices
deployment = deploy_template(
    template_id="template-uuid-123",
    device_ids=["device-1", "device-2"]
)
```

### Compliance & Inventory

```python
# Check device compliance
compliance = get_compliance_detail(device_id="device-uuid-123")

# Get device inventory
inventory = get_device_inventory()

# Monitor license usage
licenses = get_license_usage()

# Track software versions
versions = get_software_versions()
```

## Docker Deployment

### Build and Run

```bash
# Build the container
docker build -t catc-mcp-server .

# Run with environment file
docker run -d --name catc-mcp-server \
  --env-file .env \
  -p 8002:8002 \
  catc-mcp-server
```

### Docker Compose

Add to your `docker-compose.yml` file:

```yaml
services:
  catc-mcp-server:
    build: ./catc-mcp-server
    container_name: catc-mcp-server
    env_file:
      - ./catc-mcp-server/.env
    environment:
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8002
    ports:
      - "8002:8002"
    restart: unless-stopped
    networks:
      - default
```

**Or use the main project's deployment:**
```bash
# From project root  
./deploy.sh start catc          # Deploy only Catalyst Center server
./deploy.sh start cisco         # Deploy Cisco platforms (includes Catalyst Center)
./deploy.sh start management    # Deploy Meraki + Catalyst Center
./deploy.sh start all           # Deploy all servers including Catalyst Center
```

### Logs and Debugging

```bash
# View container logs
docker logs catc-mcp-server

# Enable debug logging
docker run -e LOG_LEVEL=DEBUG catc-mcp-server
```

## Integration

### MCP Client Configuration

**Cursor IDE (`~/.cursor/mcp.json`):**
```json
{
  "mcpServers": {
    "Catalyst-Center-MCP-Server": {
      "transport": "http",
      "url": "http://localhost:8002/mcp",
      "timeout": 60000
    }
  }
}
```

**LibreChat (`librechat.yaml`):**
```yaml
mcpServers:
  CatC-MCP-Server:
    type: streamable-http
    url: http://catc-mcp-server:8002/mcp
    timeout: 60000
```

## Common Use Cases

### Network Operations Center (NOC)

- **Device Monitoring**: Real-time device health and status monitoring
- **Issue Management**: Proactive issue detection and resolution tracking
- **Performance Analytics**: Network and client performance monitoring
- **Capacity Planning**: Utilization monitoring and growth planning

### Network Engineering

- **Configuration Management**: Template-based device configuration
- **Compliance Monitoring**: Policy compliance and deviation detection
- **Change Management**: Track configuration changes and deployments
- **Troubleshooting**: Detailed diagnostics and issue correlation

### Security Operations

- **Device Compliance**: Security policy compliance monitoring
- **Access Control**: Client access and authorization monitoring
- **Threat Detection**: Network anomaly and security event monitoring
- **Audit Reporting**: Compliance and security audit reports

### Infrastructure Management

- **Inventory Management**: Complete network device inventory
- **License Management**: Software licensing and compliance tracking
- **Lifecycle Management**: Device lifecycle and maintenance tracking
- **Documentation**: Automated network documentation generation

## Troubleshooting

### Common Issues

**Container Won't Start:**
```bash
# Check logs for errors
docker logs catc-mcp-server

# Common causes:
# 1. Missing CATC_URL, CATC_USERNAME, or CATC_PASSWORD in .env file
# 2. Port 8002 already in use (check: lsof -i :8002)
# 3. Invalid Catalyst Center URL format (must include https://)
# 4. Network connectivity issues to Catalyst Center
```

**Authentication Errors:**
```bash
# Test Catalyst Center authentication
curl -k -X POST "https://catalyst-center.example.com/api/system/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"YOUR_USERNAME","password":"YOUR_PASSWORD"}'

# Expected response: JWT token
# Error responses: 401 Unauthorized, 403 Forbidden
```

**Network Connectivity:**
```bash
# Test basic connectivity
ping catalyst-center.example.com
telnet catalyst-center.example.com 443

# Test from container (if needed)
docker exec catc-mcp-server ping catalyst-center.example.com
```

**MCP Client Connection Issues:**
```bash
# Verify MCP endpoint is accessible
curl http://localhost:8002/mcp

# Should return MCP protocol response
# If connection refused, check container status:
docker ps | grep catc-mcp-server
```

**SSL Certificate Issues:**
```bash
# Test SSL connectivity  
openssl s_client -connect catalyst-center.example.com:443

# For self-signed certificates in corporate environments,
# check container logs for SSL verification errors
```

**Permission Issues:**
- Verify user has appropriate RBAC permissions in Catalyst Center:
  - **Observer**: Minimum for read operations
  - **Operator**: For device management operations
  - **Administrator**: For full functionality
- Check if API access is enabled for the user account
- Ensure user account is not locked or disabled
- Verify user has access to the specific network sites/devices

### Performance Optimization

- **Pagination**: Use appropriate page sizes for large datasets
- **Filtering**: Apply filters to reduce data transfer and processing
- **Session Reuse**: Server automatically manages session tokens
- **Caching**: Results cached appropriately to reduce API calls

## API Reference

This server provides access to **Catalyst Center REST API v1** including:

- **Intent API**: High-level network intent operations
- **Command Runner**: Execute commands on network devices
- **Discovery**: Network device discovery and inventory
- **Site Management**: Hierarchical site structure management
- **Client Analytics**: Detailed client connectivity analytics
- **Assurance**: Network health and issue management
- **Configuration**: Device configuration and template management

For complete API documentation, see: [Cisco Catalyst Center API Documentation](https://developer.cisco.com/docs/dna-center/)

## Security Considerations

### Production Deployment

1. **Credential Security**: Store credentials in secure secrets management
2. **Network Security**: Use HTTPS and restrict network access
3. **Access Control**: Configure appropriate RBAC permissions
4. **Session Management**: Monitor and audit API session usage
5. **Certificate Management**: Use valid SSL certificates

### Best Practices

- **Credential Rotation**: Regularly rotate Catalyst Center passwords
- **Least Privilege**: Grant minimum required permissions
- **Audit Logging**: Enable comprehensive audit logging
- **Network Segmentation**: Isolate management network traffic
- **Multi-Factor Authentication**: Enable MFA for Catalyst Center access

## Support

For issues and questions:

1. **Check Logs**: `docker logs catc-mcp-server`
2. **Verify Credentials**: Test with Catalyst Center API directly
3. **Network Connectivity**: Ensure access to Catalyst Center
4. **Permissions**: Verify user RBAC permissions
5. **API Status**: Check Catalyst Center API service status

## Contributing

This MCP server is part of the [Network MCP Docker Suite](../README.md). Contributions welcome!

## License

Licensed under the Cisco Sample Code License, Version 1.1. See [LICENSE](../LICENSE) for details.
