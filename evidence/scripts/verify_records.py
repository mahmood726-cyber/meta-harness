"""Verify every evidence record against the bytes it names. Fails closed (exit 1) on any record that does not
verify. A record verifies when, for every non-null field:
  * `ref` is a source that was IN the row's packet (no citing outside the held set),
  * the file exists and its sha256 equals the one recorded at verification time (records written by this
    script carry it; a changed file is a changed source),
  * `span` occurs in textrep.render(ref) -- the same representation the extractor was shown -- and the
    offset of every occurrence is recorded (count > 1 is flagged, not failed: the span is still verbatim),
and the numbers in `bound_values` occur as tokens in the estimate/ci spans. The served comparison is computed,
never taken from the extractor: MATCH / DIFFERS / NOT_COMPARABLE, with both values."""
import json, os, re, sys, math, hashlib, glob
sys.path.insert(0, os.path.dirname(__file__))
import textrep
ROOT = textrep.ROOT
FIELDS = ("population", "endpoint", "estimate", "ci", "analysis_set", "treatment_strategy", "follow_up")
CORE = ("population", "endpoint", "estimate", "ci")
NUMERIC = ("estimate", "ci_low", "ci_high", "events_t", "n_t", "events_c", "n_c", "mean_t", "sd_t", "mean_c", "sd_c")


def file_sha(ref):
    return hashlib.sha256(open(os.path.join(ROOT, ref.partition("#")[0]), "rb").read()).hexdigest()


def num_tokens(s):
    return set(re.findall(r"(?<![\d.])-?\d+(?:[.·]\d+)?", (s or "").replace("·", ".").replace("−", "-")))


def canon(v):
    if v is None:
        return None
    try:
        return float(str(v).replace("·", ".").replace("−", "-").replace("%", "").replace(",", ""))
    except ValueError:
        return None


def served_compare(served, bv):
    """Served effect vs the bound numbers. Direct scale: equality at the printed precision. Counts: RR/OR/RD
    recomputed; means: MD recomputed."""
    se = served.get("effect")
    sc = (served.get("scale") or "").upper()
    if bv and se is None and served.get("ai") is not None:
        pairs = [("events_t", "ai"), ("n_t", "n1i"), ("events_c", "ci"), ("n_c", "n2i")]
        got = {b: canon(bv.get(b)) for b, _ in pairs}
        if None in got.values():
            return {"state": "NOT_COMPARABLE", "why": "served row is arm counts; bound values lack a full count set"}
        same = all(got[b] == float(served[s_]) for b, s_ in pairs)
        return {"state": "MATCH" if same else "DIFFERS", "from": "arm counts",
                "served": [served[s_] for _, s_ in pairs], "bound": [got[b] for b, _ in pairs]}
    if bv and se is None and served.get("m1i") is not None:
        pairs = [("mean_t", "m1i"), ("sd_t", "sd1i"), ("n_t", "n1i"), ("mean_c", "m2i"), ("sd_c", "sd2i"), ("n_c", "n2i")]
        got = {b: canon(bv.get(b)) for b, _ in pairs}
        if None in got.values():
            return {"state": "NOT_COMPARABLE", "why": "served row is arm means; bound values lack a full mean/SD/n set"}
        same = all(abs(got[b] - float(served[s_])) < 1e-9 for b, s_ in pairs if served.get(s_) is not None)
        return {"state": "MATCH" if same else "DIFFERS", "from": "arm means",
                "served": [served.get(s_) for _, s_ in pairs], "bound": [got[b] for b, _ in pairs]}
    if not bv or se is None:
        return {"state": "NOT_COMPARABLE", "why": "no bound values or no served effect"}
    est = canon(bv.get("estimate"))
    norm = lambda x: {"HAZARD RATIO": "HR", "RISK RATIO": "RR", "RELATIVE RISK": "RR", "ODDS RATIO": "OR",
                      "MEAN DIFFERENCE": "MD"}.get((x or "").upper().strip(), (x or "").upper().strip())
    bscale = norm(bv.get("scale"))
    if est is not None and bscale and sc and bscale != norm(sc):
        est = None   # a number on another scale is not the served number; fall through to recomputable inputs
    if est is not None:
        dp = len(str(bv.get("estimate")).replace("·", ".").split(".")[1]) if "." in str(bv.get("estimate")).replace("·", ".") else 0
        tol = 0.5 * 10 ** -dp + 1e-9
        ok = abs(est - se) <= tol
        lo, hi = canon(bv.get("ci_low")), canon(bv.get("ci_high"))
        ci_ok = (lo is None or served.get("ci_low") is None or abs(lo - served["ci_low"]) <= tol) and \
                (hi is None or served.get("ci_high") is None or abs(hi - served["ci_high"]) <= tol)
        return {"state": "MATCH" if ok and ci_ok else "DIFFERS", "served": [se, served.get("ci_low"), served.get("ci_high")],
                "bound": [est, lo, hi], "bound_scale": bv.get("scale"), "served_scale": sc, "tolerance": tol}
    et, nt, ec, nc = (canon(bv.get(k)) for k in ("events_t", "n_t", "events_c", "n_c"))
    if None not in (et, nt, ec, nc) and nt and nc:
        if sc in ("RR", "RISK RATIO"):
            v = (et / nt) / (ec / nc) if ec else None
        elif sc in ("OR", "ODDS RATIO"):
            v = (et * (nc - ec)) / ((nt - et) * ec) if ec and (nt - et) else None
        elif sc in ("RD",):
            v = et / nt - ec / nc
        else:
            v = None
        if v is None:
            return {"state": "NOT_COMPARABLE", "why": f"counts bound but served scale {sc} not recomputable"}
        return {"state": "MATCH" if abs(v - se) < 5e-4 else "DIFFERS", "served": se, "recomputed": round(v, 6), "from": "counts"}
    mt, mc = canon(bv.get("mean_t")), canon(bv.get("mean_c"))
    if mt is not None and mc is not None:
        v = mt - mc
        return {"state": "MATCH" if abs(v - se) < 5e-3 else "DIFFERS", "served": se, "recomputed": round(v, 6), "from": "means"}
    return {"state": "NOT_COMPARABLE", "why": f"bound values carry neither a {sc} estimate nor recomputable inputs",
            "bound_scale": bv.get("scale"), "served_scale": sc}


def verify(rec, packet, pinned=None):
    errs, flags, spans = [], [], {}
    allowed = {s["ref"] for s in packet["sources"]}
    renders = {}
    for f in FIELDS:
        v = (rec.get("fields") or {}).get(f)
        if v is None:
            continue
        ref, span = v.get("ref"), v.get("span")
        if ref not in allowed:
            errs.append(f"{f}: ref {ref!r} not a source in the packet"); continue
        if not span:
            errs.append(f"{f}: empty span"); continue
        if ref not in renders:
            renders[ref] = textrep.render(ref)
        text = renders[ref]
        offs = [m.start() for m in re.finditer(re.escape(span), text)]
        if not offs:
            errs.append(f"{f}: span not found verbatim in render({ref})"); continue
        sha = file_sha(ref)
        if pinned and pinned.get(f, {}).get("sha256") not in (None, sha):
            errs.append(f"{f}: {ref} sha256 changed since the record was verified")
        if len(offs) > 1:
            flags.append(f"{f}: span occurs {len(offs)} times")
        spans[f] = {"ref": ref, "sha256": sha, "offsets": offs, "len": len(span)}
    ep = rec.get("entry_population_matches_question") or {}
    if ep.get("span"):
        ref = ep.get("ref")
        if ref not in allowed:
            errs.append(f"entry_population: ref {ref!r} not a source in the packet")
        else:
            text = renders.get(ref) or textrep.render(ref)
            offs = [m.start() for m in re.finditer(re.escape(ep["span"]), text)]
            if not offs:
                errs.append("entry_population: span not found verbatim")
            else:
                spans["entry_population"] = {"ref": ref, "sha256": file_sha(ref), "offsets": offs, "len": len(ep["span"])}
    bv = rec.get("bound_values") or {}
    numtext = " ".join((rec["fields"].get(f) or {}).get("span", "") for f in ("estimate", "ci") if rec.get("fields"))
    toks = num_tokens(numtext)
    for k, val in bv.items():
        if k not in NUMERIC or val in (None, ""):
            continue
        t = str(val).replace("·", ".").replace("−", "-").replace("%", "").replace(",", "")
        if t not in toks and t.lstrip("-") not in toks:
            errs.append(f"bound_values.{k}={val!r} not a number printed in the estimate/ci spans")
    core_missing = [f for f in CORE if f not in spans]
    if rec.get("verdict") == "BOUND" and core_missing:
        errs.append(f"verdict BOUND but core fields unbound: {core_missing}")
    return {"errors": errs, "flags": flags, "spans": spans,
            "served_compare": served_compare(served_row(packet), bv) if rec.get("verdict") == "BOUND" else None}


def served_row(packet):
    """The served row read from the served review.json at the packet's json_ref (the packet copy is only a
    convenience for the extractor and may omit fields)."""
    ref = packet.get("json_ref")
    if not ref:
        return packet["served_row"]
    path, _, ptr = ref.partition("#")
    node = json.load(open(os.path.join(ROOT, path), encoding="utf-8"))
    for part in ptr.strip("/").split("/"):
        node = node[int(part)] if isinstance(node, list) else node[part]
    return node


def main(argv):
    raw_dir = os.path.join(ROOT, "evidence", "extractions", "raw")
    keys = argv or sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(raw_dir, "*.json")))
    out, bad = {}, 0
    for k in keys:
        rec = json.load(open(os.path.join(raw_dir, f"{k}.json"), encoding="utf-8"))
        pk = json.load(open(os.path.join(ROOT, "evidence", "packets", f"{k}.json"), encoding="utf-8"))
        r = verify(rec, pk)
        out[k] = {"verdict": rec.get("verdict"), "set_aside_reason": rec.get("set_aside_reason"), **r}
        bad += bool(r["errors"])
        sc = (r["served_compare"] or {}).get("state")
        print(f"{k:8} {rec.get('verdict'):9} errors={len(r['errors'])} served={sc} {'; '.join(r['errors'])[:160]}")
    json.dump(out, open(os.path.join(ROOT, "evidence", "extractions", "verification.json"), "w", encoding="utf-8"), indent=1)
    print(f"verified {len(keys) - bad} of {len(keys)}; failing {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
