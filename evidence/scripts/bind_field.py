"""Apply ONE reviewed typed-estimand binding to a ruling and re-run it through adjudicate.py (which re-verifies and
pins every span against the held bytes' sha256). The span must already be a verbatim substring of the render of
`ref` (use find_span.py), and `ref` must be in the row's packet (add a companion and rebuild packets first).
  python bind_field.py KEY FIELD REF "<span>" "<why, one sentence>" [--source-url URL]
For analysis_set the source's reading (set_reading) is recorded beside the served label, so a contradiction shows
up in the sweep and in LABEL_CORRECTIONS.md; the served label itself is never edited here."""
import datetime, json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
import textrep
from draft_from_extraction import set_reading
ROOT = textrep.ROOT
FIELDS = ("analysis_set", "treatment_strategy", "follow_up")


def main(key, field, ref, span, why, url=None):
    assert field in FIELDS, field
    pk = json.load(open(os.path.join(ROOT, f"evidence/packets/{key}.json"), encoding="utf-8"))
    if ref not in {s["ref"] for s in pk["sources"]}:
        sys.exit(f"REFUSED: {ref} is not a source in {key}'s packet (add a companion and rebuild packets)")
    if span not in textrep.render(ref):
        sys.exit("REFUSED: span is not verbatim in the render")
    a = json.load(open(os.path.join(ROOT, f"evidence/adjudication/{key}.json"), encoding="utf-8"))
    ev = a.setdefault("evidence", {})
    if ev.get(field):
        sys.exit(f"REFUSED: {key} already binds {field}; an existing binding is amended by hand, not overwritten")
    ev[field] = {"ref": ref, "span": span}
    te = a.setdefault("typed_estimand", {})
    if field == "analysis_set":
        cur = te.get("analysis_set") if isinstance(te.get("analysis_set"), dict) else {"earlier": te.get("analysis_set")}
        cur["source_reading"] = set_reading(span); cur["absent_reason"] = None
        te["analysis_set"] = cur
    else:
        te[field] = "bound"
    (a.get("unbound_reasons") or {}).pop(field, None)
    a.setdefault("amendments", []).append({
        "when_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "prompted_by": "source location 2026-09-25 (Claude subagents found candidates; the lane verified the span in held bytes)",
        "what": f"{field} bound: {why}" + (f" (source {url})" if url else "")})
    tmp = os.path.join(tempfile.gettempdir(), f"bind_{key}.json")
    json.dump(a, open(tmp, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    r = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "adjudicate.py"), tmp],
                       capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip()[-300:])
    return r.returncode


if __name__ == "__main__":
    a = sys.argv[1:]
    url = a[a.index("--source-url") + 1] if "--source-url" in a else None
    sys.exit(main(*a[:5], url=url))
