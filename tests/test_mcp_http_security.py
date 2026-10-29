import importlib.util
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "shared" / "mcp_http_security.py"


def _load_security():
    spec = importlib.util.spec_from_file_location("mcp_http_security", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class LoopbackBindTests(unittest.TestCase):
    def setUp(self):
        self.sec = _load_security()

    def test_loopback_hosts(self):
        for host in ("127.0.0.1", "localhost", "::1", "127.0.0.2", "[::1]"):
            self.assertTrue(self.sec.is_loopback_bind(host), host)

    def test_non_loopback_hosts(self):
        for host in ("0.0.0.0", "::", "192.168.1.10", "", "example.com"):
            self.assertFalse(self.sec.is_loopback_bind(host), host)


class StartupGuardTests(unittest.TestCase):
    def setUp(self):
        self.sec = _load_security()
        self._token = os.environ.pop("MCP_API_TOKEN", None)

    def tearDown(self):
        if self._token is None:
            os.environ.pop("MCP_API_TOKEN", None)
        else:
            os.environ["MCP_API_TOKEN"] = self._token

    def test_non_loopback_without_token_raises(self):
        class Dummy:
            def add_middleware(self, _mw):
                raise AssertionError("middleware should not attach")

        with self.assertRaises(RuntimeError):
            self.sec.apply_mcp_http_security(Dummy(), "0.0.0.0")

    def test_loopback_without_token_ok(self):
        class Dummy:
            def add_middleware(self, _mw):
                raise AssertionError("loopback must stay token-optional")

        host = self.sec.apply_mcp_http_security(Dummy(), "127.0.0.1")
        self.assertEqual(host, "127.0.0.1")


class ClickHouseAllowlistTests(unittest.TestCase):
    def test_raw_sql_tool_removed(self):
        source = (ROOT / "clickhouse-mcp-server" / "clickhouse_mcp_server.py").read_text()
        self.assertNotIn("def query_clickhouse", source)
        self.assertNotIn("FORBIDDEN_KEYWORDS", source)
        self.assertIn("param_", source)
        self.assertIn("mcp_readonly", source)
        self.assertIn("_require_readonly_identity", source)


class MutatingToolOptInTests(unittest.TestCase):
    def setUp(self):
        self.sec = _load_security()

    def test_disabled_does_not_register(self):
        class Dummy:
            def __init__(self):
                self.registered = False

            def tool(self):
                def deco(fn):
                    self.registered = True
                    return fn

                return deco

        dummy = Dummy()
        deco = self.sec.register_mutating_tool(dummy, False)

        @deco
        def write_tool():
            return "nope"

        self.assertFalse(dummy.registered)
        self.assertEqual(write_tool(), "nope")

    def test_enabled_registers(self):
        class Dummy:
            def __init__(self):
                self.registered = False

            def tool(self):
                def deco(fn):
                    self.registered = True
                    return fn

                return deco

        dummy = Dummy()
        deco = self.sec.register_mutating_tool(dummy, True)

        @deco
        def write_tool():
            return "ok"

        self.assertTrue(dummy.registered)

    def test_compose_publishes_loopback_only(self):
        compose = (ROOT / "docker-compose.yml").read_text()
        self.assertIn("127.0.0.1:8000:8000", compose)
        self.assertNotIn('      - "8000:8000"', compose)


if __name__ == "__main__":
    sys.exit(not unittest.main())
