#!/usr/bin/env python3
"""Unit tests for the mcp_client.py CLI helper."""

from __future__ import annotations

import base64
import io
import json
import socket
import threading
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

import mcp_client


class _MockMcpServer:
    def __init__(self, handler) -> None:
        self._handler = handler
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind(("127.0.0.1", 0))
        self._sock.listen(1)
        self.port = self._sock.getsockname()[1]
        self.received: list[dict] = []
        self._thread = threading.Thread(target=self._serve_once, daemon=True)
        self._thread.start()

    def _serve_once(self) -> None:
        try:
            conn, _ = self._sock.accept()
            with conn:
                data = b""
                while b"\n" not in data:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                req = json.loads(data.decode("utf-8").strip())
                self.received.append(req)
                resp = self._handler(req)
                conn.sendall((json.dumps(resp) + "\n").encode("utf-8"))
        finally:
            self._sock.close()


class McpClientTests(unittest.TestCase):
    def test_send_command_roundtrip(self) -> None:
        server = _MockMcpServer(lambda req: {"success": True, "echo": req})
        resp = mcp_client.send_command({"command": "os_info"}, port=server.port, timeout=2.0)
        self.assertIsNotNone(resp)
        assert resp is not None
        self.assertTrue(resp["success"])
        self.assertEqual("os_info", server.received[0]["command"])

    def test_screenshot_saves_file_and_returns_zero(self) -> None:
        png_bytes = b"\x89PNG\r\n\x1a\nfake"
        b64_data = base64.b64encode(png_bytes).decode("ascii")
        server = _MockMcpServer(
            lambda _req: {"success": True, "data": b64_data, "width": 720, "height": 1280}
        )
        with TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "snap.png"
            orig_send = mcp_client.send_command
            mcp_client.send_command = lambda cmd, **_kw: orig_send(  # type: ignore[assignment]
                cmd, port=server.port, timeout=2.0
            )
            try:
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    code = mcp_client.main(["screenshot", str(out_file)])
                self.assertEqual(0, code)
                self.assertEqual(png_bytes, out_file.read_bytes())
                self.assertIn("720x1280", stdout.getvalue())
            finally:
                mcp_client.send_command = orig_send  # type: ignore[assignment]

    def test_error_response_returns_exit_code_one(self) -> None:
        server = _MockMcpServer(lambda _req: {"error": "Node not found: /root/Missing"})
        orig_send = mcp_client.send_command
        mcp_client.send_command = lambda cmd, **_kw: orig_send(  # type: ignore[assignment]
            cmd, port=server.port, timeout=2.0
        )
        try:
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = mcp_client.main(["get_node_info", "/root/Missing"])
            self.assertEqual(1, code)
            self.assertIn("Node not found", stdout.getvalue())
        finally:
            mcp_client.send_command = orig_send  # type: ignore[assignment]


if __name__ == "__main__":
    unittest.main()
