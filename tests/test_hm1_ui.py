"""Local HTTP/browser contract for the rebuilt HM1 harm panel."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

import pytest
pytest.importorskip("playwright", reason="browser E2E; not installed in CI")
from playwright.sync_api import sync_playwright


def test_hm1_harm_panel_in_browser():
    root = Path(__file__).resolve().parents[1]
    handler = partial(SimpleHTTPRequestHandler, directory=str(root / "docs"))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)  # ephemeral port: concurrent clones each ran a server on 8000 and served each other 404s
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)
            try:
                page = browser.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.route("**/*", lambda route: route.continue_()
                           if route.request.url.startswith(f"http://127.0.0.1:{port}/") else route.abort())
                response = page.goto(f"http://127.0.0.1:{port}/reviews/probiotics-aad-prevention/",
                                     wait_until="networkidle")
                assert response.status == 200
                page.locator('button[data-t="harms"]').click()
                panel = page.locator("#tab-harms")
                assert panel.is_visible()
                text = panel.inner_text()
                assert "Any adverse events" in text and "Serious adverse events" in text
                assert "HARMS_INCOMPLETE" not in text
                assert "RETRIEVED_REFUSED_WITH_REASON" in text
                for pid in ("41699149", "39529939", "26973849", "34541475"):
                    assert pid in text
                assert not errors
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
