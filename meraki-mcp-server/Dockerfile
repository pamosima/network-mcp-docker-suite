# Meraki MCP Server SSE - Dockerfile
FROM python:3.14-slim@sha256:584e89d31009a79ae4d9e3ab2fba078524a6c0921cb2711d05e8bb5f628fc9b9

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (modern Python package manager)
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install Python dependencies using uv
RUN uv sync --frozen

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose the SSE server port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

# Run the MCP server
CMD ["uv", "run", "python", "meraki_mcp_server.py"]
