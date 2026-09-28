"""PROPOSE a comparator's included-study members from its held text, for comparators whose included set is
not machine-enumerable from a citing JATS table (no open JATS, no table, or an IPD baseline table).

One recorded, replayable model call per comparator (registry/model_calls/mc-*.json); the proposal is gated by
harness.k_gap.verify_members (verbatim quote in the whole held text, label inside its quote). The gated result
is written to registry/model_proposals/comparator_members.json. Nothing here admits a trial to any pool.

    python scripts/k_gap_propose_members.py SLUG [SLUG ...]      # live (codex), concurrency 3
    python scripts/k_gap_propose_members.py --replay              # re-derive every verification from stored records
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import k_gap  # noqa: E402
from reproducible_ai import model_source as ms  # noqa: E402

PROP = os.path.join(ROOT, "registry", "model_proposals", "comparator_members.json")
REC_DIR = os.path.join(ROOT, ms.RECORD_DIR)
MODEL, EFFORT = "gpt-6-astra", "medium"
DATE = "2026-09-28"


def held_text(slug: str) -> tuple[str, str]:
    """(text, ref). Prefer the comparator's own JATS body (fetched by k_gap); else the committed held document."""
    c = json.load(open(os.path.join(ROOT, "cache", slug, "comparators.json"), encoding="utf-8"))[0]
    m = re.search(r"PMID (\d+)", c.get("citation", ""))
    pmid = m.group(1) if m else str(c["id"])
    jp = os.path.join(ROOT, "cache", "comparators", pmid, f"{DATE}_kgap_jats.xml")
    if os.path.exists(jp):
        return k_gap.jats_body_text(open(jp, "rb").read()), os.path.relpath(jp, ROOT).replace(os.sep, "/") + "#body"
    ref = c["document_ref"]
    raw = open(os.path.join(ROOT, ref), encoding="utf-8").read()
    if ref.endswith("records.json"):
        return json.loads(raw)["comparator_fulltext"], ref + "#comparator_fulltext"
    return raw, ref


def _load():
    return json.load(open(PROP, encoding="utf-8")) if os.path.exists(PROP) else {
        "task": "comparator_members", "gate": "harness.k_gap.verify_members", "items": {}}


def propose(slug: str) -> dict:
    from reproducible_ai import model_call_live
    text, ref = held_text(slug)
    prompt = (k_gap.MEMBERS_PROMPT + text + "\nTEXT>>>\n").encode("utf-8")
    rec = model_call_live.call(
        prompt, schema=k_gap.MEMBERS_SCHEMA, model=MODEL, effort=EFFORT,
        caller={"file": "scripts/k_gap_propose_members.py", "line": "propose",
                "purpose": f"comparator_members proposal for {slug} (acq/k-gap lane)"},
        input_digests=[{"ref": ref, "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                        "what": "held comparator text shown to the model (whole, not a window)"}],
        timeout_s=1500)
    path = ms.write_record(rec, REC_DIR)
    return {"slug": slug, "record_id": rec["record_id"], "state": rec["state"], "held_ref": ref,
            "held_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "record_path": os.path.relpath(path, ROOT)}


def verify_item(item: dict) -> dict:
    rec = ms.load_record(os.path.join(REC_DIR, item["record_id"] + ".json"))
    text, ref = held_text(item["slug"])
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != item["held_sha256"]:
        return {**item, "verification": {"state": "VERIFIER_REFUSED", "problems": ["HELD_TEXT_CHANGED"]}}
    if rec["state"] != "RAN_OK":
        return {**item, "verification": {"state": "VERIFIER_REFUSED", "problems": ["RECORD_NOT_RAN_OK"]}}
    try:
        claim = json.loads(ms.replay(rec).decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {**item, "verification": {"state": "VERIFIER_REFUSED", "problems": [f"UNPARSEABLE: {exc}"[:120]]}}
    return {**item, "claim": claim, "verification": k_gap.verify_members(claim, text)}


def main(argv):
    data = _load()
    if argv and argv[0] == "--replay":
        slugs = list(data["items"])
    else:
        slugs = argv
        with cf.ThreadPoolExecutor(max_workers=3) as ex:
            for r in ex.map(propose, slugs):
                print(r["slug"], r["state"], r["record_id"], flush=True)
                data["items"][r["slug"]] = r
    for s in slugs:
        it = verify_item({k: v for k, v in data["items"][s].items() if k not in ("claim", "verification")})
        data["items"][s] = it
        v = it["verification"]
        print(s, v.get("state"), "admitted", len(v.get("admitted", [])), "refused", len(v.get("refused", [])))
    os.makedirs(os.path.dirname(PROP), exist_ok=True)
    with open(PROP, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False, sort_keys=True)


if __name__ == "__main__":
    main(sys.argv[1:])
