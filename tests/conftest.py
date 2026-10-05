"""Keep fixed-port browser contracts isolated across concurrent Windows lanes."""
import errno
import http.server
import os
import socket
import time

import pytest

# A suite run from a git hook inherits GIT_DIR / GIT_INDEX_FILE / GIT_WORK_TREE; any test's scratch `git init` would then
# re-initialise the LIVE repository (core.bare=true, a test identity: three lane clones, 19 Sep - 4 Oct 2026; tests/test_target.py,
# tests/test_incremental_rebuild.py and tests/test_search_completeness.py run `git init` with no scrub of their own).
# Tests address repositories by cwd, never by an inherited GIT_*. Plant: tests/test_git_env_never_reaches_a_live_repo.py
for _k in [k for k in os.environ if k.startswith("GIT_") and k not in ("GIT_TERMINAL_PROMPT", "GIT_ASKPASS", "GIT_SSH_COMMAND")]:
    del os.environ[_k]


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
