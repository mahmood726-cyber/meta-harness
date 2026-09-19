"""Locate a verbatim span in a HELD extracted text by an anchor regex, and print it as a span object the regulatory
manifest can carry: {kind, span, offset, extracted_text_sha256, pdf_page}. The span text is the held bytes at the
match, never typed; the script refuses when the anchor matches zero or several places (a span is one place).

usage: python scripts/locate_held_span.py <held .txt path> <kind> <anchor regex> [--lines N]
  --lines N   extend the span to N full lines starting at the match (table rows spread over lines)
"""
import argparse
import hashlib
import json
import re
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("kind")
    ap.add_argument("anchor")
    ap.add_argument("--lines", type=int, default=0)
    a = ap.parse_args()
    raw = open(a.path, "rb").read()
    digest = hashlib.sha256(raw).hexdigest()
    text = raw.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    hits = list(re.finditer(a.anchor, text))
    if len(hits) != 1:
        print(json.dumps({"refused": f"anchor matched {len(hits)} places; a span is one place", "kind": a.kind}))
        return 1
    m = hits[0]
    start, end = m.start(), m.end()
    if a.lines:
        end = start
        for _ in range(a.lines):
            nl = text.find("\n", end + 1)
            end = len(text) if nl < 0 else nl
    span = text[start:end]
    pages = re.findall(r"(?m)^(?:### PAGE |===== page )(\d+)(?: =====)?\s*$", text[:start])
    out = {"kind": a.kind, "span": span, "offset": start, "extracted_text_sha256": digest,
           "pdf_page": int(pages[-1]) if pages else None, "located_by": "scripts/locate_held_span.py", "anchor": a.anchor}
    sys.stdout.write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
