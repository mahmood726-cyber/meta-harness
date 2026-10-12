"""Register in outputs/k_gap/fulltext_index.json the PMC copies of DEV trials held in the RoB 2 local store, so the
recorder's licence guard can tell a CC copy from a closed one.

The licence is read from the PMC copy's OWN <permissions>, in the PMC XML the acquisition stored
(scripts/rob2_fulltext_acquire.py, sha256 recorded), by the NARROW test (robgrade/prompt_licence: CC BY or CC0 only,
and never a text the tracked audit rates NOT_CC). The index's 'CC' is what the recorder's guard opens, so a CC BY-NC /
-ND / -SA copy is NOT registered (2026-10-12 D8 incident: reproducible_ai.record_licence.jats_licence calls any Creative
Commons licence 'CC', and two NC/ND texts reached a prompt that way). Only TERMS are written: no text enters the index. An entry that
already carries a copy_licence is never changed. The file keeps its own format: insertion order, UTF-8, LF. A plain
json.dump with sort_keys would reformat every entry; scripts/g1_trial_acquire.pmc_copy does that, and is not used.
DEV only (outputs/robgrade/split.json): TEST prompts never change.

    python scripts/rob2_register_cc.py
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import rob2_fulltext_acquire as acq  # noqa: E402
from robgrade import prompt_licence as pl  # noqa: E402

IDX = os.path.join(ROOT, "outputs", "k_gap", "fulltext_index.json")


def pmcid_norm(x):
    x = str(x or "").strip().upper()
    return x if x.startswith("PMC") else ("PMC" + x if x.isdigit() else None)


def main():
    split = json.load(open(os.path.join(ROOT, "outputs", "robgrade", "split.json"), encoding="utf-8"))
    with open(IDX, "rb") as fh:
        idx = json.loads(fh.read().decode("utf-8"))
    out = {}
    for p in split["dev"]:
        _, meta = acq.held(p)
        if not meta or meta.get("state") != "HELD" or meta.get("via") or not meta.get("pmcid"):
            continue                                  # PMC copies only: an Unpaywall copy has no PMC permissions
        pmcid = pmcid_norm(meta["pmcid"])
        e = idx.get(p) or {}
        if e.get("copy_licence"):
            out[p] = f"KEPT ({e['copy_licence']})"
            continue
        if e.get("pmcid") and pmcid_norm(e["pmcid"]) != pmcid:
            out[p] = f"SKIPPED: index names {e['pmcid']}, store {pmcid}"
            continue
        xml_path = os.path.join(acq.store_path(p), "pmc.xml")
        xml = open(xml_path, encoding="utf-8").read()
        perm = " ".join(re.findall(r"<permissions>.*?</permissions>", xml, re.S))
        stmt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", perm)).strip()[:300] or None
        narrow = pl.prompt_licence(xml)
        if narrow not in pl.OPEN_FOR_PROMPT or pl.tracked_verdict(p) == "NOT_CC":
            out[p] = f"NOT REGISTERED ({narrow}; tracked {pl.tracked_verdict(p)})"
            continue
        lic = "CC"
        e = dict(e, pmcid=pmcid, copy_pmcid=pmcid, copy_licence=lic, copy_statement=stmt,
                 copy_source=f"scripts/rob2_register_cc.py from the stored PMC XML (sha256 {meta.get('xml_sha256')})")
        idx[p] = e
        out[p] = lic
    with open(IDX, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(idx, indent=1, ensure_ascii=False) + "\n")
    from collections import Counter
    print(dict(Counter(out.values())))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
