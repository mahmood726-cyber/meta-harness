"""The committed schema-v2 files reproduce from the repo alone.

For every committed witness extraction (evidence/typed_arms/extractions_witness[_served]/<job>/{row.json,out.json}),
rebuild each packet document FROM ITS RECORDED ORIGIN in this checkout, require its sha256 to equal the one recorded in
row.json (held-source drift is a failure, not a silent pass), re-run check_witness and write_v2, and require the result
to equal the committed OBSERVATIONS_<population>.json row for row (written rows, their observations, and the set of
rows not written). Skipped, with the reason, when the checkout does not hold the cited cache files (a sparse clone)."""
import hashlib, importlib.util, json, os, re, shutil, sys
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TA = os.path.join(ROOT, "evidence", "typed_arms")


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def rebuild(origin):
    """Bytes of a packet document from its recorded origin."""
    m = re.fullmatch(r"(cache/[^#]+/records\.json)#records\[(\d+)\] \(title\+abstract\)", origin)
    if m:
        rec = json.load(open(os.path.join(ROOT, m.group(1)), encoding="utf-8"))["records"][int(m.group(2))]
        return f"TITLE: {rec.get('title') or ''}\n\n{rec.get('abstract') or ''}\n".encode("utf-8")
    m = re.fullmatch(r"(cache/[^#]+/records\.json)#ctgov_results\.(NCT\d+) \(re-serialised indent=1\)", origin)
    if m:
        d = json.load(open(os.path.join(ROOT, m.group(1)), encoding="utf-8"))
        return json.dumps(d["ctgov_results"][m.group(2)], indent=1, ensure_ascii=False).encode("utf-8")
    return open(os.path.join(ROOT, origin), "rb").read()


@pytest.mark.parametrize("population,extractions", [("served", "extractions_witness_served"), ("held", "extractions_witness")])
def test_committed_v2_observations_reproduce(tmp_path, population, extractions):
    src = os.path.join(TA, extractions)
    jobs = sorted(os.listdir(src))
    needed = {d["origin"].split("#")[0] for j in jobs
              for d in json.load(open(os.path.join(src, j, "row.json"), encoding="utf-8"))["documents"] if d.get("file")}
    missing = sorted(p for p in needed if not os.path.exists(os.path.join(ROOT, p)))
    if missing:
        pytest.skip(f"{len(missing)} cited documents not held in this checkout, e.g. {missing[:2]}")
    cw = _load(os.path.join(TA, "witness", "check_witness.py"), "check_witness")
    wv = _load(os.path.join(TA, "v2", "write_v2.py"), "write_v2")
    packets, recs = tmp_path / "packets", tmp_path / "records"
    packets.mkdir()
    recs.mkdir()
    for j in jobs:
        d = packets / j
        d.mkdir()
        row = json.load(open(os.path.join(src, j, "row.json"), encoding="utf-8"))
        for doc in row["documents"]:
            if not doc.get("file"):
                continue
            b = rebuild(doc["origin"])
            assert hashlib.sha256(b).hexdigest() == doc["sha256"], (j, doc["file"], "held bytes changed")
            (d / doc["file"]).write_bytes(b)
        for f in ("row.json", "out.json"):
            shutil.copy(os.path.join(src, j, f), d / f)
        (recs / f"{j}.json").write_text(json.dumps(cw.check_job(str(d))), encoding="utf-8")
    out = tmp_path / "out.json"
    sys.argv = ["write_v2", population, str(recs), str(packets), str(out)]
    wv.main()
    got = json.load(open(out, encoding="utf-8"))
    want = json.load(open(os.path.join(TA, "v2", f"OBSERVATIONS_{population}.json"), encoding="utf-8"))
    assert got["rows"] == want["rows"]
    assert sorted(got["not_written_rows"]) == sorted(want["not_written_rows"])
    assert got["written"] == want["written"]
