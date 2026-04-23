"""
Splunk MCP Server - FastMCP Wrapper

A Model Context Protocol (MCP) server that wraps Splunk's MCP backend using fastmcp.
This provides proper MCP protocol support with HTTP transport for MCP client compatibility.

Features:
- SSL certificate handling for self-signed certs
- Bearer token authentication  
- Proper MCP protocol via fastmcp
- Tool forwarding to Splunk backend

Environment Variables:
- SPLUNK_HOST: Splunk hostname/IP (required unless SPLUNK_MCP_URL is set)
- SPLUNK_PORT: Management/web port (default: 8089) used with SPLUNK_MCP_PATH
- SPLUNK_MCP_PATH: Path to MCP endpoint (default: /services/mcp). For UI proxy
  (e.g. /en-US/splunkd/__raw/services/mcp) set this or use SPLUNK_MCP_URL.
- SPLUNK_MCP_URL: Optional full HTTPS URL to the Splunk MCP endpoint, overrides
  host/port/path (e.g. https://host:443/en-US/splunkd/__raw/services/mcp)
- SPLUNK_API_KEY: Required. Splunk Bearer token
- SPLUNK_VERIFY_SSL: Optional. Verify SSL certificates (default: false)
- MCP_PORT: Optional. Port for this MCP server (default: 8006)
- MCP_HOST: Optional. Host for this MCP server (default: 0.0.0.0)
- SPLUNK_MCP_DYNAMIC: Optional. If "true" (default), load tools at startup from Splunk tools/list
- SPLUNK_MCP_MAX_TOOLS: Optional. Cap dynamically registered tools (default: 64)
- SPLUNK_MCP_APPEND_INPUT_SCHEMA: If "true" (default), append Splunk inputSchema JSON to each tool description
- SPLUNK_MCP_SCHEMA_DESC_MAX_CHARS: Max length of embedded schema in description (default: 12000)

Author: Patrick Mosimann
"""

import httpx
import json
import keyword
import logging
import os
import re
import sys
import uuid
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ---- Environment Variables ----
def load_dotenv_file(env_file: str | None = None) -> bool:
    """
    Load environment variables from a .env file on disk.

    Docker Compose `env_file:` injects the same values into the process environment but does
    not copy a file into the image, so /app/.env may be missing unless you bind-mount it.
    In that case we rely on the environment that Compose (or the shell) already set.
    """
    path = env_file or os.getenv("DOTENV_PATH", ".env")
    env_path = Path(path)

    if not env_path.exists():
        if os.getenv("SPLUNK_API_KEY") and not (os.getenv("SPLUNK_API_KEY") or "").startswith(
            "your_actual_"
        ):
            logger.info(
                "No .env file at %s (optional if vars are set via Docker env_file or the host).",
                env_path.resolve(),
            )
        else:
            logger.warning("⚠️  .env file not found at %s", env_path.resolve())
            logger.info("📋 Using environment variables or defaults")
        return False
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    os.environ[key] = value
        
        logger.info(f"✅ Loaded environment from {env_file}")
        return True
    except Exception as e:
        logger.error(f"❌ Error loading .env file: {e}")
        return False

# Load .env file first
load_dotenv_file()

# Get Splunk configuration from environment
splunk_host = os.getenv("SPLUNK_HOST", "").strip() or None
splunk_port = os.getenv("SPLUNK_PORT", "8089")
splunk_mcp_url = os.getenv("SPLUNK_MCP_URL", "").strip()
splunk_mcp_path = (os.getenv("SPLUNK_MCP_PATH", "/services/mcp") or "/services/mcp").strip()
if not splunk_mcp_path.startswith("/"):
    splunk_mcp_path = f"/{splunk_mcp_path}"
splunk_api_key = os.getenv("SPLUNK_API_KEY")
splunk_verify_ssl = os.getenv("SPLUNK_VERIFY_SSL", "false").lower() == "true"

# Get MCP server configuration
mcp_port = int(os.getenv("MCP_PORT", "8006"))
mcp_host = os.getenv("MCP_HOST", "0.0.0.0")

# Validate required configuration
if not splunk_mcp_url and not splunk_host:
    logger.error("❌ SPLUNK_HOST or SPLUNK_MCP_URL is required!")
    logger.error("📋 Set SPLUNK_HOST (and optional SPLUNK_MCP_PATH) or a full SPLUNK_MCP_URL")
    sys.exit(1)

if not splunk_api_key or splunk_api_key.startswith('your_actual_'):
    logger.error("❌ SPLUNK_API_KEY not configured properly!")
    logger.error("📋 Please set your Splunk API key in .env file")
    sys.exit(1)

# Build Splunk backend URL (direct mgmt 8089/services/mcp vs web 443/.../__raw/.../mcp)
if splunk_mcp_url:
    splunk_backend_url = splunk_mcp_url.rstrip("/")
else:
    splunk_backend_url = f"https://{splunk_host}:{splunk_port}{splunk_mcp_path}"

logger.info(f"✅ Splunk backend: {splunk_backend_url}")
logger.info(f"✅ API key loaded: [CONFIGURED]")
logger.info(f"✅ SSL verification: {splunk_verify_ssl}")
logger.info(f"🌐 MCP Server will run on: http://{mcp_host}:{mcp_port}")

# Filled by lifespan on server start, closed on shutdown
http_client: httpx.AsyncClient | None = None

splunk_mcp_dynamic = os.getenv("SPLUNK_MCP_DYNAMIC", "true").lower() in ("1", "true", "yes")
splunk_mcp_max_tools = int(os.getenv("SPLUNK_MCP_MAX_TOOLS", "64"))
splunk_mcp_append_input_schema = os.getenv("SPLUNK_MCP_APPEND_INPUT_SCHEMA", "true").lower() in ("1", "true", "yes")
splunk_mcp_schema_desc_max = int(os.getenv("SPLUNK_MCP_SCHEMA_DESC_MAX_CHARS", "12000"))


def _append_input_schema_to_description(
    base: str,
    schema: dict[str, Any] | None,
) -> str:
    """Append Splunk's inputSchema to the tool description for LLM/client visibility (same as tools/list)."""
    base = (base or "").rstrip()
    if not splunk_mcp_append_input_schema:
        return base
    if not schema:
        return base
    try:
        blob = json.dumps(schema, indent=2, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        logger.warning("Could not serialize inputSchema for tool description: %s", e)
        return base
    limit = max(1000, splunk_mcp_schema_desc_max)
    if len(blob) > limit:
        blob = blob[: limit - 40] + "\n... (inputSchema truncated)"
    return (
        f"{base}\n\n---\n**Splunk `inputSchema`** (JSON Schema for `arguments` — use these names and types):\n\n"
        f"```json\n{blob}\n```"
    )


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


def _args_drop_none_for_splunk(args: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in args.items() if v is not None}


async def call_splunk_mcp(method: str, params: dict | None = None) -> Any:
    """Call Splunk MCP backend with JSON-RPC 2.0 over HTTP."""
    if http_client is None:
        raise RuntimeError("Splunk HTTP client is not initialized (server lifespan not started)")

    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": method,
        "params": params or {}
    }
    try:
        response = await http_client.post(
            splunk_backend_url,
            json=payload,
            headers={
                "Authorization": f"Bearer {splunk_api_key}",
                "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
        result = response.json()
        if "error" in result:
            raise RuntimeError(f"Splunk MCP error: {result['error']}")
        return result.get("result", {})
    except Exception as e:
        logger.error(f"Error calling Splunk MCP: {e}")
        raise


async def _call_splunk_tool(backend_name: str, args: dict[str, Any]) -> Any:
    """Forward a tools/call, omitting only None in arguments for optional fields."""
    return await call_splunk_mcp(
        "tools/call",
        {"name": backend_name, "arguments": _args_drop_none_for_splunk(args)},
    )


def _build_splunk_tool_function(backend_name: str, input_schema: dict[str, Any] | None):
    """
    Build an async function with an explicit parameter list. FastMCP disallows **kwargs for tools;
    we compile a small async def from the Splunk inputSchema (string exec; names/structure come from Splunk only).
    """
    if not input_schema or input_schema.get("type") != "object":
        input_schema = {"type": "object", "properties": {}}
    props: dict = input_schema.get("properties") or {}
    required: set = set(input_schema.get("required", []))

    if not props:
        b = backend_name

        async def _no_args() -> Any:
            return await _call_splunk_tool(b, {})

        _no_args.__name__ = "splunk_tool_" + _py_param_name(backend_name)
        _no_args.__doc__ = None
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
            lit = _default_literal(dval)
            sig_lines.append(f"{py}: {py_t} = {lit}")
        else:
            sig_lines.append(f"{py}: {py_t} | None = None")

    sig = ", ".join(sig_lines)
    # arguments dict by JSON property names, values from Python param names; drop Nones in handler
    dict_innards = ", ".join(f"{json.dumps(j)}: {p}" for j, p in pnames)
    fname = "tool_" + _py_param_name(backend_name)[:80]

    g: dict[str, Any] = {
        "_call_splunk_tool": _call_splunk_tool,
        "__builtins__": __builtins__,
    }
    lcl: dict[str, Any] = {}
    body_lines = [f"    _a = {{{dict_innards}}}"]
    body_lines.append(f"    return await _call_splunk_tool({backend_name!r}, _a)")
    final_src = f"async def {fname}({sig}) -> object:\n" + "\n".join(body_lines)
    exec(compile(final_src, f"<splunk_tool {backend_name}>", "exec"), g, lcl)  # noqa: S102
    fn = lcl[fname]
    fn.__name__ = f"splunk_{_py_param_name(backend_name)}"[:99]
    return fn


async def _register_splunk_tools_from_backend(server) -> int:
    """Call Splunk tools/list and add FunctionTools (must run after httpx client exists)."""
    from fastmcp.tools.function_tool import FunctionTool  # local import: startup cost

    result = await call_splunk_mcp("tools/list", {})
    tools = result.get("tools")
    if not tools:
        raise RuntimeError("Splunk tools/list returned no tools — check URL, token, and Splunk MCP feature")

    tools = tools[: splunk_mcp_max_tools]
    n = 0
    for t in tools:
        tname = t.get("name")
        if not tname:
            continue
        tdesc = t.get("description") or f"Proxied tool from Splunk: {tname}"
        tschema = t.get("inputSchema")
        if not tschema and t.get("input_schema"):
            tschema = t.get("input_schema")
        tdesc = _append_input_schema_to_description(tdesc, tschema if isinstance(tschema, dict) else None)
        try:
            fn = _build_splunk_tool_function(tname, tschema)
            ft = FunctionTool.from_function(fn, name=tname, description=tdesc)
        except Exception as e:
            logger.error(f"Failed to build proxy for {tname!r}: {e}")
            continue
        server.add_tool(ft)
        n += 1
    return n


@lifespan
async def splunk_http_lifespan(server) -> object:
    global http_client
    client = httpx.AsyncClient(
        verify=splunk_verify_ssl,
        timeout=60.0,
        follow_redirects=True,
    )
    http_client = client
    try:
        if not splunk_mcp_dynamic:
            logger.warning("SPLUNK_MCP_DYNAMIC is false — static tools are not bundled; still loading from Splunk.")
        n = await _register_splunk_tools_from_backend(server)
        logger.info("🛠️  Tools: %s (loaded from Splunk tools/list)", n)
        yield {}
    finally:
        try:
            await client.aclose()
        finally:
            http_client = None


# Create FastMCP server after handlers exist (lifespan loads tools at startup)
mcp = FastMCP("Splunk MCP Server", lifespan=splunk_http_lifespan)


if __name__ == "__main__":
    logger.info("🚀 Splunk MCP Server starting...")
    logger.info(f"📡 Backend: {splunk_backend_url}")
    logger.info(f"🔑 SSL Verification: {splunk_verify_ssl}")
    logger.info("🛠️  Tools: discovered at startup (Splunk tools/list)")

    mcp.run(transport="streamable-http", host=mcp_host, port=mcp_port)
