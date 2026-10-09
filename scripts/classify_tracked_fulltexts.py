"""V13-04Q (signed 9 Oct, 'sign v13' / 'yes to all recommended'): classify every trial full text TRACKED in the repo by its
typed licence, recorded -- never by hand.

For each tracked cache/<slug>/ft_<pmid>.(txt|xml|pdf):
  * europepmc_licence -- the ARTICLE's licence, as Europe PMC records it (field `license`, REST 'core'), via
    scripts/g1_licence.licence: looked up once and cached in outputs/k_gap/g1_binding/licences.json (metadata only);
  * pmc_copy_licence  -- the PMC copy's permissions, if outputs/k_gap/fulltext_index.json already read them.
Verdict:
  KEEP_CC     Europe PMC licence is CC BY or CC0 (the D8 rule: only these may be redistributed);
  NOT_CC      any other licence, CC BY-NC/ND/SA included;
  UNKNOWN     no licence recorded (closed, never open).
NOT_CC and UNKNOWN texts are REMOVAL CANDIDATES. Each is removed only with a rebuild proving no served number moves;
any text a number depends on comes back to Mahmood as its own item (V13-04Q).

    python scripts/classify_tracked_fulltexts.py [--offline]
Writes registry/tracked_fulltext_licences.json.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
OUT = os.path.join(ROOT, "registry", "tracked_fulltext_licences.json")
INDEX = os.path.join(ROOT, "outputs", "k_gap", "fulltext_index.json")
OPEN = {"cc by", "cc-by", "cc0", "cc-0", "public domain"}


def tracked_fulltexts(root=ROOT):
    out = subprocess.run(["git", "-C", root, "ls-files", "cache"], capture_output=True, text=True, check=True).stdout
    rows = []
    for f in out.split():
        base = os.path.basename(f)
        if base.startswith("ft_") and base.rsplit(".", 1)[-1] in ("txt", "xml", "pdf"):
            pmid = base[3:].rsplit(".", 1)[0]
            if pmid.isdigit():
                rows.append({"file": f, "slug": f.split("/")[1], "pmid": pmid})
    return rows


def verdict(europepmc_licence):
    lic = (europepmc_licence or "").strip().lower()
    if not lic:
        return "UNKNOWN"
    return "KEEP_CC" if lic in OPEN else "NOT_CC"


def classify(offline=False, root=ROOT):
    import g1_licence
    idx = json.load(open(INDEX, encoding="utf-8")) if os.path.exists(INDEX) else {}
    rows = []
    for r in tracked_fulltexts(root):
        lic = g1_licence.licence(r["pmid"], offline=offline)
        e = idx.get(r["pmid"]) or {}
        rows.append(dict(r, europepmc_licence=lic.get("license"), europepmc_state=lic.get("state", "CACHED"),
                         pmcid=lic.get("pmcid") or e.get("pmcid"), pmc_copy_licence=e.get("copy_licence"),
                         verdict=verdict(lic.get("license"))))
    return rows


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    rows = classify(offline="--offline" in argv)
    tally = {}
    for r in rows:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    doc = {"_doc": ("V13-04Q: every tracked trial full text classified by its typed Europe PMC article licence (scripts/"
                    "classify_tracked_fulltexts.py; licences cached in outputs/k_gap/g1_binding/licences.json). NOT_CC and "
                    "UNKNOWN are removal candidates, each removed only with a no-number-moved rebuild."),
           "tally": tally, "rows": rows}
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(json.dumps(tally))
    return 0


if __name__ == "__main__":
    sys.exit(main())
