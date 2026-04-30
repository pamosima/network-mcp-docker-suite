# MCP Suite Gateway — aggregates tools from other MCP servers in this suite
FROM python:3.12-slim@sha256:7026274c107626d7e940e0e5d6730481a4600ae95d5ca7eb532dd4180313fea9

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY pyproject.toml ./
RUN uv sync

COPY suite_gateway_mcp_server.py ./

RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

EXPOSE 8010

ENV PYTHONPATH=/app
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8010
ENV SUITE_GATEWAY_USE_DEFAULT_BACKENDS=true

CMD ["uv", "run", "python", "suite_gateway_mcp_server.py"]
