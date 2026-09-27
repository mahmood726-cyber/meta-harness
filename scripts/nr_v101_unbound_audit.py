"""ENDPOINT_UNBOUND rows whose OWN span names the target endpoint (read-only).

  python scripts/nr_v101_unbound_audit.py BUILD_DIR [--out REPORT.json]

For every served row (pooled or declared-absent) refused/set aside as ENDPOINT_UNBOUND, its own result span
(endpoint_result_span, else source) is checked against the target outcome: the span NAMES the target when one of the
outcome's own keywords occurs in it (folded: case, British/American spelling, hospitalization/hospitalised/hospitalized
verb forms), or when its components include every canonical component of the target. Such a row is a binder false-unbound
candidate: the endpoint was stated, the binder did not read it.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import target_endpoint as te  # noqa: E402


def _fold(s: str) -> str:
    s = te._fold(s)
    return re.sub(r"\bhospitali[sz](?:ation|ations|ed|e)\b", "hospitaliz", s)


def main(argv):
    build = Path(argv[0])
    rep = {"unbound": 0, "names_target": [], "by_slug": {}}
    for f in sorted(build.glob("*.review.json")):
        slug = f.name[:-len(".review.json")]
        cfg = json.loads((ROOT / "topics" / f"{slug}.json").read_text(encoding="utf-8"))
        specs = {o["name"]: o for o in [cfg["primary_outcome"]] + (cfg.get("secondary_outcomes") or [])
                 + (cfg.get("harm_outcomes") or [])}
        rv = json.loads(f.read_text(encoding="utf-8"))
        for o in rv.get("outcomes") or []:
            spec = specs.get(o.get("name")) or {"name": o.get("name")}
            kws = [_fold(k) for k in (spec.get("keywords") or []) if len(str(k)) > 3
                   and _fold(k) not in ("primary outcome", "primary endpoint", "primary end point")]
            canon = set(te.canonical_components(spec))
            for kind in ("trials", "declared_absent_trials"):
                for t in o.get(kind) or []:
                    if "ENDPOINT_UNBOUND" not in (t.get("reason_code"), t.get("endpoint_admissibility")):
                        continue
                    rep["unbound"] += 1
                    span = t.get("endpoint_result_span") or t.get("source") or ""
                    fs = _fold(span)
                    kw = [k for k in kws if k in fs]
                    comps = te._mentions_from_text(span, expand_named_composites=False)
                    if kw or (canon and canon <= comps):
                        rep["names_target"].append({"slug": slug, "outcome": o.get("name"), "id": t.get("id"),
                                                    "keywords_in_span": kw, "span": span[:240],
                                                    "binding_reason": t.get("endpoint_binding_reason")})
                        rep["by_slug"][slug] = rep["by_slug"].get(slug, 0) + 1
    print(f"ENDPOINT_UNBOUND rows whose own span names the target: {len(rep['names_target'])} of {rep['unbound']}; "
          f"by topic {rep['by_slug']}")
    if "--out" in argv:
        Path(argv[argv.index("--out") + 1]).write_text(json.dumps(rep, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
