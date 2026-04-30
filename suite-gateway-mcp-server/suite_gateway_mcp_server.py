"""
MCP Suite Gateway — single entrypoint that aggregates tools from other MCP servers.

Implements the multi-backend pattern described in Cisco's MCP reference architecture
(MultiServer MCP client / REST bridge): one FastMCP server discovers `tools/list` from
each configured backend over HTTP, registers prefixed tools, and forwards `tools/call`.

Environment:
- MCP_HOST / MCP_PORT: bind for this gateway (default 0.0.0.0:8010)
- SUITE_GATEWAY_BACKENDS: JSON list of {"alias": "meraki", "url": "http://host:8000/mcp"}
  If unset and SUITE_GATEWAY_USE_DEFAULT_BACKENDS=true (default in Docker), uses Docker
  Compose service hostnames for all suite servers on the default bridge.
- SUITE_GATEWAY_VERIFY_HTTP: verify TLS for backend calls (default false for internal http://)
- SUITE_GATEWAY_REQUEST_TIMEOUT: seconds per backend HTTP call (default 120)
- SUITE_GATEWAY_MAX_TOOLS_PER_BACKEND: cap tools per server (default 96)
- SUITE_GATEWAY_MAX_TOOLS_TOTAL: cap total registered tools (default 512)

Author: Network MCP Docker Suite
"""

from __future__ import annotations

import json
import keyword
import logging
import os
import re
import sys
import uuid
from pathlib import Path
from collections.abc import Awaitable, Callable
from typing import Any

import httpx
from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("suite-gateway-mcp-server")

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
                "clientInfo": {"name": "suite-gateway", "version": "0.1.0"},
            },
        )

    async def tools_list(self) -> dict[str, Any]:
        return await self._rpc("tools/list", {})

    async def tools_call(self, name: str, arguments: dict[str, Any]) -> Any:
        return await self._rpc("tools/call", {"name": name, "arguments": arguments})


def _args_drop_none(args: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in args.items() if v is not None}


def _py_param_name(raw: str) -> str:
    s = re.sub(r"[^0-9a-zA-Z_]", "_", raw) or "arg"
    if s[0].isdigit() or keyword.iskeyword(s) or s in ("self", "None", "True", "False"):
        s = "p_" + s
    return s


def _default_literal(v: Any) -> str:
    if v is None:
        return "None"
    if isinstance(v, bool):
        return "True" if v else "False"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return repr(v)
    return json.dumps(v)


def _js_type_to_python(sub: dict[str, Any] | None) -> str:
    if not sub or not isinstance(sub, dict):
        return "Any"
    t = sub.get("type", "any")
    if t == "integer":
        return "int"
    if t == "number":
        return "float"
    if t == "boolean":
        return "bool"
    if t == "string":
        return "str"
    if t == "array":
        return "list"
    if t == "object":
        return "dict"
    if isinstance(t, list) and t:
        return _js_type_to_python({"type": t[0]})
    return "Any"


def _append_schema_to_description(base: str, schema: dict[str, Any] | None, max_chars: int) -> str:
    base = (base or "").rstrip()
    if not schema:
        return base
    try:
        blob = json.dumps(schema, indent=2, ensure_ascii=False)
    except (TypeError, ValueError):
        return base
    if len(blob) > max_chars:
        blob = blob[: max_chars - 40] + "\n... (schema truncated)"
    return (
        f"{base}\n\n---\n**Proxied tool (suite gateway)** — original `inputSchema`:\n\n```json\n{blob}\n```"
    )


def _build_proxy_function(
    backend_tool_name: str,
    input_schema: dict[str, Any] | None,
    invoke: Callable[[dict[str, Any]], Awaitable[Any]],
):
    """Build async tool function from JSON Schema (FastMCP disallows **kwargs)."""
    if not input_schema or input_schema.get("type") != "object":
        input_schema = {"type": "object", "properties": {}}
    props: dict = input_schema.get("properties") or {}
    required: set = set(input_schema.get("required", []))

    if not props:

        async def _no_args() -> Any:
            return await invoke({})

        _no_args.__name__ = "gw_" + _py_param_name(backend_tool_name)
        return _no_args

    sig_lines: list[str] = []
    pnames: list[tuple[str, str]] = []
    for jname, sub in props.items():
        py = _py_param_name(jname)
        pnames.append((jname, py))
        py_t = _js_type_to_python(sub if isinstance(sub, dict) else None)
        has_d = isinstance(sub, dict) and "default" in sub
        dval = sub.get("default") if has_d else None
        in_req = jname in required

        if in_req and not has_d and dval is None:
            sig_lines.append(f"{py}: {py_t}")
        elif has_d:
            sig_lines.append(f"{py}: {py_t} = {_default_literal(dval)}")
        else:
            sig_lines.append(f"{py}: {py_t} | None = None")

    sig = ", ".join(sig_lines)
    dict_innards = ", ".join(f"{json.dumps(j)}: {p}" for j, p in pnames)
    fname = "gw_" + _py_param_name(backend_tool_name)[:70]

    g: dict[str, Any] = {
        "_invoke": invoke,
        "__builtins__": __builtins__,
    }
    lcl: dict[str, Any] = {}
    src = (
        f"async def {fname}({sig}) -> object:\n"
        f"    _a = {{{dict_innards}}}\n"
        f"    return await _invoke(_a)\n"
    )
    exec(compile(src, f"<gateway_tool {backend_tool_name}>", "exec"), g, lcl)  # noqa: S102
    fn = lcl[fname]
    fn.__name__ = "gw_" + _py_param_name(backend_tool_name)[:99]
    return fn


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


@lifespan
async def gateway_lifespan(server) -> object:
    from fastmcp.tools.function_tool import FunctionTool

    global _http_client

    verify = os.getenv("SUITE_GATEWAY_VERIFY_HTTP", "false").lower() in ("1", "true", "yes")
    timeout = float(os.getenv("SUITE_GATEWAY_REQUEST_TIMEOUT", "120"))
    per_cap = int(os.getenv("SUITE_GATEWAY_MAX_TOOLS_PER_BACKEND", "96"))
    total_cap = int(os.getenv("SUITE_GATEWAY_MAX_TOOLS_TOTAL", "512"))
    schema_desc_max = int(os.getenv("SUITE_GATEWAY_SCHEMA_DESC_MAX_CHARS", "8000"))

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
        for spec in backends:
            if registered >= total_cap:
                logger.warning("Stopped at SUITE_GATEWAY_MAX_TOOLS_TOTAL=%s", total_cap)
                break
            alias = _safe_segment(spec["alias"])
            url = spec["url"].strip()
            bridge = BackendMCPClient(client, url)
            try:
                init_info = await bridge.initialize()
                await bridge.notify_initialized()
                logger.info(
                    "Backend %s initialized: %s",
                    alias,
                    (init_info or {}).get("serverInfo", {}).get("name", url),
                )
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
                logger.warning("Backend %s returned no tools", alias)
                continue

            for t in tools[:per_cap]:
                if registered >= total_cap:
                    break
                tname = t.get("name")
                if not tname or not isinstance(tname, str):
                    continue
                gw_name = f"{alias}__{_safe_segment(tname)}"
                desc = t.get("description") or f"Proxied from `{alias}`: `{tname}`"
                schema = t.get("inputSchema") or t.get("input_schema")
                if not isinstance(schema, dict):
                    schema = None
                desc = _append_schema_to_description(desc, schema, schema_desc_max)
                desc = f"[backend:{alias} url:{bridge.mcp_url} tool:{tname}]\n{desc}"

                async def _invoke(
                    args: dict[str, Any],
                    *,
                    _tool: str = tname,
                    _br: BackendMCPClient = bridge,
                ) -> Any:
                    return await _br.tools_call(_tool, _args_drop_none(args))

                try:
                    fn = _build_proxy_function(
                        tname,
                        schema,
                        _invoke,
                    )
                except Exception as e:
                    logger.error("Build proxy failed %s / %s: %s", alias, tname, e)
                    continue

                try:
                    ft = FunctionTool.from_function(fn, name=gw_name, description=desc)
                    server.add_tool(ft)
                    registered += 1
                except Exception as e:
                    logger.error("Register tool failed %s: %s", gw_name, e)

        logger.info("Suite gateway registered %s tool(s) from %s backend(s)", registered, len(backends))
        yield {}
    finally:
        if _http_client is not None:
            await _http_client.aclose()
        _http_client = None


load_dotenv_file()

mcp_host = os.getenv("MCP_HOST", "0.0.0.0")
mcp_port = int(os.getenv("MCP_PORT", "8010"))

mcp = FastMCP("Network MCP Suite Gateway", lifespan=gateway_lifespan)


if __name__ == "__main__":
    load_dotenv_file()
    if not _backends_from_env():
        logger.error("Configure SUITE_GATEWAY_BACKENDS or enable SUITE_GATEWAY_USE_DEFAULT_BACKENDS.")
        sys.exit(1)
    logger.info("Starting suite gateway on %s:%s", mcp_host, mcp_port)
    mcp.run(transport="streamable-http", host=mcp_host, port=mcp_port)
