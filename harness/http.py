"""Tiny stdlib HTTP helpers (no third-party deps) with bounded retries.

Used only by the fetch step, which runs ONCE and writes a committed cache. The
offline pipeline (screen/extract/synthesise/render) never touches the network, so a
fresh clone reproduces byte-for-byte from the committed cache alone.
"""
from __future__ import annotations
import json
import time
import urllib.parse
import urllib.error
import urllib.request

UA = "meta-harness/1.0 (reproducible-ma; mailto:meta-harness@example.org)"
RECORDER = None


def _full_url(url: str, params: dict | None = None) -> str:
    if params:
        return url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    return url


def _record(url: str, params: dict | None, status, body: bytes) -> None:
    if RECORDER is not None:
        RECORDER.record_current(url, params, status, body)


def get_raw(url: str, params: dict | None = None, tries: int = 4, timeout: int = 30) -> tuple[int | str, bytes]:
    request_url = _full_url(url, params)
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(request_url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
                status = r.getcode()
                _record(url, params, int(status) if status is not None else "UNKNOWN", body)
                return int(status) if status is not None else "UNKNOWN", body
        except urllib.error.HTTPError as exc:
            last = exc
            body = exc.read() or str(exc).encode("utf-8", "replace")
            if i + 1 >= tries:
                _record(url, params, int(exc.code), body)
                raise RuntimeError(f"GET failed after {tries} tries: {request_url}\n{exc}") from exc
            time.sleep(0.5 * (2 ** i))
        except Exception as exc:  # noqa: BLE001 - bounded retry, then raise
            last = exc
            if i + 1 >= tries:
                body = str(exc).encode("utf-8", "replace")
                _record(url, params, "EXCEPTION", body)
                raise RuntimeError(f"GET failed after {tries} tries: {request_url}\n{last}") from exc
            time.sleep(0.5 * (2 ** i))
    body = str(last).encode("utf-8", "replace")
    _record(url, params, "EXCEPTION", body)
    raise RuntimeError(f"GET failed after {tries} tries: {request_url}\n{last}")


def get(url: str, params: dict | None = None, tries: int = 4, timeout: int = 30) -> bytes:
    return get_raw(url, params, tries=tries, timeout=timeout)[1]


def get_json(url: str, params: dict | None = None, **kw) -> dict:
    return json.loads(get(url, params, **kw).decode("utf-8"))


def get_text(url: str, params: dict | None = None, **kw) -> str:
    return get(url, params, **kw).decode("utf-8", "replace")
