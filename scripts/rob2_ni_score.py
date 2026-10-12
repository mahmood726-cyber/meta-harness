"""Score the PRE-REGISTERED NI policy on TEST (outputs/robgrade/NI_POLICY.md section 4): agreement with the published
per-trial domain judgements as n of N -- all pairs, excluding NI-driven pairs, and the NI-driven pairs alone.

The pairs are REBUILT here from the committed per-trial RoB 2 objects (outputs/robgrade/rob2/<slug>.json) and the
recorded comparator transcriptions (outputs/robgrade/reference/<slug>.json) through scripts/rob2_calibrate.pairs_for;
no calibration file is trusted (codex review, 12 Oct). Refuses unless
  (a) PREREG is an ancestor of HEAD and every policy file is byte-identical to it;
  (b) each pair's judgement AND NI label are recomputed from its stored answers and match (the label never changed a
      judgement, and was not edited after the fact);
  (c) every pair is a TEST trial (outputs/robgrade/split.json), and no (topic, trial, domain) appears twice.
The comparators' tools are named: a RoB 1 table mapped to RoB 2 domains is an approximation (Handbook 8.8). Excluded
and unmatched records are counted, never dropped.

    python scripts/rob2_ni_score.py PREREG_SHA   -> outputs/robgrade/NI_SCORE.md + ni_score.json
"""
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from robgrade import ni_policy as nip  # noqa: E402
from robgrade import rob2_formal as rf  # noqa: E402
import rob2_calibrate as cal  # noqa: E402

POLICY_FILES = ["outputs/robgrade/NI_POLICY.md", "robgrade/rob2_formal.py", "robgrade/ni_policy.py",
                "scripts/rob2_calibrate.py", "scripts/rob2_ni_score.py", "tests/test_rob2_ni_policy.py",
                "tests/test_rob2_algorithm_guidance.py"]
TOPICS = ["balanced-crystalloids-vs-saline-mortality", "iv-iron-hfref-hosp", "probiotics-aad-prevention",
          "ticagrelor-vs-clopidogrel-acs"]
V3 = os.path.join(ROOT, "outputs", "robgrade", "calibration_v3.json")
# the frozen INPUTS: byte-identical to the pre-registration commit too (codex round 2)
INPUT_FILES = ["outputs/robgrade/split.json", "outputs/robgrade/calibration_v3.json"] +               [f"outputs/robgrade/reference/{t}.json" for t in TOPICS]
DISCLOSURE = ("A comparator row is matched to our trial by PMID only: result identity (the same outcome, time point and "
              "numerical result) is NOT verified, so these counts do not establish agreement on the same result "
              "(RoB 2 rates a result; Handbook 8.2.1).")


def _git(*a):
    return subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True)


def check_prereg(sha):
    """The anchor is not the caller's choice: it must be the commit that first ADDED the policy file (codex round 4)."""
    full = _git("rev-parse", sha).stdout.strip()
    added = [x for x in _git("log", "--diff-filter=A", "--format=%H", "--", POLICY_FILES[0]).stdout.split() if x]
    if not added or full != added[-1]:
        raise SystemExit(f"REFUSED: {sha} is not the commit that added {POLICY_FILES[0]} "
                         f"({added[-1] if added else 'never added'})")
    if _git("merge-base", "--is-ancestor", sha, "HEAD").returncode != 0:
        raise SystemExit(f"REFUSED: {sha} is not an ancestor of HEAD")
    changed = [f for f in POLICY_FILES + INPUT_FILES if _git("diff", "--quiet", sha, "--", f).returncode != 0]
    if changed:
        raise SystemExit(f"REFUSED: policy files differ from the pre-registration {sha}: {changed}")
    return _git("rev-parse", sha).stdout.strip()


def frozen_object(sha, slug):
    """The per-trial RoB 2 objects of a topic as committed AT the pre-registration (v3 answers)."""
    out = _git("show", f"{sha}:outputs/robgrade/rob2/{slug}.json")
    if out.returncode != 0:
        raise SystemExit(f"REFUSED: no committed objects for {slug} at {sha}")
    return json.loads(out.stdout)


def _answer_view(dom, ans):
    return {q: (a.get("answer"), a.get("span")) for q, a in rf.normalize_answers(dom, ans).items()}


def check_answers_frozen(sha, slug, doc):
    """Every scored answer (value and span) equals the pre-registration's, after the same vocabulary normalisation:
    v3.1 may re-judge the answers, never change them."""
    frozen = frozen_object(sha, slug)["trials"]
    if set(frozen) != set(doc["trials"]):           # the cohort is frozen too: a dropped trial is a change (codex r3)
        raise SystemExit(f"REFUSED: {slug}: trials differ from the pre-registration {sha}: "
                         f"{sorted(set(frozen) ^ set(doc['trials']))}")
    for pmid, o in doc["trials"].items():
        for d, dom in o["domains"].items():
            f = ((frozen.get(pmid) or {}).get("domains") or {}).get(d)
            if f is None or _answer_view(d, dom["answers"]) != _answer_view(d, f["answers"]):
                raise SystemExit(f"REFUSED: {slug} {pmid} {d}: answers differ from the pre-registration {sha}")
            if (dom.get("judgement") == rf.INSUFFICIENT) != (f.get("judgement") == rf.INSUFFICIENT):
                raise SystemExit(f"REFUSED: {slug} {pmid} {d}: eligibility (INSUFFICIENT_OPEN_SOURCE) changed since {sha}")
            if dom.get("judgement") != rf.INSUFFICIENT and dom.get("judgement") != rf.ni_label(d, dom["answers"])["judgement"]:
                # a malformed judgement would otherwise fall out as an exclusion before any recomputation (codex r4)
                raise SystemExit(f"REFUSED: {slug} {pmid} {d}: stored judgement {dom.get('judgement')!r} != recomputed")


def v3_compare(now, base):
    """v3 -> v3.1 on IDENTICAL pairs: the same (topic, trial, domain) and comparator judgement in both (codex round 2)."""
    b = {(p["slug"], p["pmid"], p["domain"]): p for p in base}
    same = [(p, b[k]) for p in now for k in [(p["slug"], p["pmid"], p["domain"])] if k in b and b[k]["theirs"] == p["theirs"]]
    tally = lambda xs: {"agree": sum(x["ours"] == x["theirs"] for x in xs), "N": len(xs)}
    return {"v3": tally([o for _, o in same]), "v31": tally([n for n, _ in same]),
            "moved": [[n["slug"], n["pmid"], n["domain"], o["ours"], n["ours"], n["theirs"]] for n, o in same
                      if n["ours"] != o["ours"]],
            "not_in_baseline": len(now) - len(same)}


def rebuild(slugs, test):
    """Pairs from the objects + references, each judgement and label recomputed from its stored answers."""
    pairs, excluded, unmatched, tools, seen = [], [], [], {}, set()
    for s in slugs:
        p, e, u, t = cal.pairs_for(s)
        objs = json.load(open(os.path.join(cal.OURS, f"{s}.json"), encoding="utf-8"))["trials"]
        for x in p:
            dom = objs[x["pmid"]]["domains"][x["domain"]]
            lab = rf.ni_label(x["domain"], dom["answers"])
            if lab["judgement"] != x["ours"] or lab["ni_driven"] != x["ni_driven"]:
                raise SystemExit(f"REFUSED: {s} {x['pmid']} {x['domain']}: stored judgement/label "
                                 f"({x['ours']}, {x['ni_driven']}) != recomputed ({lab['judgement']}, {lab['ni_driven']})")
            if x["pmid"] not in test:
                raise SystemExit(f"REFUSED: {s} {x['pmid']} is not a TEST trial")
        for x in p:                                        # across topics too: a slug given twice is a duplicate
            k = (x["slug"], x["pmid"], x["domain"])
            if k in seen:
                raise SystemExit(f"REFUSED: duplicate (topic, trial, domain) pair {k}")
            seen.add(k)
        pairs += p
        excluded += e
        unmatched += [dict(x, slug=s) for x in u]
        tools[s] = t
    return pairs, excluded, unmatched, tools


def main(argv):
    if len(argv) != 1:                    # no topic subset: a subset is not the registered analysis (codex round 4)
        raise SystemExit("REFUSED: the scorer takes the pre-registration SHA only; all four registered comparators are scored")
    sha = check_prereg(argv[0])
    slugs = TOPICS
    test = set(json.load(open(os.path.join(ROOT, "outputs", "robgrade", "split.json"), encoding="utf-8"))["test"])
    for s in slugs:
        check_answers_frozen(sha, s, json.load(open(os.path.join(cal.OURS, f"{s}.json"), encoding="utf-8")))
    pairs, excluded, unmatched, tools = rebuild(slugs, test)
    t = nip.two_way(pairs)
    # the algorithm corrections found by the review (v3 -> v3.1) are a separate change: shown, not mixed in
    vc = v3_compare(pairs, json.load(open(V3, encoding="utf-8"))["pairs"])
    res = {"preregistration_commit": sha, "topics": slugs, "tools": tools, "two_way": t,
           "excluded": len(excluded), "unmatched_trials": len(unmatched), "v3_to_v31": vc,
           "result_identity": DISCLOSURE}
    with open(os.path.join(ROOT, "outputs", "robgrade", "ni_score.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1)
    f = lambda c: f"{c['agree']} / {c['N']}"
    lines = ["# NI policy on TEST: agreement with the published per-trial risk-of-bias judgements, n of N", "",
             f"Pre-registered policy: commit {sha} (outputs/robgrade/NI_POLICY.md). Engine v3.1 = v3 with the three "
             "algorithm corrections the review found against the RoB 2 guidance tables (D2 2.4/2.7 NI, D4 4.1 NI).", "",
             "Comparators and their tools (a RoB 1 table mapped to RoB 2 domains is an approximation, Handbook 8.8): " +
             "; ".join(f"{s}: {tools[s] or '?'}" for s in slugs) + ".",
             f"Coverage: {len(excluded)} trial-domain records excluded (ours INSUFFICIENT_OPEN_SOURCE, or the reference "
             f"cell unresolved), {len(unmatched)} trials not bound to exactly one reference row. Not counted in any N below.",
             "", DISCLOSURE,
             "", "Excluding NI-driven pairs is a STRATUM, not an improvement: it is always shown with the full count and "
             "the NI-driven pairs themselves. The policy changes no judgement (each pair's judgement and label are "
             "recomputed from its stored answers).", "",
             "| domain | all pairs | excluding NI-driven | NI-driven only |", "|---|---|---|---|"]
    for d in nip.DOMS + ("all",):
        lines.append(f"| {d} | {f(t['all'][d])} | {f(t['excluding_ni_driven'][d])} | {f(t['ni_driven_only'][d])} |")
    lines += ["", f"Algorithm corrections v3 -> v3.1, on the identical {vc['v3']['N']} pairs: {len(vc['moved'])} judgements "
              f"moved; agreement {f(vc['v3'])} under v3, {f(vc['v31'])} under v3.1 ({vc['not_in_baseline']} scored pairs "
              "have no identical v3 pair)."]
    lines += [f"- {a} {b} {c}: {o} -> {n} (comparator {th})" for a, b, c, o, n, th in vc["moved"]]
    with open(os.path.join(ROOT, "outputs", "robgrade", "NI_SCORE.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main(sys.argv[1:])
