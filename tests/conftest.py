"""Keep fixed-port browser contracts isolated across concurrent Windows lanes."""
import errno
import http.server
import socket
import time

import pytest


@pytest.fixture(autouse=True)
def exclusive_browser_listener(request, monkeypatch):
    if not request.node.path.name.endswith("_ui.py") or not hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
        return
    original = http.server.ThreadingHTTPServer.server_bind

    def bind(server):
        if server.server_address != ("127.0.0.1", 8000):
            return original(server)
        # Windows SO_REUSEADDR permits two live listeners on the same address,
        # routing a request to another worktree's document root. Do not share it.
        server.allow_reuse_address = False
        server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        deadline = time.monotonic() + 90
        while True:
            try:
                return original(server)
            except OSError as exc:
                busy = exc.errno in (errno.EADDRINUSE, errno.EACCES) or getattr(exc, "winerror", None) in (10048, 10013)
                if not busy or time.monotonic() >= deadline:
                    raise
                time.sleep(0.25)

    monkeypatch.setattr(http.server.ThreadingHTTPServer, "server_bind", bind)
