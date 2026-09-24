"""Hostile re-verification of every EV53 citation against the bytes held at THIS checkout.

EV53 marks its citations verified=true. That flag is not evidence here (POLICY.md). For each citation this script
re-reads the cited file, decompresses .gz, and records: the file's current sha256 (and whether it equals the one EV53
recorded), whether the span sits at EV53's recorded character offset, and whether it occurs anywhere in the file.
Output: evidence/p5_populations/ev53_reverify.json. Nothing is inferred; a citation with no document_ref is counted as
NO_DOCUMENT_REF, never as verified."""
import json, os, gzip, hashlib, subprocess, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EV = json.load(open(os.path.join(ROOT, "evidence", "inputs", "ev53.json"), encoding="utf-8"))
head = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
cache = {}


def load(ref):
    if ref not in cache:
        p = os.path.join(ROOT, ref)
        if not os.path.exists(p):
            cache[ref] = None
        else:
            raw = open(p, "rb").read()
            dec = gzip.decompress(raw) if ref.endswith(".gz") else raw
            cache[ref] = (hashlib.sha256(raw).hexdigest(), hashlib.sha256(dec).hexdigest(), dec.decode("utf-8"))
    return cache[ref]


out, tally = {}, collections.Counter()
for cid, c in sorted(EV["citations"].items()):
    ref = (c.get("document_ref") or "").split("#")[0]
    rec = {"evidence_id": cid, "document_ref": c.get("document_ref"), "span": c.get("span")}
    if not ref:
        rec["state"] = "NO_DOCUMENT_REF"
    else:
        got = load(ref)
        if got is None:
            rec["state"] = "FILE_NOT_HELD_AT_CHECKOUT"
        else:
            raw_sha, dec_sha, text = got
            span = c.get("span") or ""
            off = c.get("offset")
            rec["file_sha256_now"], rec["decoded_sha256_now"] = raw_sha, dec_sha
            rec["file_unchanged"] = (c.get("document_sha256") in (raw_sha, dec_sha)) or (c.get("decoded_sha256") in (raw_sha, dec_sha))
            at_offset = isinstance(off, int) and text[off:off + len(span)] == span
            anywhere = text.find(span) if span else -1
            rec["at_recorded_offset"], rec["found_at"] = at_offset, anywhere
            if not span:
                rec["state"] = "EMPTY_SPAN"
            elif at_offset and rec["file_unchanged"]:
                rec["state"] = "REVERIFIED_EXACT"
            elif anywhere >= 0:
                rec["state"] = "REVERIFIED_RELOCATED"
            else:
                rec["state"] = "NOT_FOUND"
    tally[rec["state"]] += 1
    out[cid] = rec
json.dump({"checkout": head, "N": len(out), "tally": dict(tally), "citations": out},
          open(os.path.join(ROOT, "evidence", "p5_populations", "ev53_reverify.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print(head[:8], dict(tally), "of", len(out))
