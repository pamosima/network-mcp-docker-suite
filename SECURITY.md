# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
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

1. **Never expose MCP servers directly to the internet** - Use them behind a reverse proxy or VPN
2. **Use environment variables for secrets** - Never hardcode credentials
3. **Keep images updated** - Regularly pull latest versions
4. **Network isolation** - Run MCP servers in isolated Docker networks
5. **Least privilege** - Use read-only tokens where possible (e.g., `IOS_XE_READ_ONLY=true`)

### Security Features

This project includes several security measures:

- **Non-root containers**: All containers run as non-root users
- **Input validation**: SQL injection prevention, command sanitization
- **Rate limiting**: Abuse prevention on sensitive operations
- **Allowlists**: Restricted file paths and pipeline variables
- **No credential exposure**: Secrets loaded from environment only

## Security Contacts

- Repository: https://github.com/pamosima/network-mcp-docker-suite
- Maintainer: @pamosima
