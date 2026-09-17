"""Local browser contract for HM2 pages; no remote requests or browser downloads."""
import functools
import http.server
import json
import os
from pathlib import Path
import threading

import pytest
pytest.importorskip("playwright", reason="browser E2E; not installed in CI")
from playwright.sync_api import sync_playwright


def test_hm2_harm_tables_render_in_browser():
    root = Path(__file__).resolve().parents[1]
    evidence = json.loads((root / "outputs/handover/HM2_item_evidence.json").read_text(encoding="utf-8"))
    candidates = [Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft/Edge/Application/msedge.exe",
                  Path(os.environ.get("PROGRAMFILES", "")) / "Google/Chrome/Application/chrome.exe"]
    executable = next((p for p in candidates if p.is_file()), None)
    assert executable, "A locally installed browser is required; no download is permitted"
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 8000), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=str(executable), headless=True)
            try:
                page = browser.new_page()
                page.route("**/*", lambda route: route.continue_()
                           if route.request.url.startswith("http://127.0.0.1:8000/") else route.abort())
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                for slug in sorted({i["slug"] for i in evidence}):
                    response = page.goto(f"http://127.0.0.1:8000/docs/reviews/{slug}/index.html")
                    assert response.status == 200
                    page.locator('button[data-t="harms"]').click()
                    panel = page.locator("#tab-harms")
                    assert panel.is_visible()
                    text = panel.inner_text()
                    for item in evidence:
                        if item["slug"] == slug:
                            assert item["pmid"] in text
                    assert "{{" not in text
                    if slug == "colchicine-postop-af":
                        page.locator('button[data-t="outcomes"]').click()
                        results = page.locator("#tab-outcomes").inner_text()
                        assert "mixed / trial-defined" in results
                        assert "AVAILABLE_CASE" in results and "not_stated" in results
                    assert not errors, errors
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
