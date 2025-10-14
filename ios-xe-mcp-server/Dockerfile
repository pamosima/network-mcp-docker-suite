# IOS XE MCP Server - Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    openssh-client \
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
EXPOSE 8003

# Set environment variables
ENV PYTHONPATH=/app
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8003

# Run the IOS XE MCP server
CMD ["uv", "run", "python", "ios_xe_mcp_server.py"]
