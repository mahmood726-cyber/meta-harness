"""Source-bound COVACTA percentage conversion; Dispatch option b, 16 Oct.
Static: endpoint, identity, hashes and rounding policy. Dynamic: all arm values.
"""
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "registry/source_acquisitions/tocilizumab-covid19-mortality/NCT04320615_ctgov_v2.json"
SHA256 = "955e18681bbd647ca069c6e4a44e55724640c7378902ea10b479284b9f6dc9a3"
TITLE = "Mortality Rate at Day 28 (Week 4)"

def unique_count(percentage, n):
    try:
        p = Decimal(percentage)
        if not p.is_finite() or not 0 <= p <= 100 or type(n) is not int or n <= 0:
            raise ValueError("invalid percentage/denominator")
        precision = Decimal(1).scaleb(p.as_tuple().exponent)
        candidates = [k for k in range(n+1) if (Decimal(100)*k/n).quantize(precision, rounding=ROUND_HALF_UP) == p]
        rounded = int((p*n/100).quantize(Decimal(1), rounding=ROUND_HALF_UP))
        if candidates != [rounded]:
            raise ValueError("percentage does not identify a unique integer count")
        return rounded
    except InvalidOperation as exc:
        raise ValueError("invalid percentage") from exc

def binding():
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise ValueError("COVACTA source digest differs")
    doc = json.loads(raw)
    if doc["protocolSection"]["identificationModule"]["nctId"] != "NCT04320615":
        raise ValueError("wrong trial")
    matches = [m for m in doc["resultsSection"]["outcomeMeasuresModule"]["outcomeMeasures"] if m.get("title") == TITLE]
    if len(matches) != 1:
        raise ValueError("outcome not unique")
    m = matches[0]
    if (m.get("timeFrame"), m.get("reportingStatus"), m.get("paramType"), m.get("unitOfMeasure")) != ("Day 28", "POSTED", "NUMBER", "Percentage of Participants") or not m.get("populationDescription", "").startswith("mITT population:"):
        raise ValueError("wrong outcome semantics")
    if len(m["groups"]) != 2 or len(m["denoms"]) != 1 or m["denoms"][0]["units"] != "Participants" or len(m["classes"]) != 1 or len(m["classes"][0]["categories"]) != 1:
        raise ValueError("ambiguous arm table")
    ms = m["classes"][0]["categories"][0]["measurements"]
    ns = m["denoms"][0]["counts"]
    inputs = []
    for g in m["groups"]:
        vs = [x["value"] for x in ms if x["groupId"] == g["id"]]
        ds = [x["value"] for x in ns if x["groupId"] == g["id"]]
        if len(vs) != 1 or len(ds) != 1:
            raise ValueError("ambiguous arm values")
        n = int(ds[0])
        count = unique_count(vs[0], n)
        inputs.append(dict(group_id=g["id"], label=g["title"], percentage=vs[0], n=n, count=count, unique_candidates=[count]))
    active = [a for a in inputs if a["label"].startswith("Tocilizumab")]
    control = [a for a in inputs if a["label"].startswith("Placebo")]
    if len(active) != 1 or len(control) != 1:
        raise ValueError("ambiguous treatment assignment")
    a,b = active[0],control[0]
    output = dict(ai=a["count"], n1i=a["n"], ci=b["count"], n2i=b["n"])
    ref = SOURCE.relative_to(ROOT).as_posix() + "#resultsSection/outcomeMeasuresModule/" + TITLE
    span = json.dumps(m, ensure_ascii=False, sort_keys=True, indent=2)
    conversion = dict(kind="percentage_to_count", reference="CT.gov posted results; Dispatch option b, 16 Oct 2026", reference_url="https://clinicaltrials.gov/study/NCT04320615?tab=results", source_ref=ref, source_sha256=SHA256, inputs=inputs, output=output, population=m["populationDescription"], source_span=span,
        formula="Round percentage x N / 100 to nearest integer (half up); enumerate every integer 0..N and refuse unless this is the unique integer whose percentage rounds half up to the printed precision.",
        corroboration=dict(role="Corroboration only; not the bound source", document="EMA/733881/2021", file="EMA_roactemra_II-0101_AR.pdf", page=105, sha256="0e9c68ea8df00a35f79ccd7159caab9ab123978a94fb0e69bca96d5d7e4487db"))
    return dict(served=output, source_ref=ref, source_sha256=SHA256, span=span, licence_class="PUBLIC_DOMAIN_REGISTRY", declared_conversion=conversion)
