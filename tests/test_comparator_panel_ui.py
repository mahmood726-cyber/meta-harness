"""Offline served comparator-panel contract, using an installed browser."""
import functools
import http.server
import json
import os
from pathlib import Path
import threading

import pytest

pytest.importorskip("playwright", reason="browser E2E; not installed in CI")
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def test_all_served_comparator_panels():
    candidates = [Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft/Edge/Application/msedge.exe",
                  Path(os.environ.get("PROGRAMFILES", "")) / "Google/Chrome/Application/chrome.exe"]
    exe = next((p for p in candidates if p.is_file()), None)
    assert exe, "Installed browser required; no download"
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 8000),
        functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=str(exe), headless=True)
            try:
                page = browser.new_page()
                page.route("**/*", lambda route: route.continue_() if route.request.url.startswith("http://127.0.0.1:8000/") else route.abort())
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                paths = sorted((ROOT / "docs/reviews").glob("*/review.json"))
                assert len(paths) == 32
                for path in paths:
                    review = json.loads(path.read_text(encoding="utf-8"))
                    assert page.goto(f"http://127.0.0.1:8000/docs/reviews/{path.parent.name}/index.html").status == 200
                    page.locator('button[data-t="comparator"]').click()
                    tab = page.locator("#tab-comparator")
                    assert tab.is_visible()
                    assert tab.locator("article[data-comparator]").count() == len(review["comparator_panel"])
                    if path.parent.name == "glp1-ra-mace-t2d":
                        assert tab.locator("article[data-comparator]").count() == 5
                        assert tab.inner_text().count("NOT HELD — identity only") == 4
                        assert "0.7777777777777778" in tab.inner_text()
                        assert "not independent replication" in tab.inner_text()
                    assert not errors
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
