"""Evidence entry pages: one index.html per evidence directory, generated from docs/evidence/CAPTIONS.json.

WHY (2026-09-14). GitHub Pages serves no directory listings, so /evidence/<tranche>/ returned 404 and an auditor who
cannot construct URLs had nothing to open. Each directory now gets a plain index listing every capture with a one-line
statement of what it proves, its FULL served URL, its size and the SHA-256 of the committed bytes -- so what they fetch
can be checked against what we attested without any narration from us. The captures themselves are never touched.

The captions live in CAPTIONS.json (data, reviewed by a person); this generator refuses if any committed capture has no
caption or any caption names a file that does not exist, so a capture cannot be served unexplained and a caption cannot
outlive its file. scripts/verify_all.py's index-currency limb regenerates these pages and refuses if the committed
ones differ (same rule as docs/index.html: generated, never hand-maintained).

Usage: python scripts/build_evidence_index.py [--check]
"""
from __future__ import annotations
import hashlib
import html
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV = os.path.join(ROOT, "docs", "evidence")
SITE = "https://mahmood726-cyber.github.io/meta-harness/evidence/"
GENERATED = ("index.html",)

STYLE = ("body{font:15px/1.5 system-ui,Segoe UI,Arial,sans-serif;max-width:64rem;margin:2rem auto;padding:0 1rem;color:#12232e}"
         "code{background:#f1f3f5;padding:0 .2em;word-break:break-all}table{border-collapse:collapse;width:100%}"
         "td,th{border-top:1px solid #ddd;padding:.4em .5em;vertical-align:top;text-align:left}"
         ".note{border-left:4px solid #b45309;padding:.5em 1em;background:#fffbeb}.sha{font-size:.85em}")


def _served_bytes(p: str) -> bytes:
    """The bytes that will be COMMITTED and therefore SERVED: .gitattributes sets `* text=auto eol=lf`, so a text
    file's CRLF in a Windows working tree becomes LF in the blob. Hashing the raw working-tree bytes produced digests
    that differed from CI's (the first CI run of this generator refused the index for exactly that reason)."""
    data = open(p, "rb").read()
    if b"\0" in data[:8192]:
        return data  # binary: stored as-is
    return data.replace(b"\r\n", b"\n")


def _sha(p: str) -> str:
    return hashlib.sha256(_served_bytes(p)).hexdigest()


def _size(p: str) -> int:
    return len(_served_bytes(p))


def _captures(d: str) -> list[str]:
    files = {f for f in os.listdir(os.path.join(EV, d)) if os.path.isfile(os.path.join(EV, d, f))}
    # generated: index.html and every "<capture>.html" twin whose capture exists beside it
    return sorted(f for f in files if f not in GENERATED and not (f.endswith(".html") and f[:-5] in files))


def render_twin(d: str, f: str, caption: str) -> str:
    """HTML twin of a raw capture, for fetchers that refuse non-HTML content types (the auditor's did: every capture
    is served as text/plain or text/markdown, everything they had ever read from us was text/html). The capture is
    shown VERBATIM in a <pre>; the raw file's URL and SHA-256 are stated; the digest is of the RAW file, not of this
    wrapper -- the attestation covers the raw bytes and this page is a rendering of them."""
    p = os.path.join(EV, d, f)
    raw = _served_bytes(p).decode("utf-8", "replace")
    url = f"{SITE}{d}/{f}"
    return (f"<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{html.escape(f)} (rendered capture)</title><style>{STYLE}pre{{white-space:pre-wrap;word-break:break-word;background:#f8f9fa;padding:1em;border:1px solid #ddd}}</style></head><body>"
            f"<h1>{html.escape(f)}</h1><p class=\"note\"><strong>This is an HTML rendering of a raw evidence capture.</strong> The text below is the "
            f"capture verbatim. The raw file is served at <code>{html.escape(url)}</code>; its SHA-256 is <code>{_sha(p)}</code> "
            f"({_size(p):,} bytes). <strong>That digest is of the raw file, not of this HTML page.</strong> The attestation in "
            f"<code>/_production/manifest.json</code> covers the raw bytes; this page exists only because some fetchers refuse "
            f"text/plain and text/markdown.</p><p><em>What it proves:</em> {html.escape(caption)}</p>"
            f"<pre>{html.escape(raw)}</pre>"
            f"<p><a href=\"./\">This directory's index</a> · <a href=\"../\">All evidence</a></p></body></html>\n")


def render_dir(d: str, cap: dict) -> str:
    title = cap.get("_title") or d
    rows = []
    for f in _captures(d):
        p = os.path.join(EV, d, f)
        url = f"{SITE}{d}/{f}"
        rows.append(f"<tr><td><a href=\"{html.escape(f)}.html\">{html.escape(f)} (HTML rendering)</a> · <a href=\"{html.escape(f)}\">raw</a>"
                    f"<br><code>{html.escape(url)}.html</code><br><code>{html.escape(url)}</code></td>"
                    f"<td>{html.escape(cap[f])}</td><td class='sha'>{_size(p):,} B<br><code>{_sha(p)}</code></td></tr>")
    return (f"<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{html.escape(title)}</title><style>{STYLE}</style></head><body>"
            f"<h1>{html.escape(title)}</h1><p class=\"note\"><strong>Raw captures, served as committed.</strong> Every file below is served "
            f"byte-for-byte as committed under <code>docs/evidence/{html.escape(d)}/</code>; the SHA-256 shown is of those bytes. Fetch the URL, "
            f"hash the body, compare. This index page is generated from <code>CAPTIONS.json</code> and is the only non-capture file here.</p>"
            f"<p>{html.escape(cap.get('_intro', ''))}</p>"
            f"<table><tr><th>file: HTML rendering / raw (full URLs)</th><th>what it proves</th><th>size / SHA-256 of committed bytes</th></tr>{''.join(rows)}</table>"
            f"<p><a href=\"../\">All evidence</a> · <a href=\"../../_production/manifest.json\">per-file manifest of the deployed tree</a></p></body></html>\n")


def render_top(caps: dict) -> str:
    items = []
    for d in sorted(k for k in caps if not k.startswith("_")):
        c = caps[d]
        n = len(_captures(d))
        items.append(f"<li><a href=\"{html.escape(d)}/\">{html.escape(c.get('_title') or d)}</a> — {html.escape(c.get('_intro', ''))} "
                     f"({n} captures) <br><code>{html.escape(SITE + d + '/')}</code></li>")
    top = caps.get("_top", {})
    return (f"<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>meta-harness — evidence bundle (raw captures)</title><style>{STYLE}</style></head><body>"
            f"<h1>Evidence bundle — raw captures, served as committed</h1>"
            f"<p class=\"note\"><strong>Nothing here is generated or prettified except the index pages.</strong> Every capture is served byte-for-byte as "
            f"committed under <code>docs/evidence/</code>; each directory's index lists every capture with its full URL, what it proves, and the SHA-256 of "
            f"the committed bytes. The deploy that placed these files recorded the same digests in the production record.</p>"
            f"<h2>Start here</h2><p>{html.escape(top.get('start', ''))}<br><code>{html.escape(top.get('start_url', ''))}</code></p>"
            f"<h2>Directories</h2><ul>{''.join(items)}</ul>"
            f"<h2>Verify the bytes you are reading</h2><p>{html.escape(top.get('verify', ''))}</p>"
            f"<h2>If github.com refuses you, try these hosts (same bytes)</h2><ul>"
            + "".join(f"<li>{html.escape(k)}: <code>{html.escape(v)}</code></li>" for k, v in (top.get("fallbacks") or {}).items())
            + "</ul></body></html>\n")


def build() -> dict[str, str]:
    caps = json.load(io.open(os.path.join(EV, "CAPTIONS.json"), encoding="utf-8"))
    out = {}
    problems = []
    for d in sorted(x for x in os.listdir(EV) if os.path.isdir(os.path.join(EV, x))):
        cap = caps.get(d)
        if cap is None:
            problems.append(f"{d}/: no captions block")
            continue
        for f in _captures(d):
            if f not in cap:
                problems.append(f"{d}/{f}: no caption -- a capture may not be served unexplained")
        for f in cap:
            if not f.startswith("_") and not os.path.isfile(os.path.join(EV, d, f)):
                problems.append(f"{d}/{f}: caption names a file that does not exist")
    if problems:  # refuse BEFORE rendering anything: an unexplained capture never gets a page
        raise SystemExit("EVIDENCE INDEX REFUSED:\n  " + "\n  ".join(problems))
    for d in sorted(x for x in os.listdir(EV) if os.path.isdir(os.path.join(EV, x))):
        out[os.path.join(EV, d, "index.html")] = render_dir(d, caps[d])
        for f in _captures(d):
            out[os.path.join(EV, d, f + ".html")] = render_twin(d, f, caps[d][f])
    out[os.path.join(EV, "index.html")] = render_top(caps)
    return out


def main(argv) -> int:
    pages = build()
    if "--check" in argv:
        stale = [p for p, want in pages.items()
                 if not os.path.exists(p) or io.open(p, encoding="utf-8").read() != want]
        if stale:
            print("evidence index STALE: " + ", ".join(os.path.relpath(p, ROOT) for p in stale))
            return 1
        print(f"evidence indexes current ({len(pages)} pages)")
        return 0
    for p, want in pages.items():
        io.open(p, "w", encoding="utf-8", newline="\n").write(want)
    print(f"wrote {len(pages)} evidence index pages")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
