"""Tiny stdlib HTTP helpers (no third-party deps) with bounded retries.

Used only by the fetch step, which runs ONCE and writes a committed cache. The
offline pipeline (screen/extract/synthesise/render) never touches the network, so a
fresh clone reproduces byte-for-byte from the committed cache alone.
"""
from __future__ import annotations
import json
import time
import urllib.parse
import urllib.request

UA = "meta-harness/1.0 (reproducible-ma; mailto:meta-harness@example.org)"


def get(url: str, params: dict | None = None, tries: int = 4, timeout: int = 30) -> bytes:
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as exc:  # noqa: BLE001 - bounded retry, then raise
            last = exc
            time.sleep(0.5 * (2 ** i))
    raise RuntimeError(f"GET failed after {tries} tries: {url}\n{last}")


def get_json(url: str, params: dict | None = None, **kw) -> dict:
    return json.loads(get(url, params, **kw).decode("utf-8"))


def get_text(url: str, params: dict | None = None, **kw) -> str:
    return get(url, params, **kw).decode("utf-8", "replace")
