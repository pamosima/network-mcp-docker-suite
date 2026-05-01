# 🌐 Network MCP Docker Suite

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/pamosima/network-mcp-docker-suite)

> **📚 Example Code for Learning & Development**  
> This is a demonstration project showcasing MCP server implementations for network management. Intended for educational purposes, testing, and development environments.

Docker-based MCP server suite for **AIOps** - enabling AI-driven network operations through Cisco Meraki, Catalyst Center, IOS XE, ISE, ThousandEyes, Splunk, NetBox & GitLab integration. AI-ready with LibreChat, Cursor, and other MCP clients for intelligent network management, automated troubleshooting, CI/CD orchestration, and operational insights.

## 🎬 Live Demo

AI-Powered Network Troubleshooting with LibreChat using Multiple MCP Servers

![Catalyst Center MCP Demo](_img/CatC-MCP_demo.gif)

*Watch how natural language queries automatically investigate and resolve network issues using both Catalyst Center MCP Server and IOS XE MCP Server. The AI assistant correlates data from management systems (Catalyst Center) with direct device access (IOS XE SSH) to identify root causes and provide comprehensive solutions.*

## 📋 Description

This **AIOps-focused** Docker suite contains eleven MCP servers (ten platform servers plus an optional **NetOps MCP Gateway**) enabling AI-driven network operations:

- **Meraki MCP Server** (8000): Cloud network management through Meraki Dashboard API - [📖 Details](meraki-mcp-server/README.md)
- **NetBox MCP Server** (8001): DCIM/IPAM infrastructure documentation and management - [📖 Details](netbox-mcp-server/README.md)
- **Catalyst Center MCP Server** (8002): Enterprise network management and assurance - [📖 Details](catc-mcp-server/README.md)
- **IOS XE MCP Server** (8003): Direct SSH-based device management - [📖 Details](ios-xe-mcp-server/README.md)
- **ThousandEyes MCP Server** (8004): Network performance monitoring and path visualization - [📖 Details](thousandeyes-mcp-server/README.md)
- **ISE MCP Server** (8005): Identity and access control operations - [📖 Details](ise-mcp-server/README.md)
- **Splunk MCP Server** (8006): Log analysis and operational intelligence - [📖 Details](splunk-mcp-server/README.md)
- **Prometheus MCP Server** (8007): Metrics queries for network monitoring ([netops-stack](https://github.com/pamosima/netops-stack)) - [📖 Details](prometheus-mcp-server/README.md)
- **ClickHouse MCP Server** (8008): Syslog and log queries for troubleshooting ([netops-stack](https://github.com/pamosima/netops-stack)) - [📖 Details](clickhouse-mcp-server/README.md)
- **GitLab MCP Server** (8009): CI/CD pipeline triggering and repository management for network automation - [📖 Details](gitlab-mcp-server/README.md)
- **NetOps MCP Gateway** (8010, optional): One MCP URL that discovers and proxies tools from the other suite servers — ideal for LibreChat with a single `mcpServers` entry - [📖 Details](netops-mcp-gateway/README.md)

All servers are containerized with flexible deployment profiles, enabling **AIOps workflows** through natural language queries, automated troubleshooting, and intelligent network analytics via AI assistants.

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
| **AI-Driven Troubleshooting** | AI assistant diagnosing interface drops or syslog errors | NetBox + Prometheus + ClickHouse | Automated correlation of topology, metrics, and logs |
| **Performance Analysis** | Network analyst monitoring application performance | ThousandEyes + Catalyst Center | End-to-end performance visibility |
| **Infrastructure Documentation** | SysAdmin updating network documentation | NetBox + Catalyst Center | Automated documentation synchronization |
| **Compliance Reporting** | IT Manager generating audit reports | All servers | Consolidated reporting across infrastructure |
| **Device Configuration** | Network engineer deploying configurations | Catalyst Center + IOS-XE | Standardized configuration management |
| **CI/CD Dry-Run** | AI assistant updating config and triggering Ansible dry-run | GitLab + NetBox + IOS-XE | Safe config preview before deployment |

### 📚 Detailed Documentation

For comprehensive use case scenarios and implementation details, see:

- **📖 [Detailed Use Case Analysis](USECASE.md)** - Complete business case, technical scenarios, and success metrics
- **☁️ [Meraki Server Guide](meraki-mcp-server/README.md)** - Cloud network management and Meraki Dashboard API integration
- **📋 [NetBox Server Guide](netbox-mcp-server/README.md)** - DCIM/IPAM documentation and infrastructure management  
- **🏢 [Catalyst Center Server Guide](catc-mcp-server/README.md)** - Enterprise network management and assurance operations
- **🔧 [IOS XE Server Guide](ios-xe-mcp-server/README.md)** - Direct SSH-based device management capabilities
- **📊 [ThousandEyes Server Guide](thousandeyes-mcp-server/README.md)** - Network performance monitoring and path visualization
- **🔐 [ISE Server Guide](ise-mcp-server/README.md)** - Identity and access control operations
- **📈 [Splunk Server Guide](splunk-mcp-server/README.md)** - Log analysis and operational intelligence monitoring
- **🦊 [GitLab Server Guide](gitlab-mcp-server/README.md)** - CI/CD pipeline triggering and repository management
- **🤝 [Contributing Guidelines](CONTRIBUTING.md)** - How to extend use cases and add new functionality

### 🔗 netops-stack Integration

This MCP suite integrates with [**netops-stack**](https://github.com/pamosima/netops-stack) - an observability and orchestration platform for network automation featuring:

- **gNMIc** - gNMI streaming telemetry collection
- **Prometheus** - Metrics storage and querying
- **ClickHouse** - Syslog and log storage via Vector
- **Grafana** - Visualization dashboards
- **GitLab CI/CD** - Ansible pipeline orchestration

**Use the `netops-stack` profile** to start MCP servers optimized for netops-stack integration:

```bash
./deploy.sh start netops-stack   # Starts MCP Servers for: ClickHouse, GitLab, IOS-XE, NetBox, Prometheus
```

| MCP Server | netops-stack Component | Purpose |
|------------|------------------------|---------|
| Prometheus MCP | Prometheus (9090) | Query interface/device metrics |
| ClickHouse MCP | ClickHouse (8123) | Query syslog messages |
| GitLab MCP | GitLab CI/CD | Trigger Ansible dry-runs |
| NetBox MCP | External SoT | Device inventory and topology |
| IOS-XE MCP | Network devices | Direct show command access |

## 🏗️ Architecture

### 📐 Deployment Architecture

The suite provides direct access to seven containerized MCP servers, perfect for development, testing, and AI-powered network operations:


```
┌─────────────────┐    ┌──────────────────────────────────┐
│                 │    │          Docker Host             │
│   MCP Client    │    │                                  │
│                 │    │  ┌─────────────────────────────┐ │
│ • Cursor IDE    │────┼─▶│ Meraki MCP        :8000     │ │
│ • LibreChat     │    │  ├─────────────────────────────┤ │
│ • Claude Desktop│────┼─▶│ NetBox MCP        :8001     │ │
│ • Other MCP     │    │  ├─────────────────────────────┤ │
│   Clients       │────┼─▶│ Catalyst Center   :8002     │ │
│                 │    │  ├─────────────────────────────┤ │
│                 │────┼─▶│ IOS XE MCP        :8003     │ │
│                 │    │  ├─────────────────────────────┤ │
│                 │────┼─▶│ ThousandEyes MCP  :8004     │ │
│                 │    │  ├─────────────────────────────┤ │
│                 │────┼─▶│ ISE MCP           :8005     │ │
│                 │    │  ├─────────────────────────────┤ │
│                 │────┼─▶│ Splunk MCP        :8006     │ │
│                 │    │  ├─────────────────────────────┤ │
│                 │────┼─▶│ Prometheus MCP    :8007     │ │
│                 │    │  ├─────────────────────────────┤ │
│                 │────┼─▶│ ClickHouse MCP    :8008     │ │
│                 │    │  ├─────────────────────────────┤ │
│                 │────┼─▶│ GitLab MCP        :8009     │ │
│                 │────┼─▶│ NetOps MCP Gateway :8010    │ │
│                 │    │  └─────────────────────────────┘ │
└─────────────────┘    └──────────────────────────────────┘
        
        Direct HTTP Connections
        ✅ Simple setup - no authentication required
        ✅ Individual server access and configuration
        ✅ Flexible port-based deployment
        ✅ Perfect for development and testing
```

### 🎯 Key Architecture Features

- **🐳 Containerized Services**: Each MCP server runs in an isolated Docker container
- **🔌 Standard MCP Protocol**: Compatible with any MCP client (Cursor, Claude Desktop, LibreChat)
- **📊 Port-Based Access**: Each server on dedicated port (8000-8009)
- **🔄 Independent Scaling**: Start/stop servers individually as needed
- **🛡️ Network Isolation**: Internal Docker network for inter-container communication
- **📝 Comprehensive Logging**: JSON-formatted logs with rotation for all services

## 🧩 Solution Components

### 🏢 Technical Stack
- **MCP Protocol Implementation**: Standards-based Model Context Protocol for AI integration
- **Docker Containerization**: Well-structured containers with security considerations and resource limits
- **Network Isolation**: Secure communication via Docker networks (mcp-network)
- **FastMCP Framework**: Modern Python-based MCP server implementation

## 🚀 Quick Start

### 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+  
- **API Access**: Valid credentials for the network platforms you want to integrate (see individual server guides for specific requirements)

### ⚡ 3-Minute Setup

```bash
# 1. Clone repository
git clone https://github.com/pamosima/network-mcp-docker-suite.git
cd network-mcp-docker-suite

# 2. Configure environment variables (single .env file for all servers)
cp .env.example .env          # Copy the environment template
nano .env                     # Edit and configure:
                             # - Set ENABLE_*_MCP=false for servers you don't want to use
                             # - Add API keys and credentials for enabled servers
# See .env.example for detailed configuration instructions

# 3. Deploy servers
./deploy.sh start all          # All servers
# OR
./deploy.sh start cisco        # Just Cisco platforms
# OR  
./deploy.sh start meraki       # Just Meraki

# 4. Verify deployment
curl http://localhost:8000/mcp    # Test Meraki server
curl http://localhost:8002/mcp    # Test Catalyst Center server
```

> 💡 **Quick Tip**: All servers now use a single centralized `.env` file for configuration. Use `ENABLE_*_MCP=false` to disable servers you don't need, and only add credentials for enabled servers.

> 🌐 **LibreChat Integration**: To use with LibreChat on an external network, see the [External Network Integration](#external-network-integration-for-librechat) section below.

## 🎯 Deployment Options

### Managing Active Servers

Control which MCP servers run using environment variables in your `.env` file:

```bash
# Enable/Disable individual servers (edit .env)
ENABLE_MERAKI_MCP=true       # Set to false to disable
ENABLE_NETBOX_MCP=true       # Set to false to disable
ENABLE_CATC_MCP=true         # Set to false to disable
ENABLE_IOS_XE_MCP=false      # Disabled - won't start
ENABLE_THOUSANDEYES_MCP=true
ENABLE_ISE_MCP=true
ENABLE_SPLUNK_MCP=false      # Disabled - won't start
ENABLE_PROMETHEUS_MCP=true   # netops-stack metrics
ENABLE_CLICKHOUSE_MCP=true   # netops-stack syslog
ENABLE_GITLAB_MCP=true       # CI/CD orchestration
ENABLE_NETOPS_MCP_GATEWAY=false  # Single MCP URL aggregating other servers (host 8010)
```

**Best Practices:**
- Set `ENABLE_*_MCP=false` for servers you don't use
- Only configure credentials for enabled servers
- Use deployment profiles (below) to start specific groups
- Reduces resource usage and attack surface

### Available Profiles

| Profile | Description | Servers Deployed | Use Case |
|---------|-------------|------------------|----------|
| `all` | Deploy all enabled servers | All suite servers including optional gateway (8000-8010) | Complete infrastructure visibility |
| `cisco` | Cisco-focused platforms | Meraki + Catalyst Center + ThousandEyes + ISE + IOS XE | Cisco-centric environments |
| `monitoring` | Network monitoring | Meraki + Catalyst Center + ThousandEyes + Splunk | Operations teams |
| `observability` | netops-stack metrics/logs | Prometheus + ClickHouse + NetBox | AI-driven troubleshooting |
| `netops-stack` | Full netops-stack integration | ClickHouse + GitLab + IOS-XE + NetBox + Prometheus | Complete AI orchestration |
| `orchestration` | CI/CD automation | GitLab + NetBox + IOS XE | Network automation workflows |
| `security` | Security-focused | Catalyst Center + ISE | Security operations |
| `management` | Traditional management | Meraki + Catalyst Center | Network management |
| `docs` | Documentation-focused | NetBox + Catalyst Center | Infrastructure documentation |

### Deployment Examples

```bash
# Flexible deployment using profiles
./deploy.sh start all                        # Complete suite
./deploy.sh start cisco                      # Cisco platforms only
./deploy.sh start monitoring                 # Monitoring focus
./deploy.sh start security                   # Security focus

# Individual servers
./deploy.sh start meraki                     # Cloud management
./deploy.sh start catc                       # Enterprise management
./deploy.sh start ios-xe                     # Direct device access

# Management operations
./deploy.sh status all                       # Check status
./deploy.sh logs cisco                       # View logs
./deploy.sh stop all                         # Stop services
```

### External Network Integration (for LibreChat)

All MCP services attach to the external **`mcp-server`** bridge (see `docker-compose.yml`). LibreChat and other tools on that network can use per-server URLs (for example `http://ise-mcp-server:8005/mcp`) or the NetOps MCP Gateway when enabled (`http://netops-mcp-gateway:8010/mcp`).

```bash
docker network create mcp-server   # once, before first up
# Optional: cp docker-compose.override.yml.example docker-compose.override.yml
docker compose up -d    # or: ./deploy.sh start all
```

**`./deploy.sh`** still filters which services start from **`ENABLE_*_MCP`** in `.env` and merges optional **`docker-compose.override.yml`**.

## 💻 Usage

### 🤖 Example Prompts

Here's a real-world example of how to interact with the MCP servers using natural language:

#### **Network Troubleshooting Example**

**User Prompt:**
```
Check why wlsn-access-1.dna.its-best.ch is unreachable from Cisco Catalyst Center.
```

**AI Assistant Response:**
The AI assistant automatically uses both MCP servers working together:

1. **Catalyst Center MCP Server** - Checks device status and issues
2. **IOS XE MCP Server** - Direct SSH access to verify physical layer  
3. **Multi-Server Correlation** - AI correlates data to identify root cause

**Resolution Identified:**
- ✅ Device is UP and operational (verified via SSH)
- ✅ Physical connectivity confirmed via CDP
- ❌ **Root Cause**: IP address mismatch in Catalyst Center inventory
- 🔧 **Solution**: Update device IP and re-sync

#### **More Example Prompts**

| Scenario | Example Prompt | Servers Used |
|----------|----------------|--------------|
| **Device Configuration** | *"Configure VLAN 100 on all access switches in Building A"* | Catalyst Center + IOS XE |
| **Performance Analysis** | *"Show me network latency for our main website over the last 6 hours"* | ThousandEyes |
| **Security Compliance** | *"Show me all non-compliant devices and their authorization profiles"* | ISE + Catalyst Center |
| **Infrastructure Audit** | *"Generate a report of devices that don't match between NetBox and reality"* | NetBox + Catalyst Center |
| **Capacity Planning** | *"Show me bandwidth utilization trends across all sites"* | Meraki + Catalyst Center |

### 🌐 Server Endpoints

| Server | Port | Endpoint | Purpose |
|--------|------|----------|---------|
| Meraki | 8000 | `http://localhost:8000/mcp` | Cloud network management |
| NetBox | 8001 | `http://localhost:8001/mcp` | DCIM/IPAM documentation |
| Catalyst Center | 8002 | `http://localhost:8002/mcp` | Enterprise management |
| IOS XE | 8003 | `http://localhost:8003/mcp` | Direct device access |
| ThousandEyes | 8004 | `http://localhost:8004/mcp` | Performance monitoring |
| ISE | 8005 | `http://localhost:8005/mcp` | Identity & access control |
| Splunk | 8006 | `http://localhost:8006/mcp` | Log analysis |
| Prometheus | 8007 | `http://localhost:8007/mcp` | Metrics queries (netops-stack) |
| ClickHouse | 8008 | `http://localhost:8008/mcp` | Syslog queries (netops-stack) |
| GitLab | 8009 | `http://localhost:8009/mcp` | CI/CD & repository management |
| NetOps MCP Gateway | 8010 | `http://localhost:8010/mcp` | Aggregated tools from enabled backends |

## 🌐 MCP Client Integration

### Cursor IDE Configuration

Create or update `~/.cursor/mcp.json`:

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
    },
    "ThousandEyes-MCP-Server": {
      "transport": "http",
      "url": "http://localhost:8004/mcp",
      "timeout": 60000
    },
    "ISE-MCP-Server": {
      "transport": "http",
      "url": "http://localhost:8005/mcp",
      "timeout": 60000
    },
    "Splunk-MCP-Server": {
      "transport": "http",
      "url": "http://localhost:8006/mcp",
      "timeout": 60000
    },
    "Prometheus-MCP-Server": {
      "transport": "http",
      "url": "http://localhost:8007/mcp",
      "timeout": 60000
    },
    "ClickHouse-MCP-Server": {
      "transport": "http",
      "url": "http://localhost:8008/mcp",
      "timeout": 60000
    },
    "GitLab-MCP-Server": {
      "transport": "http",
      "url": "http://localhost:8009/mcp",
      "timeout": 60000
    }
  }
}
```

### LibreChat Configuration  

Add to your `librechat.yaml`:

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
  ThousandEyes-MCP-Server:
    type: streamable-http
    url: http://thousandeyes-mcp-server:8004/mcp
    timeout: 60000
  ISE-MCP-Server:
    type: streamable-http
    url: http://ise-mcp-server:8005/mcp
    timeout: 60000
  Splunk-MCP-Server:
    type: streamable-http
    url: http://splunk-mcp-server:8006/mcp
    timeout: 60000
  Prometheus-MCP-Server:
    type: streamable-http
    url: http://prometheus-mcp-server:8007/mcp
    timeout: 60000
  ClickHouse-MCP-Server:
    type: streamable-http
    url: http://clickhouse-mcp-server:8008/mcp
    timeout: 60000
  GitLab-MCP-Server:
    type: streamable-http
    url: http://gitlab-mcp-server:8009/mcp
    timeout: 60000
```

## 🔧 Management Commands

### Basic Operations

```bash
# Deploy services
./deploy.sh start all          # All servers
./deploy.sh start cisco        # Cisco platforms
./deploy.sh start monitoring   # Monitoring focused

# Check status
./deploy.sh status all         # All services
docker-compose ps              # Docker status

# View logs  
./deploy.sh logs all           # All services
./deploy.sh logs meraki        # Specific server

# Stop services
./deploy.sh stop all           # All services
docker-compose down            # Docker stop

# Update and rebuild
git pull                       # Get updates
docker-compose up -d --build   # Rebuild and restart
```

### Quick Verification

```bash
# Test all servers are responding
curl http://localhost:8000/mcp    # Meraki
curl http://localhost:8001/mcp    # NetBox
curl http://localhost:8002/mcp    # Catalyst Center
curl http://localhost:8003/mcp    # IOS XE
curl http://localhost:8004/mcp    # ThousandEyes
curl http://localhost:8005/mcp    # ISE
curl http://localhost:8006/mcp    # Splunk
curl http://localhost:8007/mcp    # Prometheus
curl http://localhost:8008/mcp    # ClickHouse
curl http://localhost:8009/mcp    # GitLab
```

## 🔒 Security Considerations

### Container Security
- ✅ Runs as non-root user
- ✅ Security options enabled (`no-new-privileges`)
- ✅ Resource limits configured
- ✅ Network isolation via Docker networks

### Production Security
- 🔒 API keys loaded from environment variables only
- 🔒 Network isolation via Docker networks
- 🔒 Role-based access control (where supported)

For production deployments, consider:
1. **Secrets Management**: Use Docker secrets or external secret managers
2. **Network Security**: Implement proper firewall rules and network segmentation
3. **Monitoring**: Set up comprehensive logging and monitoring
4. **Updates**: Regular security updates and vulnerability scanning

## 🔧 Troubleshooting

### Common Issues

**Servers not responding:**
```bash
# Check if containers are running
./deploy.sh status all

# Check logs for errors
./deploy.sh logs all

# Restart problematic services
./deploy.sh restart <profile>
```

**MCP clients can't connect:**
```bash
# Verify endpoints are accessible
curl http://localhost:8000/mcp

# Check network connectivity
docker network ls
docker network inspect <network_name>

# Restart MCP client (Cursor, LibreChat, etc.)
```

**Configuration issues:**
- Check the centralized `.env` file for correct credentials
- Verify API keys and passwords are properly set (not example placeholders)
- Check individual server READMEs for detailed troubleshooting
- Verify API credentials have appropriate permissions
- Check network connectivity to target systems

## 📊 Monitoring and Maintenance

### Health Checks

```bash
# Check all services
./deploy.sh status all

# Monitor resource usage
docker stats

# View recent logs
./deploy.sh logs all | tail -100
```

### Updates

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up -d --build

# Clean up old images
docker system prune -f
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test with `docker-compose up -d --build`
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the Cisco Sample Code License, Version 1.1 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Special thanks to:

- **kiskander** for the original [Meraki MCP Server](https://github.com/kiskander/meraki-mcp-server) implementation that inspired the Meraki component of this comprehensive multi-server suite.

- **tspuhler** for the IOS XE MCP Server implementation, providing direct SSH-based device management capabilities for Cisco IOS XE devices.

- **Aditya Chellam** and **Kiran Kabdal** for the [ThousandEyes MCP Community](https://github.com/CiscoDevNet/thousandeyes-mcp-community) server implementation. The ThousandEyes MCP Server in this suite is based on their comprehensive ThousandEyes v7 API integration.

- **automateyournetwork** (John Capobianco) and **RobertBergman** for the [ISE MCP Server](https://github.com/automateyournetwork/ISE_MCP) implementation. The ISE MCP Server in this suite is based on their comprehensive ISE ERS API integration for network access control and security operations.

## ⚠️ Disclaimer

This project is part of the Cisco DevNet community and is provided as **example code** for demonstration and learning purposes. It is not officially supported by Cisco Systems and is not intended for production use without proper testing and customization for your specific environment.