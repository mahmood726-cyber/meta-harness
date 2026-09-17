"""Browser E2E: every release is visible and its downloadable object is identical."""
import functools
import http.server
import json
import os
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def test_all_certificate_blocks_and_downloads():
    candidates = [Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft/Edge/Application/msedge.exe",
                  Path(os.environ.get("PROGRAMFILES", "")) / "Google/Chrome/Application/chrome.exe"]
    exe = next((p for p in candidates if p.is_file()), None)
    assert exe, "Local browser required; no downloads"
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 8000), functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=str(exe), headless=True)
            try:
                page = browser.new_page()
                page.route("**/*", lambda r: r.continue_() if r.request.url.startswith(
                    "http://127.0.0.1:8000/") else r.abort())
                errors = []
                page.on("pageerror", lambda e: errors.append(str(e)))
                for directory in sorted((ROOT / "docs/reviews").iterdir()):
                    cert = json.loads((directory / "CERTIFICATE.json").read_text(encoding="utf-8"))
                    url = f"http://127.0.0.1:8000/docs/reviews/{directory.name}/"
                    assert page.goto(url + "index.html").status == 200
                    block = page.locator("#evidence-certificate")
                    assert block.is_visible()
                    assert block.locator("p").first.inner_text() == "release_sha256 " + cert["release_sha256"]
                    assert json.loads(block.locator("pre").inner_text()) == cert
                    assert "an auditor with the bundle recomputes release_sha256 from the listed inputs" in block.inner_text()
                    block.get_by_role("link", name="Download CERTIFICATE.json").click()
                    assert page.url == url + "CERTIFICATE.json"
                    assert json.loads(page.locator("body").inner_text()) == cert
                    assert not errors, errors
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
