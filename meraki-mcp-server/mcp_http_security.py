"""Inbound MCP HTTP bind and bearer-token controls.

Canonical copy. Each server directory also contains this file so Docker
build contexts (per-server) can import it as ``mcp_http_security``.
"""

from __future__ import annotations

import hmac
import ipaddress
import os
from typing import Any, Callable, Optional, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def is_loopback_bind(host: str) -> bool:
    """True for localhost, ::1, and 127.0.0.0/8. 0.0.0.0 is not loopback."""
    value = (host or "").strip().lower()
    if not value:
        return False
    if value in {"localhost", "::1", "0:0:0:0:0:0:0:1"}:
        return True
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1]
    try:
        return ipaddress.ip_address(value).is_loopback
    except ValueError:
        return False


def mcp_api_token() -> str:
    return os.getenv("MCP_API_TOKEN", "").strip()


def _mcp_api_token_middleware_class():
    from fastmcp.exceptions import AuthorizationError
    from fastmcp.server.dependencies import get_http_request
    from fastmcp.server.middleware import Middleware

    class McpApiTokenMiddleware(Middleware):
        """Require Authorization: Bearer <MCP_API_TOKEN> on every HTTP MCP request."""

        def __init__(self, token: str) -> None:
            super().__init__()
            self._token = token

        async def on_request(self, context: Any, call_next: Any) -> Any:
            request = None
            try:
                request = get_http_request()
            except Exception:
                request = None

            if request is None:
                raise AuthorizationError(
                    "MCP API token auth requires HTTP transport requests"
                )

            authz: Optional[str] = request.headers.get("authorization")
            if not authz or not authz.startswith("Bearer "):
                raise AuthorizationError("Missing bearer token")

            presented = authz[7:].strip()
            if not presented or not hmac.compare_digest(presented, self._token):
                raise AuthorizationError("Invalid bearer token")

            return await call_next(context)

    return McpApiTokenMiddleware


def apply_mcp_http_security(mcp: Any, host: str) -> str:
    """Refuse non-loopback binds without a token; attach Bearer middleware.

    Loopback binds stay token-optional for local Cursor/dev use.
    """
    token = mcp_api_token()
    if not is_loopback_bind(host):
        if not token:
            raise RuntimeError(
                "MCP_API_TOKEN is required when MCP_HOST is not loopback "
                f"(got {host!r}). Bind 127.0.0.1 for local-only access, or set "
                "MCP_API_TOKEN and send Authorization: Bearer <token>."
            )
        mcp.add_middleware(_mcp_api_token_middleware_class()(token))
    return host


def register_mutating_tool(mcp: Any, enabled: bool) -> Callable[[F], F]:
    """Register an MCP tool only when the write opt-in flag is true."""

    def decorator(fn: F) -> F:
        if enabled:
            return mcp.tool()(fn)
        return fn

    return decorator
