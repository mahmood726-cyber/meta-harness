"""Acquire ONE document by URL into evidence/held_local/<dir>/<name> (NOT redistributed: gitignored; URL, sha256, bytes
and fetch time in evidence/LOCAL_ACQUISITIONS.json). For sources with no open licence: sponsor analysis plans posted
on ClinicalTrials.gov, free-to-read publisher pages. Fails closed: a body that is not the expected kind (a PDF must
start %PDF; an HTML page must not be a bot-check / error page) is never stored. Written once, like held/.
  python acquire_url.py <dir> <name> <url>"""
import datetime, hashlib, json, os, sys, urllib.request
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LEDGER = os.path.join(ROOT, "evidence", "LOCAL_ACQUISITIONS.json")
CHALLENGE = (b"Just a moment", b"Performing security verification", b"cf-challenge", b"Access Denied", b"captcha")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (evidence audit; one document)"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read()


def main(d, name, url):
    rel = f"{d}/{name}"
    p = os.path.join(ROOT, "evidence", "held_local", rel)
    status, ctype, body = fetch(url)
    if status != 200:
        sys.exit(f"REFUSED: HTTP {status}")
    if name.endswith(".pdf") and not body.startswith(b"%PDF"):
        sys.exit(f"REFUSED: expected a PDF, got {ctype} ({body[:40]!r})")
    if name.endswith(".html") and any(c.lower() in body[:20000].lower() for c in CHALLENGE):
        sys.exit("REFUSED: the page is a bot-check or error page, not the document")
    digest = hashlib.sha256(body).hexdigest()
    led = json.load(open(LEDGER, encoding="utf-8"))
    if os.path.exists(p):
        if hashlib.sha256(open(p, "rb").read()).hexdigest() != digest:
            sys.exit(f"REFUSED: {rel} is held with different bytes; not overwritten")
        print(f"{rel}: already held, identical"); return 0
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "wb").write(body)
    led[rel] = {"url": url, "sha256": digest, "bytes": len(body),
                "fetched_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "why_local": "no open licence stated; held for span verification only, not redistributed"}
    json.dump(led, open(LEDGER, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(f"{rel}: held LOCAL ({len(body)} bytes, sha256 {digest[:12]})")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
