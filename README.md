# 🐳 Multi-MCP Server - Docker Deployment

Multi-MCP Server implementation providing Cisco Meraki Dashboard API, NetBox DCIM/IPAM, Cisco Catalyst Center, and IOS XE device management functionality through Model Context Protocol (MCP) servers. This project enables seamless integration with LibreChat and other MCP-compatible applications for comprehensive network management and infrastructure documentation.

## 📋 Description

This repository contains four production-ready MCP servers designed for Cisco DevNet community use:

- **Meraki MCP Server**: Provides comprehensive access to Cisco Meraki Dashboard API functionality including device management, network monitoring, and configuration operations
- **NetBox MCP Server**: Enables complete NetBox DCIM/IPAM capabilities for infrastructure documentation, IP address management, and device lifecycle tracking
- **Catalyst Center MCP Server**: Delivers full Cisco Catalyst Center (DNA Center) functionality including network device management, site topology, client analytics, and network assurance
- **IOS XE MCP Server**: Enables direct SSH-based management of Cisco IOS XE devices including configuration changes, monitoring commands, and device information retrieval

All servers are containerized using Docker with flexible deployment profiles, designed for easy integration with LibreChat and supporting role-based access control and production-grade security features.

## 🎯 Use Case

Network administrators and DevOps teams need streamlined access to network infrastructure data and management capabilities. This solution provides:

- **Unified Network Management**: Single interface for Meraki cloud, on-premises NetBox systems, Catalyst Center management, and direct IOS-XE device control
- **Automated Documentation**: Real-time synchronization between network devices and documentation systems  
- **Role-Based Operations**: Granular access control for different operational teams (NOC, SysAdmin, etc.)
- **Integration Ready**: MCP protocol compatibility enables integration with AI assistants and automation platforms

## 🧩 Solution Components

### 🏢 Architecture
- **MCP Protocol Implementation**: Standards-based Model Context Protocol for AI integration
- **Docker Containerization**: Production-ready containers with security hardening
- **Network Isolation**: Secure communication via Docker networks
- **Role-Based Access**: Configurable permission levels for different user types

## 🚀 Installation

### 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+  
- Valid Meraki Dashboard API key
- NetBox instance with API access (for NetBox MCP Server)
- Cisco Catalyst Center with credentials (for Catalyst Center MCP Server)
- Cisco IOS XE device with SSH access (for IOS XE MCP Server)

### 🚀 Quick Start

#### 1. Clone the Repository

```bash
# Clone this repository
git clone https://github.com/your-username/devnet-mcp-servers.git
cd devnet-mcp-servers
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
CATC_URL=https://dnac.example.com
CATC_USERNAME=your_catalyst_center_username
CATC_PASSWORD=your_catalyst_center_password
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

If you need custom network settings (e.g., for LibreChat integration), copy and modify the network override file:

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

### 🌐 Server Endpoints

All MCP servers provide standardized endpoints for integration:

- **Meraki MCP Server**: `http://localhost:8000/mcp` (or `http://meraki-mcp-server:8000/mcp` within Docker network)
- **NetBox MCP Server**: `http://localhost:8001/mcp` (or `http://netbox-mcp-server:8001/mcp` within Docker network)
- **Catalyst Center MCP Server**: `http://localhost:8002/mcp` (or `http://catc-mcp-server:8002/mcp` within Docker network)
- **IOS XE MCP Server**: `http://localhost:8003/mcp` (or `http://ios-xe-mcp-server:8003/mcp` within Docker network)

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

### LibreChat Integration

For seamless integration with LibreChat, all MCP servers can run on the same Docker network using Docker Compose override files.

#### MCP Servers Network Configuration

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

#### LibreChat Network Configuration

Configure LibreChat to use the same network by creating a `docker-compose.override.yml` in your LibreChat project:

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

#### Setup Steps for LibreChat Integration

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

3. **Configure LibreChat** with the override file above and deploy it

4. **Update LibreChat configuration** by adding MCP servers to your `librechat.yaml`:
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

5. **Restart LibreChat** to load the new MCP server configurations

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

## 🏗️ Production Deployment

### Recommended Production Setup

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

For support and questions:

1. Check the logs: `docker-compose logs meraki-mcp-server`
2. Review configuration: Check your service-specific `.env` files for API keys and settings
3. Monitor resources: `docker stats`
4. Open an issue on GitHub for bugs or feature requests

## 🙏 Acknowledgments

Special thanks to **kiskander** for the original [Meraki MCP Server](https://github.com/kiskander/meraki-mcp-server) implementation. This project builds upon that foundation to provide a containerized, multi-server deployment solution.

## ⚠️ Disclaimer

This project is part of the Cisco DevNet community and is not officially supported by Cisco Systems. Use at your own risk in production environments.