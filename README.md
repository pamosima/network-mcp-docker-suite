# 🐳 Meraki MCP Server - Docker Deployment

This guide explains how to deploy the Meraki MCP Server SSE version using Docker and Docker Compose.

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Valid Meraki Dashboard API key

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Navigate to the project directory
cd meraki-mcp-server

# Copy the Docker environment template
cp .env.example .env

# Edit with your Meraki API key
nano .env  # or use your preferred editor
```

### 2. Configure Environment

Edit the `.env` file with your configuration:

```bash
# Required: Your Meraki API key
MERAKI_KEY=your_actual_api_key_here

# Optional: Access control role
MCP_ROLE=noc

# Optional: Custom port (default: 8000)
MCP_PORT=8000
```

### 3. Start the Server

```bash
# Build and start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 4. Test the Deployment

```bash
# Or open in browser
open http://localhost:8000
```

## 🔧 Configuration Options

### Environment Variables

The Docker deployment supports all the same environment variables as the native deployment:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MERAKI_KEY` | Meraki Dashboard API key | - | ✅ Yes |
| `MCP_ROLE` | Access control role (noc/sysadmin/all) | `noc` | No |
| `MCP_PORT` | Host port mapping | `8000` | No |
| `MERAKI_BASE_URL` | Meraki API base URL | `https://api.meraki.com/api/v1` | No |

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

The server is configured to run on the `librechat_default` network and can be accessed by other containers at:

```
http://meraki-mcp-server:8000
```

### Local Development

For local testing, the server is also accessible on the host at:

```bash
# Open test page
open http://localhost:8000
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

## 🤝 Support

If you encounter issues:

1. Check the logs: `docker-compose logs meraki-mcp-server`
2. Verify configuration: Review your `.env` file
3. Check resources: `docker stats`