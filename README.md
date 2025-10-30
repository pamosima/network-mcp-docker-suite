# 🌐 Network MCP Docker Suite

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/pamosima/network-mcp-docker-suite)

> **📚 Example Code for Learning & Development**  
> This is a demonstration project showcasing MCP server implementations for network management. Intended for educational purposes, testing, and development environments.

A comprehensive Docker-based suite of Model Context Protocol (MCP) servers for network infrastructure management. This example implementation provides Cisco Meraki Dashboard API, NetBox DCIM/IPAM, Cisco Catalyst Center, Cisco ThousandEyes, and IOS XE device management through containerized MCP servers. Designed for demonstration, learning, and integration with MCP clients like Cursor, LibreChat, and other MCP-enabled applications.

## 🎬 Live Demo

AI-Powered Network Troubleshooting with LibreChat using Multiple MCP Servers

![Catalyst Center MCP Demo](img/CatC-MCP_demo.gif)

*Watch how natural language queries automatically investigate and resolve network issues using both Catalyst Center MCP Server and IOS XE MCP Server. The AI assistant correlates data from management systems (Catalyst Center) with direct device access (IOS XE SSH) to identify root causes and provide comprehensive solutions.*

## 📋 Description

This Docker suite contains five example MCP servers for comprehensive network infrastructure management:

- **Meraki MCP Server**: Provides comprehensive access to Cisco Meraki Dashboard API functionality including device management, network monitoring, and configuration operations
- **NetBox MCP Server**: Enables complete NetBox DCIM/IPAM capabilities for infrastructure documentation, IP address management, and device lifecycle tracking
- **Catalyst Center MCP Server**: Delivers full Cisco Catalyst Center functionality including network device management, site topology, client analytics, and network assurance
- **ThousandEyes MCP Server**: Provides comprehensive access to Cisco ThousandEyes v7 API for network performance monitoring, path visualization, dashboard data, and alert management
- **IOS XE MCP Server**: Enables direct SSH-based management of Cisco IOS XE devices including configuration changes, monitoring commands, and device information retrieval

All servers are containerized using Docker with flexible deployment profiles, designed for development, testing, and demonstration environments with seamless integration across MCP clients.

## 🎯 Use Case

Network administrators and DevOps teams face significant challenges in managing modern hybrid network infrastructure across cloud and on-premises environments. This solution addresses these challenges by providing:

### 🚀 Primary Use Cases

#### 1. **Unified Network Operations** 🌐
- **Single Interface**: Manage Meraki cloud networks, on-premises NetBox DCIM/IPAM, Catalyst Center infrastructure, and direct IOS-XE devices through one MCP protocol interface
- **Streamlined Workflows**: Reduce context switching between multiple network management tools and dashboards
- **Cross-Platform Visibility**: Correlate data across different network management systems for comprehensive operational insights

#### 2. **AI-Powered Network Management** 🤖
- **Natural Language Queries**: Use AI assistants (Cursor, LibreChat) to query network infrastructure using plain English
- **Automated Troubleshooting**: Enable AI-driven network issue diagnosis by providing unified access to network data
- **Intelligent Documentation**: Generate automated reports combining real-time network state with infrastructure documentation

#### 3. **DevOps Integration & Automation** ⚙️
- **Infrastructure as Code**: Programmatic access to network infrastructure for automation workflows
- **CI/CD Integration**: Embed network management capabilities into deployment pipelines
- **Configuration Management**: Standardized API access for network device configuration and monitoring

#### 4. **Operational Efficiency** 📈
- **Role-Based Access**: Granular permissions for NOC teams (monitoring + firmware), SysAdmins (read-only), and full API access
- **Audit Trail**: Comprehensive logging of all network management operations for compliance
- **Real-Time Synchronization**: Automated synchronization between network devices and documentation systems

### 🎯 Target Scenarios

| Scenario | Description | Servers Used | Benefits |
|----------|-------------|--------------|----------|
| **Network Troubleshooting** | NOC engineer investigating connectivity issues (as shown in demo) | Catalyst Center + IOS-XE + ThousandEyes | Cross-platform correlation with performance monitoring |
| **Performance Analysis** | Network analyst monitoring application performance | ThousandEyes + Catalyst Center | End-to-end performance visibility |
| **Infrastructure Documentation** | SysAdmin updating network documentation | NetBox + Catalyst Center | Automated documentation synchronization |
| **Compliance Reporting** | IT Manager generating audit reports | All servers | Consolidated reporting across infrastructure |
| **Device Configuration** | Network engineer deploying configurations | Catalyst Center + IOS-XE | Standardized configuration management |

### 📚 Detailed Documentation

For comprehensive use case scenarios and implementation details, see:

- **📖 [Detailed Use Case Analysis](USECASE.md)** - Complete business case, technical scenarios, and success metrics
- **🔧 [IOS XE Server Guide](ios-xe-mcp-server/README.md)** - Specific documentation for direct device management capabilities
- **📊 [ThousandEyes Server Guide](thousandeyes-mcp-server/README.md)** - Comprehensive network performance monitoring and analysis
- **🤝 [Contributing Guidelines](CONTRIBUTING.md)** - How to extend use cases and add new functionality


## 🧩 Solution Components

### 🏢 Architecture
- **MCP Protocol Implementation**: Standards-based Model Context Protocol for AI integration
- **Docker Containerization**: Well-structured containers with security considerations
- **Network Isolation**: Secure communication via Docker networks
- **Role-Based Access**: Configurable permission levels for different user types

## 🚀 Installation

### 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+  
- Valid Meraki Dashboard API key
- NetBox instance with API access (for NetBox MCP Server)
- Cisco Catalyst Center with credentials (for Catalyst Center MCP Server)
- Cisco ThousandEyes with API v7 Bearer token (for ThousandEyes MCP Server)
- Cisco IOS XE device with SSH access (for IOS XE MCP Server)

### 🚀 Quick Start

#### 1. Clone the Repository

```bash
# Clone this repository
git clone https://github.com/pamosima/network-mcp-docker-suite.git
cd network-mcp-docker-suite
```

#### 2. Configure Environment Variables

Copy the environment templates and configure your API keys (only for servers you plan to deploy):

```bash
# Copy environment templates for the servers you need

# For Meraki MCP server (if using --profile meraki or --profile all)
cp meraki-mcp-server/.env.example meraki-mcp-server/.env
nano meraki-mcp-server/.env

# For NetBox MCP server (if using --profile netbox or --profile all)
cp netbox-mcp-server/.env.example netbox-mcp-server/.env
nano netbox-mcp-server/.env

# For Catalyst Center MCP server (if using --profile catc or --profile all)
cp catc-mcp-server/.env.example catc-mcp-server/.env
nano catc-mcp-server/.env

# For ThousandEyes MCP server (if using --profile thousandeyes or --profile all)
cp thousandeyes-mcp-server/.env.example thousandeyes-mcp-server/.env
nano thousandeyes-mcp-server/.env

# For IOS XE MCP server (if using --profile ios-xe or --profile all)
cp ios-xe-mcp-server/.env.example ios-xe-mcp-server/.env
nano ios-xe-mcp-server/.env
```

> 💡 **Tip**: Only configure the `.env` files for the servers you plan to deploy. For example, if you only need Meraki integration, you only need to configure `meraki-mcp-server/.env`.

Configure your actual credentials in the respective `.env` files:

**meraki-mcp-server/.env:**
```bash
MERAKI_KEY=your_actual_meraki_api_key_here
MCP_ROLE=noc
```

**netbox-mcp-server/.env:**
```bash
NETBOX_URL=https://netbox.example.com
NETBOX_TOKEN=your_netbox_token_here
```

**catc-mcp-server/.env:**
```bash
CATC_URL=https://catalyst-center.example.com
CATC_USERNAME=your_catalyst_center_username
CATC_PASSWORD=your_catalyst_center_password
```

**thousandeyes-mcp-server/.env:**
```bash
TE_TOKEN=your_thousandeyes_api_bearer_token_here
TE_BASE_URL=https://api.thousandeyes.com/v7
```

**ios-xe-mcp-server/.env:**
```bash
# Optional default device settings (credentials can also be provided per API request)
IOS_XE_HOST=192.168.1.1
IOS_XE_USERNAME=admin
IOS_XE_PASSWORD=your_device_password
MCP_HOST=0.0.0.0
MCP_PORT=8003
LOG_LEVEL=INFO
```

#### 3. Optional: Configure Custom Networks

If you need custom network settings (e.g., for integration with other applications), copy and modify the network override file:

```bash
# Copy the network configuration template (optional)
cp docker-compose.override.yml.example docker-compose.override.yml

# Edit network settings if needed
nano docker-compose.override.yml

# Create the custom network (if using external network like 'demo')
docker network create -d bridge demo
```

#### 4. Deploy the Servers

**Default behavior** - Deploy all servers:

```bash
# Deploy ALL servers (default behavior)
docker-compose up -d

# View logs for all servers
docker-compose logs -f

# Check status of all servers
docker-compose ps
```

**Selective deployment** - Use the convenience script:

```bash
# Deploy specific servers using convenience script
./deploy.sh start meraki        # Deploy only Meraki
./deploy.sh start netbox        # Deploy only NetBox  
./deploy.sh start catc          # Deploy only Catalyst Center
./deploy.sh start ios-xe        # Deploy only IOS XE
./deploy.sh start management    # Deploy Meraki + Catalyst Center
./deploy.sh start docs          # Deploy NetBox + Catalyst Center

# View logs for specific deployments
./deploy.sh logs meraki
./deploy.sh logs management

# Check status
./deploy.sh status all
```

#### 5. Verify Deployment

```bash
# Test MCP servers (check if they respond to MCP protocol)
curl http://localhost:8000/mcp    # Meraki MCP Server
curl http://localhost:8001/mcp    # NetBox MCP Server  
curl http://localhost:8002/mcp    # Catalyst Center MCP Server
curl http://localhost:8003/mcp    # IOS XE MCP Server
```

## 🎯 Deployment Options

By default, `docker-compose up -d` will start all MCP servers. For selective deployment, use the included convenience script:

### Available Profiles

| Profile | Description | Servers Deployed |
|---------|-------------|------------------|
| `all` | Deploy all servers | Meraki + NetBox + Catalyst Center + IOS XE |
| `meraki` | Deploy only Meraki server | Meraki MCP Server |
| `netbox` | Deploy only NetBox server | NetBox MCP Server |
| `catc` or `catalyst` | Deploy only Catalyst Center server | Catalyst Center MCP Server |
| `ios-xe` | Deploy only IOS XE server | IOS XE MCP Server |
| `management` | Deploy network management servers | Meraki + Catalyst Center + IOS XE |
| `docs` | Deploy documentation-focused servers | NetBox + Catalyst Center |

### Deployment Examples

```bash
# Default Docker Compose behavior
docker-compose up -d                         # Start all servers
docker-compose down                          # Stop all servers

# Selective deployment using convenience script
./deploy.sh start all                        # Start all servers
./deploy.sh start meraki                     # Start only Meraki
./deploy.sh start ios-xe                     # Start only IOS XE
./deploy.sh start management                 # Start Meraki + Catalyst Center + IOS XE
./deploy.sh start docs                       # Start NetBox + Catalyst Center

# Management operations
./deploy.sh stop meraki                      # Stop only Meraki server
./deploy.sh restart management               # Restart management servers
./deploy.sh logs docs                        # View logs for documentation servers
```

### 🚀 Convenience Script (Recommended)

For easier deployment management, use the included `deploy.sh` script:

```bash
# Make script executable (one-time setup)
chmod +x deploy.sh

# Easy deployment commands
./deploy.sh start all          # Start all servers
./deploy.sh start meraki       # Start only Meraki
./deploy.sh start management   # Start Meraki + Catalyst Center
./deploy.sh start docs         # Start NetBox + Catalyst Center

# Management commands
./deploy.sh status all         # Check status
./deploy.sh logs meraki        # View logs
./deploy.sh stop all           # Stop servers
./deploy.sh restart meraki     # Restart specific server

# Show all available options
./deploy.sh help
```

## 💻 Usage

### 🤖 Example Prompts

Here's a real-world example of how to interact with the MCP servers using natural language in AI assistants like Cursor or LibreChat:

#### **Network Troubleshooting Example**

**User Prompt:**
```
Check why wlsn-access-1.dna.its-best.ch is unreachable from Cisco Catalyst Center.
```

**AI Assistant Response:**
The AI assistant automatically uses both MCP servers working together to investigate:

1. **Catalyst Center MCP Server** - Checks device status and issues:
   ```
   🔴 Status: Unreachable (Priority P1 Active Issue)
   Device: Cisco Catalyst 9300-48UXM Switch
   IP: 10.10.254.166 (expected)
   Error: SNMP Connectivity Failed
   ```

2. **IOS XE MCP Server** - Direct SSH access to verify physical layer:
   ```python
   show_command("show cdp neighbors detail", "10.10.254.161")
   show_command("show arp | include 10.10.254", "10.10.254.161")
   # Discovers device is actually on 10.10.254.165, not .166
   ```

3. **Multi-Server Correlation** - AI correlates management system data with direct device access:
   ```
   ✅ Device is UP and operational (4 days uptime via SSH)
   ✅ Physical connectivity confirmed via CDP from border switch
   ✅ ARP table shows device at .165, not .166
   ❌ IP address mismatch: Catalyst Center expects .166, device actually at .165
   
   Root Cause: Management IP mismatch in Catalyst Center inventory
   ```

**Resolution Provided:**
- Update Catalyst Center device IP from 10.10.254.166 → 10.10.254.165
- Verify SNMP credentials match
- Re-sync device in Catalyst Center

#### **More Example Prompts**

| Scenario | Example Prompt | MCP Servers Used |
|----------|----------------|------------------|
| **Device Configuration** | *"Configure VLAN 100 on all access switches in Building A"* | Catalyst Center + IOS XE |
| **Network Health Check** | *"Show me the health status of all Meraki devices and any recent alerts"* | Meraki MCP Server |
| **Performance Analysis** | *"Show me network latency and path visualization for our main website over the last 6 hours"* | ThousandEyes MCP Server |
| **Infrastructure Audit** | *"Generate a report of all devices in NetBox that don't match Catalyst Center inventory"* | NetBox + Catalyst Center |
| **Security Compliance** | *"Check which devices have outdated firmware and create a compliance report"* | All servers |
| **Capacity Planning** | *"Show me bandwidth utilization trends for the last 30 days across all sites"* | Meraki + Catalyst Center |

#### **AI Integration Benefits**

- **🧠 Natural Language**: Ask questions in plain English instead of learning complex APIs
- **🔍 Cross-Platform Correlation**: AI automatically queries multiple systems to provide comprehensive answers
- **📊 Intelligent Analysis**: AI correlates data from different sources to identify root causes
- **⚡ Rapid Troubleshooting**: Get detailed technical analysis in seconds instead of manual investigation
- **📝 Automated Documentation**: Generate reports combining real-time data with infrastructure documentation
- **✅ Real Working Example**: The demo above shows actual production data from both Catalyst Center and direct IOS XE device access being analyzed through LibreChat

### 🌐 Server Endpoints

All MCP servers provide standardized endpoints for integration:

- **Meraki MCP Server**: `http://localhost:8000/mcp` (or `http://meraki-mcp-server:8000/mcp` within Docker network)
- **NetBox MCP Server**: `http://localhost:8001/mcp` (or `http://netbox-mcp-server:8001/mcp` within Docker network)
- **Catalyst Center MCP Server**: `http://localhost:8002/mcp` (or `http://catc-mcp-server:8002/mcp` within Docker network)
- **IOS XE MCP Server**: `http://localhost:8003/mcp` (or `http://ios-xe-mcp-server:8003/mcp` within Docker network)
- **ThousandEyes MCP Server**: `http://localhost:8004/mcp` (or `http://thousandeyes-mcp-server:8004/mcp` within Docker network)

### ⚙️ Configuration Options

### Environment Variables

#### Meraki MCP Server Variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MERAKI_KEY` | Meraki Dashboard API key | - | ✅ Yes |
| `MCP_ROLE` | Access control role (noc/sysadmin/all) | `noc` | No |
| `MERAKI_MCP_PORT` | Host port mapping for Meraki server | `8000` | No |
| `MERAKI_BASE_URL` | Meraki API base URL | `https://api.meraki.com/api/v1` | No |

#### NetBox MCP Server Variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NETBOX_URL` | NetBox instance URL | - | ✅ Yes |
| `NETBOX_TOKEN` | NetBox API token | - | ✅ Yes |
| `NETBOX_MCP_PORT` | Host port mapping for NetBox server | `8001` | No |

#### Catalyst Center MCP Server Variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CATC_URL` | Catalyst Center URL | - | ✅ Yes |
| `CATC_USERNAME` | Catalyst Center username | - | ✅ Yes |
| `CATC_PASSWORD` | Catalyst Center password | - | ✅ Yes |
| `CATC_MCP_PORT` | Host port mapping for Catalyst Center server | `8002` | No |

#### IOS XE MCP Server Variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MCP_HOST` | Server bind host | `0.0.0.0` | No |
| `MCP_PORT` | Server port | `8003` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

> **Note**: IOS XE MCP Server does not require stored credentials. Device credentials (host, username, password) are provided with each API call for enhanced security.

### Access Control Roles

- **`noc`**: Network Operations Center - monitoring + firmware upgrades
- **`sysadmin`**: System Administrator - read-only access
- **`all`**: Full API access (firehose mode)

## 📊 Docker Commands

### Basic Operations

```bash
# Start services (all servers by default)
docker-compose up -d                             # All servers
docker-compose up -d meraki-mcp-servers          # Meraki only
docker-compose up -d netbox-mcp-server           # NetBox only
docker-compose up -d catc-mcp-server             # Catalyst Center only
docker-compose up -d ios-xe-mcp-server           # IOS XE only

# Stop services
docker-compose down                              # All servers
docker-compose stop meraki-mcp-servers          # Meraki only
docker-compose stop netbox-mcp-server           # NetBox only
docker-compose stop ios-xe-mcp-server           # IOS XE only

# Restart services
docker-compose restart                           # All servers
docker-compose restart meraki-mcp-servers       # Specific server

# View logs
docker-compose logs meraki-mcp-servers          # Specific server
docker-compose logs                              # All running servers

# Follow logs in real-time
docker-compose logs -f meraki-mcp-servers       # Specific server
docker-compose logs -f                           # All running servers

# Check service status
docker-compose ps                                # All containers

# Check resource usage
docker stats meraki-mcp-server                  # Specific server
docker stats                                     # All running containers
```

### Development Operations

```bash
# Rebuild image after code changes
docker-compose build                            # All servers
docker-compose build meraki-mcp-servers         # Specific server

# Rebuild and restart
docker-compose up -d --build                    # All servers
docker-compose up -d --build meraki-mcp-servers # Meraki only

# Run without cache
docker-compose build --no-cache                 # All servers
docker-compose build --no-cache meraki-mcp-servers # Specific server

# Shell into running container
docker-compose exec meraki-mcp-servers /bin/bash
docker-compose exec netbox-mcp-server /bin/bash
docker-compose exec catc-mcp-server /bin/bash

# Run one-off commands
docker-compose run --rm meraki-mcp-servers python --version
docker-compose run --rm netbox-mcp-server python --version
```

### Maintenance Operations

```bash
# Update base images
docker-compose pull

# Clean up unused images
docker system prune

# View container resource usage
docker stats

# Export logs
docker-compose logs meraki-mcp-server > meraki-server.log
```

## 🌐 Network Access

### Quick Start: MCP Client Configuration

| **MCP Client** | **Configuration File** | **Port Range** |
|---|---|---|
| **Cursor IDE** | `~/.cursor/mcp.json` | 8000-8003 |
| **LibreChat** | `librechat.yaml` | 8000-8003 |
| **Custom Client** | HTTP transport to `localhost:PORT/mcp` | 8000-8003 |

### MCP Client Integration

For seamless integration with MCP clients (Cursor, LibreChat, etc.), all MCP servers can run on the same Docker network using Docker Compose override files.

#### Network Configuration for MCP Clients

The MCP servers can be configured to use a custom network using `docker-compose.override.yml`:

```yaml
# docker-compose.override.yml for MCP servers
services:
  meraki-mcp-servers:
    networks: ['demo']
  netbox-mcp-server:
    networks: ['demo']
  catc-mcp-server:
    networks: ['demo']
  ios-xe-mcp-server:
    networks: ['demo']
networks:
  demo:
    external: true
```

#### Example: LibreChat Integration

If using LibreChat specifically, configure it to use the same network by creating a `docker-compose.override.yml` in your LibreChat project:

```yaml
# docker-compose.override.yml for LibreChat
services:
  api:
    networks: ['demo']
  mongodb:
    networks: ['demo']
  meilisearch:
    networks: ['demo']
  vectordb:
    networks: ['demo']
  rag_api:
    networks: ['demo']
networks:
  demo:
    external: true
```

#### Example Setup Steps for LibreChat

1. **Create the shared network:**
   ```bash
   docker network create -d bridge demo
   ```

2. **Deploy MCP servers with custom network:**
   ```bash
   # Copy network configuration
   cp docker-compose.override.yml.example docker-compose.override.yml
   
   # Start MCP servers on custom network
   ./deploy.sh start all
   ```

3. **Configure your MCP client** (Cursor, LibreChat, etc.) to connect to the servers

4. **For LibreChat specifically**, add MCP servers to your `librechat.yaml`:
   ```yaml
   mcpServers:
     Meraki-MCP-Server:
       type: streamable-http
       url: http://meraki-mcp-server:8000/mcp
       timeout: 60000
     Netbox-MCP-Server:
       type: streamable-http
       url: http://netbox-mcp-server:8001/mcp
       timeout: 60000
     CatC-MCP-Server:
       type: streamable-http
       url: http://catc-mcp-server:8002/mcp
       timeout: 60000
     IOS-XE-MCP-Server:
       type: streamable-http
       url: http://ios-xe-mcp-server:8003/mcp
       timeout: 60000
   ```

5. **Restart your MCP client** to load the new MCP server configurations

#### Example: Cursor IDE Integration

For **Cursor IDE**, create or update your `~/.cursor/mcp.json` file:

```json
{
  "mcpServers": {
    "Meraki-MCP-Server": {
      "transport": "http",
      "url": "http://localhost:8000/mcp",
      "timeout": 60000
    },
    "NetBox-MCP-Server": {
      "transport": "http",
      "url": "http://localhost:8001/mcp",
      "timeout": 60000
    },
    "Catalyst-Center-MCP-Server": {
      "transport": "http",
      "url": "http://localhost:8002/mcp",
      "timeout": 60000
    },
    "IOS-XE-MCP-Server": {
      "transport": "http", 
      "url": "http://localhost:8003/mcp",
      "timeout": 60000
    }   
  }
}
```

> **💡 Pro Tips:**
> - **Cursor**: Restart Cursor after updating `mcp.json`
> - **LibreChat**: Use the web interface to restart the service
> - **All Clients**: Check logs if servers don't appear in the client

### Local Development Access

For local testing and development, all servers are accessible on the host at:

```bash
# Test MCP server availability
curl http://localhost:8000/mcp    # Meraki MCP Server
curl http://localhost:8001/mcp    # NetBox MCP Server  
curl http://localhost:8002/mcp    # Catalyst Center MCP Server
curl http://localhost:8003/mcp    # IOS XE MCP Server
```

### Network Isolation Benefits

- **Security**: Network isolation between different environments
- **Service Discovery**: Containers can communicate using service names
- **Scalability**: Easy to add more services to the same network
- **Flexibility**: Different networks for development, staging, and production

## 🔒 Security Considerations

### Container Security

- ✅ Runs as non-root user
- ✅ Security options enabled (`no-new-privileges`)
- ✅ Resource limits configured
- ✅ Network isolation via Docker networks

### Network Security

- 🔒 API key never stored in image
- 🔒 Environment variable isolation
- 🔒 Network isolation via Docker networks

### Production Security

For production deployments:

1. **Use secrets management**:
   ```bash
   # Use Docker secrets instead of environment variables
   echo "your_api_key" | docker secret create meraki_key -
   ```

2. **Firewall configuration**:
   ```bash
   # Only allow specific IPs
   iptables -A INPUT -p tcp --dport 8000 -s trusted_ip -j ACCEPT
   ```

## 📊 Monitoring and Logging

### Logging Configuration

Logs are configured with rotation to prevent disk space issues:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"  # Maximum log file size
    max-file: "3"    # Number of rotated files
```

### External Monitoring

For production monitoring, consider integrating with:

- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **ELK Stack**: Log aggregation

## 🔧 Troubleshooting

### Common Issues

#### Container Won't Start

```bash
# Check logs for errors
docker-compose logs meraki-mcp-server

# Common causes:
# 1. Missing MERAKI_KEY
# 2. Port 8000 already in use
# 3. Invalid API key
```

#### Can't Access Server

```bash
# Check if container is running
docker-compose ps

# Check port mapping
docker port meraki-mcp-server
```

#### Permission Issues

```bash
# Check file permissions
ls -la openapi/

# Fix permissions if needed
chmod 644 openapi/spec3.json
```

### Debug Mode

Enable debug logging:

```bash
# Add to .env file
LOG_LEVEL=DEBUG

# Restart container
docker-compose restart
```

### Performance Issues

Monitor resource usage:

```bash
# Check container resources
docker stats meraki-mcp-server

# Adjust limits in docker-compose.yml
```

## 🔄 Updates and Maintenance

### Updating the Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build

# Clean up old images
docker image prune
```

### Backup and Recovery

```bash
# Backup configuration
cp .env .env.backup
cp docker-compose.yml docker-compose.yml.backup

# Export container (if needed)
docker export meraki-mcp-server > meraki-backup.tar
```

## 🏗️ Advanced Deployment

### Enterprise Deployment Considerations

> **Note:** The following are recommendations for those adapting this example code for enterprise use. Additional security review and testing would be required.

1. **Use Docker Swarm or Kubernetes** for orchestration
2. **Set up monitoring** and alerting
3. **Configure log aggregation**
4. **Implement backup strategies**
5. **Use secrets management**

### Scaling

For high availability:

```bash
# Scale to multiple replicas (requires load balancer)
docker-compose up -d --scale meraki-mcp-server=3
```

## 📈 Performance Optimization

### Resource Tuning

Adjust resource limits based on your needs:

```yaml
deploy:
  resources:
    limits:
      memory: 1G      # Increase for large deployments
      cpus: '1.0'     # Increase for high load
    reservations:
      memory: 512M
      cpus: '0.5'
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### Development

For development contributions:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes with `docker-compose up -d --build`
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the Cisco Sample Code License, Version 1.1 - see the [LICENSE](LICENSE) file for details.

## 💬 Support

### Cursor IDE MCP Troubleshooting

If MCP servers aren't appearing in Cursor:

```bash
# 1. Check MCP configuration file exists
ls -la ~/.cursor/mcp.json

# 2. Validate JSON syntax
cat ~/.cursor/mcp.json | python -m json.tool

# 3. Verify server accessibility  
curl -X POST http://localhost:8000/mcp  # Meraki
curl -X POST http://localhost:8001/mcp  # NetBox
curl -X POST http://localhost:8002/mcp  # Catalyst Center
curl -X POST http://localhost:8003/mcp  # IOS XE

# 4. Check all servers are running
./deploy.sh status all

# 5. Restart Cursor completely and check logs
```

For support and questions:

1. Check the logs: `docker-compose logs meraki-mcp-server`
2. Review configuration: Check your service-specific `.env` files for API keys and settings
3. Monitor resources: `docker stats`
4. Open an issue on GitHub for bugs or feature requests

## 🙏 Acknowledgments

Special thanks to **kiskander** for the original [Meraki MCP Server](https://github.com/kiskander/meraki-mcp-server) implementation. This project builds upon that foundation to provide a containerized, multi-server deployment solution.

## ⚠️ Disclaimer

This project is part of the Cisco DevNet community and is provided as **example code** for demonstration and learning purposes. It is not officially supported by Cisco Systems and is not intended for production use without proper testing and customization for your specific environment.