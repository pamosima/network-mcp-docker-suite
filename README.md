# Meraki MCP Server

A Model Context Protocol (MCP) server that exposes a curated subset of the Cisco Meraki Dashboard API to MCP-aware clients (e.g., Cursor, Claude Desktop). It provides role-based access to ensure safe and scoped operations.

## Features
- Role-based access control (noc | sysadmin | all)
- OpenAPI-driven tool generation (using the bundled spec)
- Global schema validation bypass to tolerate Meraki `null` values (prevents "None is not of type 'string'")
- Simple configuration via environment variables

## Requirements
- Python 3.10+
- A Meraki Dashboard API key with appropriate org access
- Optional: `uv` for reproducible Python environments (recommended)

## Install

### Option A: Using uv (recommended)
```bash
# 1) Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2) From project root
cd /path/to/your/meraki-mcp-server

# 3) Create and sync the environment based on pyproject.toml / uv.lock
uv sync
```

### Option B: Using pip (fallback)
```bash
# 1) Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2) Install dependencies
pip install fastmcp httpx jsonschema
```

## Configure
Set environment variables (you can export them in your shell or supply via your MCP client config):

- `MERAKI_KEY` (required): Your Meraki Dashboard API key
- `MCP_ROLE` (optional): One of `noc`, `sysadmin`, `all` (defaults to `noc`)
- `MERAKI_BASE_URL` (optional): Defaults to `https://api.meraki.com/api/v1`

Example (macOS/Linux):
```bash
export MERAKI_KEY="<your-meraki-api-key>"
export MCP_ROLE="noc"     # or sysadmin | all
```

## Quick Run (smoke test)
You can quickly validate the server starts locally (even outside an MCP client):
```bash
# Using uv
uv run python meraki_mcp_server.py

# Or with plain Python (ensure venv is active)
python3 meraki_mcp_server.py
```
This will start the MCP server process. Typically, you run this via an MCP client over stdio.

## MCP Client Configuration
Below is an example `mcp_server_config.json` entry you can adapt in your MCP client (e.g., Cursor, Claude Desktop). Ensure you replace the directory path with your actual project location.

```json
{
  "Meraki-MCP-Server": {
    "command": "uv",
    "env": {
      "MERAKI_KEY": "${MERAKI_KEY}",
      "MERAKI_BASE_URL": "https://api.meraki.com/api/v1",
      "MCP_ROLE": "noc",
      "_comment": "Set MERAKI_KEY in your shell env. MCP_ROLE values: noc | sysadmin | all"
    },
    "args": [
      "--directory",
      "/path/to/yourMCPdirector/meraki-mcp-server",
      "run",
      "python",
      "meraki_mcp_server.py",
      "stdio"
    ]
  }
}
```

Notes:
- The `${MERAKI_KEY}` placeholder means your MCP client will inherit the key from your shell environment.
- `stdio` at the end ensures the server communicates over standard I/O as MCP expects.
- If you do not use `uv`, replace `command` and `args` accordingly to invoke your Python environment.

## Roles and Allowed Endpoints
The server uses route maps to constrain access:

- `noc` (default):
  - GET `/organizations`
  - GET `/organizations/{orgId}/networks`
  - GET `/organizations/{orgId}/devices`
  - GET `/organizations/{orgId}/firmware/upgrades`
  - GET `/organizations/{orgId}/licenses/overview`
  - PUT `/networks/{networkId}/firmwareUpgrades`
  - All other endpoints are blocked

- `sysadmin`:
  - Same read endpoints as `noc`, but with PUT operations blocked (read-only)

- `all`:
  - Firehose mode. All endpoints allowed (use with caution)

You can switch roles by setting `MCP_ROLE` before launching the server.

## Validation Behavior
Meraki may return `null` for some fields the official schema marks as strings. To avoid frequent validation errors (e.g., `None is not of type 'string'`), this server disables JSON schema output validation globally. This keeps tools responsive and avoids brittle schema mismatches.

If you prefer strict validation, remove the monkey patch in `meraki_mcp_server.py` and update the OpenAPI spec to mark nullable string fields explicitly.

## Security
- Never commit your API key. Use environment variables.
- Limit the server’s accessible endpoints by using the appropriate role.
- Consider running this behind a process supervisor and restricting filesystem/network access where appropriate.

## Troubleshooting
- Import errors (e.g., RouteType vs MCPType): This project is pinned to the FastMCP API compatible with `MCPType`. If your local FastMCP differs, install the version specified in `pyproject.toml`/`uv.lock`.
- Validation errors: By design, validation is disabled to tolerate Meraki `null`s. If you still see validation errors, ensure you’re running the current `meraki_mcp_server.py`.

## License
MIT (or your preferred license)
