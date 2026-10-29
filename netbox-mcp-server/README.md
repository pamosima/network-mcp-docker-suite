# NetBox MCP Server

**AI-Powered NetBox Automation with Dynamic Custom Script Discovery**

A Model Context Protocol (MCP) server that automatically transforms NetBox Custom Scripts into first-class MCP tools, enabling natural language infrastructure automation with enterprise-grade security.

## 🚀 Key Innovation: Dynamic Custom Scripts

### **Your NetBox Scripts Become AI Tools Automatically**

This server **automatically discovers and registers** your NetBox Custom Scripts as native MCP tools at startup - **zero configuration required**.

Write a custom script in NetBox → Restart container → AI can use it immediately!

**Example:**
```python
# Your NetBox script becomes this MCP tool automatically:
create_site_and_locations(
    tenant_id=24,
    region_id=12,
    site_name="Site-10",
    address="123 Main St",
    number_of_floors=3,
    lowest_floor=0
)
```

### **How It Works**

1. **Auto-Discovery**: Server fetches custom scripts from NetBox API on startup
2. **Dynamic Registration**: Each script becomes a typed MCP tool with proper parameters
3. **AI-Native**: Tools appear directly to AI agents (Claude, LibreChat, etc.)
4. **Type-Safe**: ObjectVar → int, StringVar → str, IntegerVar → int
5. **Smart Endpoints**: Automatically maps parameters to NetBox endpoints

### 🎯 Benefits

- ✅ **Zero Configuration**: Fully API-based, no manual setup
- ✅ **Direct Execution**: AI calls tools directly - simple and efficient
- ✅ **Type Safety**: Parameters properly typed for better AI understanding
- ✅ **Auto-Updates**: New scripts appear after container restart
- ✅ **Scalable**: Follows [Anthropic's MCP best practices](https://www.anthropic.com/engineering/code-execution-with-mcp)
- ✅ **Production Ready**: Error handling, logging, job tracking

### 📦 Currently Auto-Discovered Tools

When the server starts, it registers tools like:
- `create_site_and_locations()` - Provision new sites with floors
- `add_switches_to_site()` - Deploy switches to existing sites
- `create_ips()` - Automated IP address allocation
- **Your custom scripts automatically appear here!**

---

## 🏗️ Additional NetBox Capabilities

Beyond custom scripts, this server also provides comprehensive access to:

- **DCIM (Data Center Infrastructure Management)**: Sites, racks, devices, cables
- **IPAM (IP Address Management)**: IP addresses, prefixes, VLANs, VRFs
- **Device Lifecycle Management**: Hardware inventory and tracking
- **Network Documentation**: Topology and connection documentation
- **Multi-Tenancy**: Organization and tenant-based resource separation

All accessible through natural language with your AI assistant!

## Available Tools

### 🆕 Dynamically Registered Custom Script Tools

**Auto-discovered from your NetBox custom scripts:**
- **`create_site_and_locations(...)`**: 🎯 Provision new sites with multiple floors
- **`add_switches_to_site(...)`**: 🎯 Deploy switches to existing sites
- **`create_ips(...)`**: 🎯 Automated IP address allocation workflows
- ***Your custom scripts automatically appear here!*** 🎯

Each tool is automatically generated with:
- Properly typed parameters (int, str, bool)
- Intelligent descriptions based on variable names
- Endpoint hints for ObjectVar parameters (use `get_object_choices()` to see options)
- Job tracking and status monitoring

---

### Core NetBox Operations

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

**Custom Script Utilities:**
- **`get_object_choices`**: List available options for ObjectVar parameters (essential for selecting tenants, regions, sites, etc.)
- **`get_script_job_status`**: Check script execution status and results
- **`list_script_jobs`**: View history of script executions

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
NETBOX_ENABLE_WRITES=false                   # Set true to register create/update/delete and custom scripts
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
| `NETBOX_ENABLE_WRITES` | Register mutating tools | `false` | No |
| `MCP_API_TOKEN` | Bearer token; required when bind is not loopback | (empty) | When exposed |

### NetBox API Token

1. **Login to NetBox** web interface
2. **Navigate to** Profile → API Tokens
3. **Create Token** with appropriate permissions:
   - **Read**: For monitoring and documentation
   - **Write**: For device provisioning and updates
   - **Delete**: For cleanup operations (use carefully)

## Custom Scripts & Workflow Automation

The NetBox MCP Server supports **NetBox Custom Scripts**, enabling you to execute complex workflows through natural language prompts.

### How It Works

1. **NetBox Custom Scripts** are Python-based workflows stored in NetBox (`/opt/netbox/scripts/`)
2. Each script has a **name**, **description**, and **required variables (vars)**
3. Variables can be:
   - **ObjectVar**: Requires object ID (e.g., tenant_id, region_id, site_id)
   - **StringVar**: Requires text string
   - **IntegerVar**: Requires integer number
   - **BooleanVar**: Requires true/false
4. You can ask the AI to run workflows in natural language
5. The AI automatically resolves ObjectVars by searching for objects and their IDs

### Example Workflow

**User**: "Run workflow to create a new site called DC-East-01"

**AI Process (Improved UX)**:
1. Calls `find_custom_script("create site")` to discover matching workflows
2. Finds `CreateSiteAndLocations` (ID 17)
3. Calls `get_script_variables(17)` to see it needs:
   - `tenant` (ObjectVar) - needs tenant ID
   - `region` (ObjectVar) - needs region ID
   - `site_name` (StringVar) - "DC-East-01"
   - `number_of_floors` (IntegerVar) - asks user
4. **IMPROVED**: Calls `get_object_choices("dcim/tenants")` to show ALL tenants:
   - Shows: "1: Acme Corp, 2: TechCo, 3: GlobalNet"
   - User picks: "Acme Corp" → uses ID 1
5. **IMPROVED**: Calls `get_object_choices("dcim/regions")` to show ALL regions:
   - Shows: "1: North America, 2: Europe, 3: Asia Pacific"
   - User picks: "Europe" → uses ID 2
6. Executes `execute_custom_script()` with all resolved parameters
7. Monitors execution with `get_script_job_status()`
8. Reports results back to user

**Benefits**:
- ✅ No typos - user picks from list
- ✅ No failed searches - always valid options
- ✅ Better UX - clear choices
- ✅ Faster - no guessing

### Common Use Cases

**Site Provisioning Workflows:**
- Create site with VLANs, prefixes, and device racks
- Configure standard site topology
- Set up management networks and IP addressing

**Device Onboarding:**
- Bulk device provisioning with standard configurations
- IP address allocation for new devices
- Cable and connection documentation

**IP Management Workflows:**
- Allocate IP blocks for new sites
- Reserve IP ranges for specific purposes
- Validate IP addressing schemes

**Compliance & Auditing:**
- Run compliance checks across infrastructure
- Generate audit reports
- Validate configurations against standards

### Script Discovery

The AI can intelligently match your natural language requests to scripts using `find_custom_script()`:

| Your Request | Matched Script | Script ID |
|--------------|----------------|-----------|
| "Create a new site with floors" | `CreateSiteAndLocations` | 17 |
| "Add switches to site" | `AddSwitchesToSite` | 18 |
| "Create IP addresses" | `CreateIps` | 16 |

**Example workflow:**
```python
# User: "Run workflow to create a new site"
# AI process:
matches = find_custom_script("create site")
# Returns: CreateSiteAndLocations (ID 17)

# AI then executes with user-provided parameters
result = execute_custom_script(
    script_id=17,
    data={"site_name": "DC-East-01", ...}
)
```

### Requirements

**NetBox Configuration:**
1. Custom scripts must be installed in NetBox (`/opt/netbox/scripts/`)
2. Scripts must be properly registered and available via the API
3. API token must have permissions to execute scripts

**Script Best Practices:**
- Add clear descriptions to scripts for AI discovery
- Use descriptive parameter names
- Include validation and error handling
- Document expected inputs and outputs

## Usage Examples

### 🆕 Dynamic Custom Scripts (Recommended Approach)

**The fastest way to automate NetBox workflows - your scripts become AI tools automatically!**

```python
# Example 1: Create a new site with floors using dynamic tool
# No need to find scripts, get variables, or look up IDs manually
# The AI can call this directly!

result = create_site_and_locations(
    tenant_id=24,           # Tip: Use get_object_choices("tenancy/tenants") to see options
    region_id=12,           # Tip: Use get_object_choices("dcim/regions") to see options
    site_name="DC-West-05",
    address="123 Innovation Drive, San Jose, CA",
    number_of_floors=4,
    lowest_floor=0
)

print(f"Site created! Job ID: {result['job_id']}")

# Example 2: Add switches to the site
result = add_switches_to_site(
    tenant_id=24,
    site_id=120,
    device_type_id=8,
    device_role_id=3,
    device_uplink_id=100,
    serial_numbers="SN12345,SN12346,SN12347"
)

# Example 3: Check job status
status = get_script_job_status(result['job_id'])
print(f"Status: {status['status']['label']}")
print(f"Output: {status['data']}")
```

**How to discover available options for parameters:**

```python
# Show available tenants
tenants = get_object_choices("tenancy/tenants")
for t in tenants['choices']:
    print(f"{t['name']} (ID: {t['id']})")

# Show available regions
regions = get_object_choices("dcim/regions")
for r in regions['choices']:
    print(f"{r['name']} (ID: {r['id']})")

# Show available sites
sites = get_object_choices("dcim/sites")
```

---

### Core NetBox Operations

**Site Management:**

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

### Utility: Script Job Monitoring

**Check the status of script executions:**

```python
# Check job status after running a dynamic tool
status = get_script_job_status(job_id=138)
print(f"Status: {status['status']}")
print(f"Completed: {status['completed']}")

# List recent script executions
jobs = list_script_jobs(limit=10)
for job in jobs['data']:
    print(f"{job['name']}: {job['status']}")
        "number_of_floors": 3,           # IntegerVar: Integer
        "lowest_floor": 0                # IntegerVar: Integer
    },
    commit=True
)

# Step 5: Monitor execution status
if job_result["success"]:
    job_id = job_result["job_id"]
    status = get_script_job_status(job_id=job_id)
    
    print(f"Status: {status['status']}")  # completed, pending, running, failed
    print(f"Completed: {status['completed']}")

# View recent script executions
recent_jobs = list_script_jobs(limit=10)
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
