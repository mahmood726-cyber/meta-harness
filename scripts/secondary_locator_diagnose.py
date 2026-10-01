"""Diagnose every recorded verification-locator answer the quote gate refused: WHY was it refused?

For each locator run in registry/secondary_meta/runs.json the record's own PROMPT bytes (what the model saw) and RESPONSE
bytes (what it answered) are read back, and each refusal is classified -- deterministic, no network, no model:

  TEXT_HELD_BUT_NOT_SHOWN   a held full text existed (cache/<slug>/ft_<pmid>.txt, or a PMC/Unpaywall cache) but the
                            prompt carried only the abstract -- the same wall as pool construction ignoring held texts
  ABSTRACT_ONLY_NO_OA       no full text exists anywhere we may legally read; the abstract alone was shown
  MODEL_SAID_NOT_REPORTED   the model answered NOT_REPORTED on the text it was shown
  QUOTE_NOT_IN_SHOWN_TEXT   the quote is not in the shown text even after normalisation  -> model error
  QUOTE_MATCHES_AFTER_NORM  the quote IS in the shown text once dashes / spaces / mid-dots / NBSP are folded -> GATE too strict
  NUMBER_FORMAT_ONLY        a copied number is in the quote once formatting is folded (0·87, -/minus, 1,234)  -> GATE too strict
  NUMBER_TRULY_ABSENT       a copied number is not in the quote in any format                     -> model error
  NON_NUMERIC_VALUE         a copied value is not a number ('0:31')
  INCOMPLETE_ANSWER         reported, numerically clean, but neither a full effect+CI nor full arm counts

    python scripts/secondary_locator_diagnose.py   -> outputs/k_gap/locator_diagnosis.json
"""
from __future__ import annotations

import base64
import io
import json
import os
import re
import sys
import unicodedata
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from reproducible_ai import model_source as ms  # noqa: E402

REC_DIR = os.path.join(ROOT, "evidence", "model_calls", "secondary")
NUMKEYS = ("point", "lower", "upper", "events_t", "n_t", "events_c", "n_c")


def _j(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def gate_norm(t):
    """What the gate (secondary_meta_build._norm_ws) compares: whitespace collapsed, U+2212 -> '-'."""
    return re.sub(r"\s+", " ", (t or "").replace("−", "-")).strip()


def full_norm(t):
    """Everything a typographer may vary without changing a number: NFKC, every dash -> '-', mid-dot -> '.', NBSP and
    thin spaces -> ' ', quotes, soft hyphen removed, whitespace collapsed."""
    t = unicodedata.normalize("NFKC", t or "")
    t = re.sub("[‐-―−﹘﹣－]", "-", t)
    t = t.replace("·", ".").replace("‧", ".").replace("­", "")
    t = re.sub("[    ]", " ", t)
    t = re.sub("[‘’“”]", "'", t)
    return re.sub(r"\s+", " ", t).strip()


def num_in(v, q, norm):
    v = norm(str(v)).replace(",", "")
    return bool(re.search(r"(?<![\d.])" + re.escape(v) + r"(?![\d])", norm(q).replace(",", "")))


def held_fulltext(slug, pmid):
    """Every full text we may legally read for this trial and could have shown: held cache/<slug>/ft_<pmid>.txt, the PMC
    OA cache, the Unpaywall cache (by DOI)."""
    out = {}
    p = os.path.join(ROOT, "cache", slug, f"ft_{pmid}.txt")
    if os.path.exists(p) and os.path.getsize(p) > 0:
        out["HELD_CACHE_FT"] = os.path.getsize(p)
    p = os.path.join(ROOT, "outputs", "k_gap", "_ft", f"{pmid}.txt")
    if os.path.exists(p) and os.path.getsize(p) > 0:
        out["PMC_OA"] = os.path.getsize(p)
    return out


def main():
    runs = _j(os.path.join(ROOT, "registry", "secondary_meta", "runs.json"))
    rows, tally = [], Counter()
    for key, r in sorted(runs.items()):
        if not key.startswith("locate::") or r.get("state") != "RAN_OK":
            continue
        _, slug, pmid, *want = key.split("::")
        rec = ms.load_record(os.path.join(REC_DIR, r["record_id"] + ".json"))
        prompt = base64.b64decode(rec["prompt"]["b64"]).decode("utf-8")
        shown = prompt.split("<<<TEXT\n", 1)[-1].rsplit("\nTEXT>>>", 1)[0]
        claim = json.loads(ms.replay(rec).decode("utf-8"))
        held = held_fulltext(slug, pmid)
        showed_ft = len(shown) > 6000                       # title + abstract alone is far shorter
        row = {"key": key, "want": want[0] if want else None, "shown_chars": len(shown), "held_fulltext": held,
               "state": claim.get("state")}
        if claim.get("state") != "REPORTED" or not claim.get("quote"):
            cause = ("TEXT_HELD_BUT_NOT_SHOWN" if held and not showed_ft else
                     "ABSTRACT_ONLY_NO_OA" if not held and not showed_ft else "MODEL_SAID_NOT_REPORTED")
        else:
            q = claim["quote"]
            in_gate = gate_norm(q) in gate_norm(shown)
            in_full = full_norm(q) in full_norm(shown)
            nums = {k: claim.get(k) for k in NUMKEYS if claim.get(k)}
            nonnum = [k for k, v in nums.items() if not re.fullmatch(r"-?\d+(?:[.,]\d+)?", full_norm(str(v)).replace(",", ""))]
            gate_miss = [k for k, v in nums.items() if not num_in(v, q, gate_norm)]
            full_miss = [k for k, v in nums.items() if not num_in(v, q, full_norm)]
            if not in_gate:
                cause = "QUOTE_MATCHES_AFTER_NORM" if in_full else "QUOTE_NOT_IN_SHOWN_TEXT"
            elif nonnum:
                cause = "NON_NUMERIC_VALUE"
            elif gate_miss:
                cause = "NUMBER_FORMAT_ONLY" if not full_miss else "NUMBER_TRULY_ABSENT"
            else:
                full_eff = all(claim.get(k) for k in ("point", "lower", "upper"))
                full_cnt = all(claim.get(k) for k in ("events_t", "n_t", "events_c", "n_c"))
                cause = "GATE_WOULD_PASS" if (full_eff or full_cnt) else "INCOMPLETE_ANSWER"
            row.update(quote=q[:200], gate_missing=gate_miss, nonnumeric=nonnum)
        row["cause"] = cause
        tally[cause] += 1
        rows.append(row)
    out = {"n": len(rows), "by_cause": dict(tally.most_common()), "rows": rows}
    with open(os.path.join(ROOT, "outputs", "k_gap", "locator_diagnosis.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print(json.dumps({k: out[k] for k in ("n", "by_cause")}, indent=1))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
