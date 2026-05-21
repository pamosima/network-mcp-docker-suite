"""
NetOps MCP Gateway — single entrypoint that aggregates tools from other MCP servers.

Implements the multi-backend pattern described in Cisco's MCP reference architecture
(MultiServer MCP client / REST bridge): one FastMCP server discovers `tools/list` from
each configured backend over HTTP, builds an in-memory tool catalog, and forwards `tools/call`.

Environment:
- MCP_HOST / MCP_PORT: bind for this gateway (default 0.0.0.0:8010)
- SUITE_GATEWAY_BACKENDS: JSON list of {"alias": "meraki", "url": "http://host:8000/mcp"}
  If unset and SUITE_GATEWAY_USE_DEFAULT_BACKENDS=true (default in Docker), uses Docker
  Compose service hostnames for all suite servers on the default bridge.
- SUITE_GATEWAY_VERIFY_HTTP: verify TLS for backend calls (default false for internal http://)
- SUITE_GATEWAY_REQUEST_TIMEOUT: seconds per backend HTTP call (default 120)
- SUITE_GATEWAY_MAX_TOOLS_PER_BACKEND: cap catalog entries per backend (default 96)
- Tool surface: always suite_list_backends / suite_search_tools / suite_call_tool plus five suite_flow_*
  playbook tools (same Markdown as netops://flows/* resources). suite_search_tools supports
  detail_level=name|summary|full plus legacy include_input_schema.
- SUITE_GATEWAY_NORMALIZE_TOOL_RESULTS: unwrap nested MCP text/JSON tool results from backends (default true).
- SUITE_GATEWAY_NORMALIZE_MAX_DEPTH: max unwrap iterations (default 12, max 32).

Playbooks: MCP resources under netops://flows/ (overview, troubleshoot, compact, backends, clients)
plus server instructions in initialize metadata.

Author: Network MCP Docker Suite
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
import uuid
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

import httpx
from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan

import netops_mcp_gateway_flow_resources as gateway_flows

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("netops-mcp-gateway")

DEFAULT_DOCKER_BACKENDS: list[dict[str, str]] = [
    {"alias": "meraki", "url": "http://meraki-mcp-servers:8000/mcp"},
    {"alias": "netbox", "url": "http://netbox-mcp-server:8001/mcp"},
    {"alias": "catc", "url": "http://catc-mcp-server:8002/mcp"},
    {"alias": "ios_xe", "url": "http://ios-xe-mcp-server:8003/mcp"},
    {"alias": "thousandeyes", "url": "http://thousandeyes-mcp-server:8004/mcp"},
    {"alias": "ise", "url": "http://ise-mcp-server:8005/mcp"},
    {"alias": "splunk", "url": "http://splunk-mcp-server:8006/mcp"},
    {"alias": "prometheus", "url": "http://prometheus-mcp-server:8007/mcp"},
    {"alias": "clickhouse", "url": "http://clickhouse-mcp-server:8008/mcp"},
    {"alias": "gitlab", "url": "http://gitlab-mcp-server:8009/mcp"},
]

MCP_ACCEPT = "application/json, text/event-stream"
PROTOCOL_VERSION = "2025-03-26"


def load_dotenv_file(env_file: str | None = None) -> bool:
    path = env_file or os.getenv("DOTENV_PATH", ".env")
    env_path = Path(path)
    if not env_path.exists():
        return False
    try:
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("\"'")
                if key and key not in os.environ:
                    os.environ[key] = value
        logger.info("Loaded environment from %s", env_path)
        return True
    except OSError as e:
        logger.warning("Could not read .env: %s", e)
        return False


def _safe_segment(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_]", "_", (name or "tool").strip())
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        s = "tool"
    if s[0].isdigit():
        s = "t_" + s
    return s[:80]


def _parse_jsonrpc_result(body_text: str, expect_id: Any) -> Any:
    """Parse JSON-RPC result from a plain JSON body or SSE (event/message + data: lines)."""
    text = (body_text or "").strip()
    if not text:
        raise RuntimeError("empty MCP HTTP response body")

    def _match_id(obj_id: Any) -> bool:
        return obj_id == expect_id or str(obj_id) == str(expect_id)

    if text.startswith("{"):
        try:
            obj = json.loads(text)
            if isinstance(obj, dict) and "jsonrpc" in obj and _match_id(obj.get("id")):
                if obj.get("error"):
                    raise RuntimeError(obj["error"])
                return obj.get("result")
        except json.JSONDecodeError:
            pass

    for block in text.split("\n\n"):
        for line in block.split("\n"):
            line = line.strip()
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            try:
                obj = json.loads(payload)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and _match_id(obj.get("id")):
                if obj.get("error"):
                    raise RuntimeError(obj["error"])
                return obj.get("result")
    raise RuntimeError(f"no JSON-RPC result for id={expect_id!r} in response")


def _normalize_tool_results_enabled() -> bool:
    return os.getenv("SUITE_GATEWAY_NORMALIZE_TOOL_RESULTS", "true").lower() in ("1", "true", "yes")


def _normalize_max_depth() -> int:
    try:
        n = int(os.getenv("SUITE_GATEWAY_NORMALIZE_MAX_DEPTH", "12"))
    except ValueError:
        n = 12
    return max(1, min(n, 32))


def _normalize_proxied_tool_result(result: Any) -> Any:
    """
    Flatten nested MCP CallToolResult shapes: a dict with a single text content block
    whose body is JSON may be another such dict (FastMCP backend wrapping tool output).
    Stops at isError payloads, multi-block content, or non-JSON text.
    """
    if not _normalize_tool_results_enabled():
        return result

    cur: Any = result
    for _ in range(_normalize_max_depth()):
        if not isinstance(cur, dict):
            break
        if cur.get("isError") is True:
            break
        content = cur.get("content")
        if not isinstance(content, list) or len(content) != 1:
            break
        block = content[0]
        if not isinstance(block, dict) or block.get("type") != "text":
            break
        txt = block.get("text")
        if not isinstance(txt, str):
            break
        s = txt.strip()
        if not (s.startswith("{") or s.startswith("[")):
            break
        try:
            parsed: Any = json.loads(s)
        except json.JSONDecodeError:
            break
        if parsed == cur:
            break
        cur = parsed
    return cur


class BackendMCPClient:
    """Minimal async MCP client over HTTP (supports SSE responses used by FastMCP)."""

    def __init__(self, httpx_client: httpx.AsyncClient, base_url: str) -> None:
        self._client = httpx_client
        base = base_url.rstrip("/")
        self.mcp_url = base if base.endswith("/mcp") else f"{base}/mcp"
        self._session_id: str | None = None

    async def _rpc(self, method: str, params: dict[str, Any] | None) -> Any:
        rpc_id = str(uuid.uuid4())
        payload = {"jsonrpc": "2.0", "id": rpc_id, "method": method, "params": params or {}}
        headers = {
            "Content-Type": "application/json",
            "Accept": MCP_ACCEPT,
        }
        if self._session_id:
            headers["mcp-session-id"] = self._session_id

        r = await self._client.post(
            self.mcp_url,
            json=payload,
            headers=headers,
        )
        r.raise_for_status()
        sid = r.headers.get("mcp-session-id") or r.headers.get("Mcp-Session-Id")
        if sid:
            self._session_id = sid.strip()
        return _parse_jsonrpc_result(r.text, rpc_id)

    async def notify_initialized(self) -> None:
        """Best-effort MCP initialized notification (some servers expect this after initialize)."""
        headers = {
            "Content-Type": "application/json",
            "Accept": MCP_ACCEPT,
        }
        if self._session_id:
            headers["mcp-session-id"] = self._session_id
        payload = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
        try:
            r = await self._client.post(self.mcp_url, json=payload, headers=headers)
            r.raise_for_status()
        except Exception as e:
            logger.debug("notifications/initialized not accepted for %s: %s", self.mcp_url, e)

    async def initialize(self) -> dict[str, Any]:
        return await self._rpc(
            "initialize",
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "netops-mcp-gateway", "version": "0.1.0"},
            },
        )

    async def tools_list(self) -> dict[str, Any]:
        return await self._rpc("tools/list", {})

    async def tools_call(self, name: str, arguments: dict[str, Any]) -> Any:
        raw = await self._rpc("tools/call", {"name": name, "arguments": arguments})
        return _normalize_proxied_tool_result(raw)


def _args_drop_none(args: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in args.items() if v is not None}


_http_client: httpx.AsyncClient | None = None


def _backends_from_env() -> list[dict[str, str]]:
    raw = os.getenv("SUITE_GATEWAY_BACKENDS", "").strip()
    if raw:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"SUITE_GATEWAY_BACKENDS must be valid JSON: {e}") from e
        if not isinstance(data, list):
            raise ValueError("SUITE_GATEWAY_BACKENDS must be a JSON list")
        out: list[dict[str, str]] = []
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                continue
            alias = str(item.get("alias", f"backend{i}")).strip()
            url = str(item.get("url", "")).strip()
            if not url:
                continue
            out.append({"alias": alias, "url": url})
        return out
    if os.getenv("SUITE_GATEWAY_USE_DEFAULT_BACKENDS", "true").lower() in ("1", "true", "yes"):
        return list(DEFAULT_DOCKER_BACKENDS)
    return []


@dataclass
class _CompactRegistry:
    """In-memory tool catalog built at startup (lifespan-scoped)."""

    bridges: dict[str, BackendMCPClient] = field(default_factory=dict)
    catalog: list[dict[str, Any]] = field(default_factory=list)


_compact_registry = _CompactRegistry()


@lifespan
async def gateway_lifespan(server) -> object:
    from fastmcp.tools.function_tool import FunctionTool

    global _http_client

    verify = os.getenv("SUITE_GATEWAY_VERIFY_HTTP", "false").lower() in ("1", "true", "yes")
    timeout = float(os.getenv("SUITE_GATEWAY_REQUEST_TIMEOUT", "120"))
    per_cap = int(os.getenv("SUITE_GATEWAY_MAX_TOOLS_PER_BACKEND", "96"))

    backends = _backends_from_env()
    if not backends:
        logger.error("No backends configured. Set SUITE_GATEWAY_BACKENDS JSON or defaults.")
        yield {}
        return

    _http_client = httpx.AsyncClient(
        verify=verify,
        timeout=timeout,
        follow_redirects=True,
    )
    client = _http_client
    registered = 0

    try:
        _compact_registry.bridges.clear()
        _compact_registry.catalog.clear()

        # Progressive disclosure: control tools + playbook tools mirroring netops://flows/* resources.
        # See https://www.anthropic.com/engineering/code-execution-with-mcp
        for spec in backends:
            alias = _safe_segment(spec["alias"])
            url = spec["url"].strip()
            bridge = BackendMCPClient(client, url)
            try:
                await bridge.initialize()
                await bridge.notify_initialized()
            except Exception as e:
                logger.warning("Skip backend %s (%s): init failed: %s", alias, url, e)
                continue
            try:
                listed = await bridge.tools_list()
            except Exception as e:
                logger.warning("Skip backend %s: tools/list failed: %s", alias, e)
                continue
            tools = listed.get("tools") if isinstance(listed, dict) else None
            if not tools:
                continue
            _compact_registry.bridges[alias] = bridge
            for t in tools[:per_cap]:
                tname = t.get("name")
                if not tname or not isinstance(tname, str):
                    continue
                schema = t.get("inputSchema") or t.get("input_schema")
                if not isinstance(schema, dict):
                    schema = None
                _compact_registry.catalog.append(
                    {
                        "backend": alias,
                        "backend_url": bridge.mcp_url,
                        "tool_name": tname,
                        "description": (t.get("description") or "")[:2000],
                        "inputSchema": schema,
                    }
                )

        async def suite_list_backends() -> dict[str, Any]:
            """List MCP backends reachable by this gateway and how many tools each exposes."""
            counts: dict[str, int] = {}
            for row in _compact_registry.catalog:
                b = row["backend"]
                counts[b] = counts.get(b, 0) + 1
            return {
                "backends": [
                    {
                        "backend": a,
                        "tool_count": counts[a],
                        "mcp_url": next(
                            (r["backend_url"] for r in _compact_registry.catalog if r["backend"] == a),
                            None,
                        ),
                    }
                    for a in sorted(counts)
                ],
                "total_catalog_entries": len(_compact_registry.catalog),
            }

        async def suite_search_tools(
            query: str = "",
            backend: str | None = None,
            limit: int = 40,
            detail_level: str = "summary",
            include_input_schema: bool = False,
        ) -> dict[str, Any]:
            """Search cached backend tools. detail_level: name | summary | full (progressive disclosure)."""
            q = (query or "").strip().lower()
            lim = max(1, min(int(limit), 200))
            want = _safe_segment(backend) if (backend or "").strip() else None
            lvl = (detail_level or "summary").strip().lower()
            if lvl not in ("name", "summary", "full"):
                lvl = "summary"
            hits: list[dict[str, Any]] = []
            for row in _compact_registry.catalog:
                if want and row["backend"] != want:
                    continue
                if q:
                    blob = f"{row['tool_name']} {row.get('description', '')}".lower()
                    if q not in blob:
                        continue
                item: dict[str, Any] = {
                    "backend": row["backend"],
                    "tool_name": row["tool_name"],
                }
                if lvl in ("summary", "full"):
                    desc = row.get("description") or ""
                    item["description"] = desc if lvl == "full" else desc[:500]
                if lvl == "full" or include_input_schema:
                    item["inputSchema"] = row.get("inputSchema")
                hits.append(item)
            out: dict[str, Any] = {
                "detail_level": lvl,
                "matches": hits[:lim],
                "returned": min(len(hits), lim),
                "scanned": len(_compact_registry.catalog),
            }
            if not hits and _compact_registry.catalog:
                if want and not any(r["backend"] == want for r in _compact_registry.catalog):
                    out["hint"] = (
                        f"No catalog entries for backend `{want}`. "
                        f"Known backends: {sorted({r['backend'] for r in _compact_registry.catalog})}."
                    )
                elif q:
                    out["hint"] = (
                        "No tool name or description contained that substring. Try shorter tokens "
                        "(e.g. alert, issue, assurance, health, org, network, site, log, session), "
                        "set `backend` to one vendor, or use `query=\"\"` with a higher `limit` to browse. "
                        "Meraki alert-style tools often need organizationId from a list-organizations tool first."
                    )
                else:
                    out["hint"] = (
                        "No matches with current filters. Raise `limit` or add a `query` / `backend` filter."
                    )
            return out

        async def suite_call_tool(
            backend: str,
            tool_name: str,
            arguments: dict[str, Any] | None = None,
        ) -> Any:
            """Invoke one backend MCP tool by alias, tool name, and JSON arguments."""
            alias = _safe_segment(backend)
            br = _compact_registry.bridges.get(alias)
            if not br:
                return {
                    "error": "unknown_backend",
                    "backend": backend,
                    "normalized": alias,
                    "known_backends": sorted(_compact_registry.bridges),
                }
            return await br.tools_call(tool_name, _args_drop_none(arguments or {}))

        async def suite_flow_overview() -> str:
            """Markdown playbook (mirror of MCP resource netops://flows/overview)."""
            return gateway_flows.get_overview_flow()

        async def suite_flow_troubleshoot() -> str:
            """Markdown playbook (mirror of MCP resource netops://flows/troubleshoot)."""
            return gateway_flows.get_troubleshoot_flow()

        async def suite_flow_compact() -> str:
            """Markdown playbook (mirror of MCP resource netops://flows/compact)."""
            return gateway_flows.get_compact_flow()

        async def suite_flow_backends() -> str:
            """Markdown playbook (mirror of MCP resource netops://flows/backends)."""
            return gateway_flows.get_backends_flow()

        async def suite_flow_clients() -> str:
            """Markdown playbook (mirror of MCP resource netops://flows/clients)."""
            return gateway_flows.get_clients_flow()

        meta = [
            (
                "suite_list_backends",
                suite_list_backends,
                "NetOps MCP Gateway: list backends and per-backend tool counts.",
            ),
            (
                "suite_search_tools",
                suite_search_tools,
                "NetOps MCP Gateway: search tools (query, optional backend, limit). "
                "detail_level=name|summary|full for progressive disclosure; then suite_call_tool.",
            ),
            (
                "suite_call_tool",
                suite_call_tool,
                "NetOps MCP Gateway: run a backend MCP tool by name with JSON arguments.",
            ),
            (
                "suite_flow_overview",
                suite_flow_overview,
                "NetOps MCP Gateway playbook (Markdown). Same content as MCP resource netops://flows/overview.",
            ),
            (
                "suite_flow_troubleshoot",
                suite_flow_troubleshoot,
                "NetOps MCP Gateway playbook (Markdown). Same content as MCP resource netops://flows/troubleshoot.",
            ),
            (
                "suite_flow_compact",
                suite_flow_compact,
                "NetOps MCP Gateway playbook (Markdown). Same content as MCP resource netops://flows/compact.",
            ),
            (
                "suite_flow_backends",
                suite_flow_backends,
                "NetOps MCP Gateway playbook (Markdown). Same content as MCP resource netops://flows/backends.",
            ),
            (
                "suite_flow_clients",
                suite_flow_clients,
                "NetOps MCP Gateway playbook (Markdown). Same content as MCP resource netops://flows/clients.",
            ),
        ]
        for name, fn, desc in meta:
            server.add_tool(FunctionTool.from_function(fn, name=name, description=desc))
            registered += 1
        logger.info(
            "NetOps MCP Gateway registered %s gateway tool(s) (3 control + 5 playbooks), "
            "%s catalog entries across %s backend(s)",
            registered,
            len(_compact_registry.catalog),
            len(_compact_registry.bridges),
        )
        yield {}
    finally:
        if _http_client is not None:
            await _http_client.aclose()
        _http_client = None


load_dotenv_file()

mcp_host = os.getenv("MCP_HOST", "0.0.0.0")
mcp_port = int(os.getenv("MCP_PORT", "8010"))

mcp = FastMCP(
    "NetOps MCP Gateway",
    instructions=gateway_flows.SERVER_INSTRUCTIONS,
    lifespan=gateway_lifespan,
)


@mcp.resource("netops://flows/overview")
def _suite_resource_flow_overview() -> str:
    return gateway_flows.get_overview_flow()


@mcp.resource("netops://flows/troubleshoot")
def _suite_resource_flow_troubleshoot() -> str:
    return gateway_flows.get_troubleshoot_flow()


@mcp.resource("netops://flows/compact")
def _suite_resource_flow_compact() -> str:
    return gateway_flows.get_compact_flow()


@mcp.resource("netops://flows/backends")
def _suite_resource_flow_backends() -> str:
    return gateway_flows.get_backends_flow()


@mcp.resource("netops://flows/clients")
def _suite_resource_flow_clients() -> str:
    return gateway_flows.get_clients_flow()


if __name__ == "__main__":
    load_dotenv_file()
    if not _backends_from_env():
        logger.error("Configure SUITE_GATEWAY_BACKENDS or enable SUITE_GATEWAY_USE_DEFAULT_BACKENDS.")
        sys.exit(1)
    logger.info("Starting NetOps MCP Gateway on %s:%s", mcp_host, mcp_port)
    mcp.run(transport="streamable-http", host=mcp_host, port=mcp_port)
