# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.5.x   | :white_check_mark: |
| 1.4.x   | :white_check_mark: |
| 1.3.x   | :white_check_mark: |
| < 1.3   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

1. **Do NOT** create a public GitHub issue for security vulnerabilities
2. Email the maintainer directly or use GitHub's private vulnerability reporting feature
3. Include as much detail as possible:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment**: Within 48 hours of your report
- **Initial Assessment**: Within 7 days
- **Resolution Timeline**: Depends on severity
  - Critical: 24-48 hours
  - High: 7 days
  - Medium: 30 days
  - Low: 90 days

### Security Best Practices for Users

When deploying these MCP servers:

1. **Bind to loopback unless you intentionally expose the service** - Compose publishes `127.0.0.1:<port>:<port>`. Native Python defaults to `127.0.0.1`.
2. **Set `MCP_API_TOKEN` for any non-loopback bind** - Docker Compose sets `MCP_HOST=0.0.0.0` inside the container so published ports work. That bind is not loopback, so the process refuses to start without a token. Clients send `Authorization: Bearer <token>`.
3. **Use environment variables for secrets** - Never hardcode credentials. Placeholder comments only (for example `change-me-if-exposed`).
4. **Keep write tools disabled unless you need them**
   - `IOS_XE_READ_ONLY=true` (default) — `config_command` is not registered
   - `NETBOX_ENABLE_WRITES=false` (default)
   - `CATC_ENABLE_WRITES=false` (default)
   - `GITLAB_ENABLE_WRITES=false` (default)
   - `MCP_ROLE=sysadmin` (default, read-only). `noc` and `all` are write opt-in
5. **ClickHouse** - Use `mcp_readonly` (see `clickhouse/users.d/mcp-readonly.xml`). Do not use the default superuser or an empty password. Queries are allowlisted parameterized templates; there is no raw SQL tool.
6. **Keep images updated** - Regularly pull latest versions
7. **Network isolation** - Run MCP servers in isolated Docker networks
8. **Least privilege** - Use read-only backend tokens where possible

Publishing host ports on `0.0.0.0` is an explicit operator choice. It still requires `MCP_API_TOKEN`.

### Security Features

This project includes several security measures:

- **Non-root containers**: All containers run as non-root users
- **Fail-closed HTTP auth**: Bearer token middleware on non-loopback binds
- **Loopback host publish**: Compose maps ports to `127.0.0.1` by default
- **Input validation**: Parameterized ClickHouse queries, command sanitization
- **Allowlists**: Restricted file paths and pipeline variables
- **Write opt-in**: Mutating tools are unregistered until an env flag enables them
- **No credential exposure**: Secrets loaded from environment only

### Advisory

Unauthenticated MCP-over-HTTP on published ports is tracked as [GHSA-5rxh-p2hm-g7gr](https://github.com/pamosima/network-mcp-docker-suite/security/advisories/GHSA-5rxh-p2hm-g7gr). Upgrade to **v1.5.0** or later.

## Security Contacts

- Repository: https://github.com/pamosima/network-mcp-docker-suite
- Maintainer: @pamosima
