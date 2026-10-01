"""Keep fixed-port browser contracts isolated across concurrent Windows lanes, and keep tests out of the repository that runs them."""
import errno
import http.server
import os
import socket
import time

import pytest

# A git hook exports GIT_DIR / GIT_INDEX_FILE / GIT_WORK_TREE for ITS repository. A test that runs `git init` + `git commit` in a temp
# dir inherits them and writes into the real repo instead (2026-09-27: test_heldout/test_target, run by the pre-commit hook, moved
# v1.0.1/pool-pin onto fixture commits and set core.bare=true). Strip every repository-locating variable at import (collection
# included) and again per test.
GIT_LOCATING = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
                "GIT_COMMON_DIR", "GIT_PREFIX", "GIT_NAMESPACE", "GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_AUTHOR_DATE",
                "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL", "GIT_COMMITTER_DATE", "GIT_CONFIG", "GIT_CONFIG_PARAMETERS",
                "GIT_CONFIG_COUNT")
for _k in GIT_LOCATING:
    os.environ.pop(_k, None)


@pytest.fixture(autouse=True)
def no_inherited_git_repository(monkeypatch):
    for k in GIT_LOCATING:
        monkeypatch.delenv(k, raising=False)


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
