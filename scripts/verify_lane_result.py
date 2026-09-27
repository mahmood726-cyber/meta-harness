"""Verify a Codex acquisition lane's .lane/RESULT.json against the bytes it holds. Nothing is trusted from the lane:
  - document_ref must be under evidence/acquisition_cascade/held/, exist, and hash to document_sha256 AND to HELD.json's
    sha256 for that path (the ledger entry must say ORIGINAL_VERBATIM and carry source + retrieved_utc);
  - source_span (or raw_span) must occur in the decoded bytes exactly;
  - every number in `values` must occur as a token inside the verified span (so a value cannot come from elsewhere);
  - NOT_REPORTED must name a coverage that the lane actually holds for that PMID (ABSTRACT_VERBATIM -> a held
    europepmc_record_<pmid>.json; FULL_TEXT -> a held PMC xml / pdf / html under that trial);
  - ATTEMPTS.jsonl / HELD.json lines added by the lane are checked for off-route hosts.
  python scripts/verify_lane_result.py <lane_tree> [RESULT.json] -> writes <lane_tree>/.lane/VERIFIED[.<name>].json

Moved into the repository 2026-09-27 (was a scratch script): tests/test_verify_lane_result.py plants each defect
class. Two of its own defects were found by those plants before it was relied on: '.55' (no leading zero) rejected a
true span, and a heredoc turned the regex's word-boundary escape into a backspace byte (0x08) so the table-header
path never matched."""
import hashlib, html, json, os, re, sys
from urllib.parse import urlparse
from collections import Counter

T = sys.argv[1]
RES = sys.argv[2] if len(sys.argv) > 2 else "RESULT.json"
OUT = "VERIFIED.json" if RES == "RESULT.json" else "VERIFIED." + RES.replace("RESULT", "").strip("._") + ".json"
D = os.path.join(T, "evidence", "acquisition_cascade")
res = json.load(open(os.path.join(T, ".lane", RES), encoding="utf-8"))
ledger = json.load(open(os.path.join(D, "held", "HELD.json"), encoding="utf-8"))
OK_HOSTS = ("ebi.ac.uk", "unpaywall.org", "clinicaltrials.gov", "ncbi.nlm.nih.gov", "ema.europa.eu", "fda.gov",
            "europepmc.org", "doi.org")


def num_tokens(s):
    s = s.replace("·", ".").replace("−", "-")
    toks = set(re.findall(r"\d+(?:[.,]\d+)*", s))
    toks |= {"0" + t for t in re.findall(r"(?<![\d.])\.\d+", s)}   # '.55' is 0.55 (journals that drop the leading zero)
    return toks


def header_tokens(text, span):
    """Numbers in the column headings of the ONE table that contains the span (JATS <table-wrap>): arm sizes live there.
    Never the whole document -- a count elsewhere in the paper is not this row's denominator."""
    i = text.find(span)
    if i < 0:
        return set()
    a, b = text.rfind("<table-wrap", 0, i), text.find("</table-wrap>", i)
    if a < 0 or b < 0 or text.rfind("</table-wrap>", 0, i) > a:
        return set()
    tw = text[a:b]
    heads = re.findall(r"<thead\b.*?</thead>", tw, flags=re.S)
    return num_tokens(re.sub(r"<[^>]+>", " ", " ".join(heads))) if heads else set()


def _ws(s):
    return re.sub(r"\s+", " ", s or "").strip()


_PDF = {}


def _pdf_pages(p):
    if p not in _PDF:
        import pypdf
        try:
            _PDF[p] = [_ws(pg.extract_text() or "") for pg in pypdf.PdfReader(p).pages]
        except Exception:  # noqa: BLE001
            _PDF[p] = []
    return _PDF[p]


def fmt(v):
    if isinstance(v, bool) or v is None:
        return []
    if isinstance(v, int):
        return [str(v), f"{v:,}"]
    if isinstance(v, float):
        out = {repr(v), f"{v:.2f}", f"{v:.1f}", f"{v:.3f}"}
        return [x for x in out]
    return [str(v)]


out, tally = [], Counter()
for r in res.get("rows") or []:
    v = {"topic": r.get("topic"), "outcome": r.get("outcome"), "id": r.get("id"), "verdict": r.get("verdict"),
         "checks": [], "ok": False}
    ref = (r.get("document_ref") or "").replace("\\", "/")
    rel = ref.split("evidence/acquisition_cascade/held/", 1)[-1] if "held/" in ref else None
    if r.get("verdict") == "FOUND":
        p = os.path.join(D, "held", rel) if rel else None
        if not p or not os.path.exists(p):
            v["checks"].append("DOC_MISSING")
        else:
            raw = open(p, "rb").read()
            h = hashlib.sha256(raw).hexdigest()
            led = ledger.get(rel) or {}
            if h != r.get("document_sha256"):
                v["checks"].append("SHA_MISMATCH_LANE")
            if h != led.get("sha256"):
                v["checks"].append("SHA_MISMATCH_LEDGER")
            if led.get("representation") != "ORIGINAL_VERBATIM" or not led.get("source") or not led.get("retrieved_utc"):
                v["checks"].append("LEDGER_INCOMPLETE")
            host = urlparse(led.get("source") or "").hostname or ""
            if not any(host == x or host.endswith("." + x) for x in OK_HOSTS):
                v["checks"].append(f"SOURCE_HOST_REVIEW:{host}")  # not refused: repository copies via Unpaywall
            text = raw.decode("utf-8", "replace")
            spans = [s for s in (r.get("raw_span"), r.get("source_span")) if s]
            rep = "raw bytes"
            if rel.lower().endswith(".pdf"):
                # our OWN extraction (pypdf, whitespace collapsed within ONE page): the span and any header_span must
                # sit on the same page; nothing is taken from the lane's extraction
                pages = _pdf_pages(p)
                pg = [t for t in pages if any(_ws(s) in t for s in spans)]
                text = pg[0] if pg else ""
                spans = [_ws(s) for s in spans]
                rep = "pypdf page text"
            elif rel.lower().endswith((".html", ".htm")) and not any(s in text for s in spans):
                text = _ws(html.unescape(re.sub(r"<[^>]+>", " ", text)))
                spans = [_ws(s) for s in spans]
                rep = "tag-stripped text"
            v["representation"] = rep
            hit = [s for s in spans if s in text]
            if not hit:
                v["checks"].append("SPAN_NOT_IN_HELD_BYTES")
            else:
                toks = num_tokens(re.sub(r"<[^>]+>", " ", hit[0]))
                ht = header_tokens(text, hit[0])
                missing, via_header = [], []
                for k, x in (r.get("values") or {}).items():
                    if isinstance(x, str) or x is None or any(f in toks for f in fmt(x)):
                        continue
                    hs = r.get("header_span")
                    if k in ("n1i", "n2i") and hs and rep != "raw bytes" and _ws(hs) in _ws(text) and any(f in num_tokens(hs) for f in fmt(x)):
                        via_header.append(k)       # a denominator in the column headings the lane quoted, same page/doc
                        continue
                    if k in ("n1i", "n2i") and any(f in ht for f in fmt(x)):
                        via_header.append(k)       # a denominator, in this table's own column headings
                    else:
                        missing.append(k)
                if via_header:
                    v["denominators_from_table_header"] = via_header
                if missing:
                    v["checks"].append("VALUE_NOT_IN_SPAN:" + ",".join(missing))
            v["sha256"] = h
    elif r.get("verdict") == "NOT_REPORTED":
        pmid = re.sub(r"\D", "", r.get("id") or "")
        cov = r.get("coverage_inspected") or ""
        held_for = [k for k in ledger if k.startswith(f"PMID{pmid}/")]
        if "ABSTRACT" in cov and not any(k.endswith(f"europepmc_record_{pmid}.json") for k in held_for):
            v["checks"].append("ABSTRACT_NOT_HELD")
        if "FULL_TEXT" in cov and not any(re.search(r"\.(xml|pdf|html|txt)$", k) for k in held_for):
            v["checks"].append("FULLTEXT_NOT_HELD")
        if not cov:
            v["checks"].append("COVERAGE_UNNAMED")
    v["ok"] = not [c for c in v["checks"] if not c.startswith("SOURCE_HOST_REVIEW")]
    tally[(r.get("verdict"), v["ok"])] += 1
    out.append(v)

# off-route requests made by the lane
bad = []
for line in open(os.path.join(D, "ATTEMPTS.jsonl"), encoding="utf-8"):
    try:
        u = json.loads(line).get("url") or ""
    except ValueError:
        continue
    host = urlparse(u).hostname or ""
    if host and not any(host == x or host.endswith("." + x) for x in OK_HOSTS):
        bad.append(host)
json.dump({"rows": out, "offroute_hosts": Counter(bad)}, open(os.path.join(T, ".lane", OUT), "w",
          encoding="utf-8"), indent=1, ensure_ascii=False)
print(dict(tally)); print("non-core hosts in ATTEMPTS:", Counter(bad).most_common(15))
print("failed:", Counter(c for x in out for c in x["checks"]).most_common())
