# 🐳 Multi-MCP Server - Docker Deployment

Multi-MCP Server implementation providing Cisco Meraki Dashboard API and NetBox DCIM/IPAM functionality through Model Context Protocol (MCP) servers. This project enables seamless integration with LibreChat and other MCP-compatible applications for network management and infrastructure documentation.

## 📋 Description

This repository contains two production-ready MCP servers designed for Cisco DevNet community use:

- **Meraki MCP Server**: Provides comprehensive access to Cisco Meraki Dashboard API functionality including device management, network monitoring, and configuration operations
- **NetBox MCP Server**: Enables complete NetBox DCIM/IPAM capabilities for infrastructure documentation, IP address management, and device lifecycle tracking

Both servers are containerized using Docker and designed for easy deployment with LibreChat network integration, supporting role-based access control and production-grade security features.

## 🎯 Use Case

Network administrators and DevOps teams need streamlined access to network infrastructure data and management capabilities. This solution provides:

- **Unified Network Management**: Single interface for both Meraki cloud and on-premises NetBox systems
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

### 🚀 Quick Start

#### 1. Clone the Repository

```bash
# Clone this repository
git clone https://github.com/your-username/devnet-mcp-servers.git
cd devnet-mcp-servers
```

#### 2. Configure Environment Variables

Copy the environment templates and configure your API keys:

```bash
# Copy Meraki environment template
cp meraki-mcp-server/.env.example meraki-mcp-server/.env

# Copy NetBox environment template  
cp netbox-mcp-server/.env.example netbox-mcp-server/.env

# Edit the Meraki configuration
nano meraki-mcp-server/.env

# Edit the NetBox configuration
nano netbox-mcp-server/.env
```

Configure your actual API keys in the respective `.env` files:

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

#### 3. Optional: Configure Custom Networks

If you need custom network settings (e.g., for LibreChat integration), copy and modify the network override file:

```bash
# Copy the network configuration template (optional)
cp docker-compose.override.yml.example docker-compose.override.yml

# Edit network settings if needed
nano docker-compose.override.yml
```

#### 4. Deploy the Servers

```bash
# Build and start both servers in background
docker-compose up -d

# View logs for both servers
docker-compose logs -f

# View logs for specific server
docker-compose logs -f meraki-mcp-server
docker-compose logs -f netbox-mcp-server

# Check status
docker-compose ps
```

#### 5. Verify Deployment

```bash
# Test Meraki MCP Server
curl http://localhost:8000/health

# Test NetBox MCP Server  
curl http://localhost:8001/health
```

## 💻 Usage

### 🌐 Server Endpoints

Both MCP servers provide standardized endpoints for integration:

- **Meraki MCP Server**: `http://localhost:8000` (or `http://meraki-mcp-server:8000` within Docker network)
- **NetBox MCP Server**: `http://localhost:8001` (or `http://netbox-mcp-server:8001` within Docker network)

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

### Access Control Roles

- **`noc`**: Network Operations Center - monitoring + firmware upgrades
- **`sysadmin`**: System Administrator - read-only access
- **`all`**: Full API access (firehose mode)

## 📊 Docker Commands

### Basic Operations

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs meraki-mcp-server

# Follow logs in real-time
docker-compose logs -f meraki-mcp-server

# Check service status
docker-compose ps

# Check resource usage
docker stats meraki-mcp-server
```

### Development Operations

```bash
# Rebuild image after code changes
docker-compose build

# Rebuild and restart
docker-compose up -d --build

# Run without cache
docker-compose build --no-cache

# Shell into running container
docker-compose exec meraki-mcp-server /bin/bash

# Run one-off commands
docker-compose run --rm meraki-mcp-server python --version
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

Both servers are configured to run on the `librechat_default` network and can be accessed by other containers at:

```bash
# Meraki MCP Server
http://meraki-mcp-server:8000

# NetBox MCP Server
http://netbox-mcp-server:8001
```

### Local Development

For local testing, both servers are accessible on the host at:

```bash
# Meraki MCP Server
open http://localhost:8000

# NetBox MCP Server  
open http://localhost:8001
```

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