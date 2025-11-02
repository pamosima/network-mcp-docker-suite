# Splunk MCP Proxy Server

A lightweight proxy server that bridges LibreChat to Splunk's native MCP implementation.

## Overview

This server acts as a transparent proxy between LibreChat (using HTTP transport) and Splunk's MCP backend (using HTTPS with Bearer token authentication). It handles:

- SSL certificate validation for self-signed certificates
- Bearer token authentication to Splunk
- Protocol translation between LibreChat and Splunk MCP
- Clean HTTP interface on port 8006

## Features

✅ **Transparent Proxying**: Forwards all MCP requests to Splunk backend  
✅ **SSL Handling**: Manages self-signed certificate validation  
✅ **Authentication**: Adds Bearer token authentication automatically  
✅ **Health Checks**: Built-in `/health` endpoint for monitoring  
✅ **Logging**: Comprehensive logging for debugging  

## Available Tools (from Splunk MCP backend)

The Splunk MCP Server (v0.2.4) provides 9 tools:

1. **get_splunk_info** - Get comprehensive Splunk instance information
2. **get_indexes** - List all Splunk indexes
3. **get_index_info** - Get detailed information about a specific index
4. **get_user_list** - Get list of Splunk users
5. **get_user_info** - Get current user information
6. **run_splunk_query** - Execute SPL queries (main search tool)
7. **get_metadata** - Retrieve metadata about hosts, sources, sourcetypes
8. **get_kv_store_collections** - Get KV Store statistics
9. **get_knowledge_objects** - Retrieve knowledge objects (saved searches, alerts, etc.)

## Configuration

### Environment Variables

```bash
# Splunk Backend
SPLUNK_HOST=splunk.company.com       # Splunk server hostname/IP
SPLUNK_PORT=8089                     # Splunk management port
SPLUNK_API_KEY=your_bearer_token     # Splunk Bearer token
SPLUNK_VERIFY_SSL=false              # SSL certificate verification

# Proxy Server
MCP_HOST=0.0.0.0                     # Listen on all interfaces
MCP_PORT=8006                        # Proxy server port
```

### Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your Splunk credentials:
   ```bash
   SPLUNK_HOST=your-splunk-host
   SPLUNK_API_KEY=your_actual_bearer_token
   ```

3. Build and run:
   ```bash
   docker build -t splunk-mcp-server .
   docker run -d -p 8006:8006 --env-file .env splunk-mcp-server
   ```

## Testing

### Health Check
```bash
curl http://localhost:8006/health
```

### Test MCP Initialize
```bash
curl -X POST http://localhost:8006/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

### List Tools
```bash
curl -X POST http://localhost:8006/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

## Integration with LibreChat

Add to `librechat.yaml`:

```yaml
mcpServers:
  Splunk-MCP-Server:
    type: streamable-http
    url: http://splunk-mcp-server:8006/mcp
    timeout: 60000
```

Add to `docker-compose.yml`:

```yaml
  splunk-mcp-server:
    image: splunk-mcp-server:latest
    container_name: splunk-mcp-server
    environment:
      - SPLUNK_HOST=splunk.company.com
      - SPLUNK_PORT=8089
      - SPLUNK_API_KEY=${SPLUNK_API_KEY}
      - SPLUNK_VERIFY_SSL=false
      - MCP_PORT=8006
    ports:
      - "8006:8006"
    networks:
      - demo
    restart: unless-stopped
```

## Architecture

```
LibreChat (HTTP) → Splunk MCP Proxy (port 8006) → Splunk MCP Backend (HTTPS, port 8089)
                    └─ Adds Bearer Auth
                    └─ Handles SSL
                    └─ Transparent proxy
```

## Troubleshooting

### Check logs
```bash
docker logs splunk-mcp-server
```

### Test Splunk connectivity
```bash
curl -k https://splunk.company.com:8089/services/mcp \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Common Issues

1. **Connection refused**: Check SPLUNK_HOST and SPLUNK_PORT
2. **401 Unauthorized**: Verify SPLUNK_API_KEY is correct
3. **SSL errors**: Ensure SPLUNK_VERIFY_SSL=false for self-signed certs

## License

Part of the network-mcp-docker-suite
Author: Patrick Mosimann

