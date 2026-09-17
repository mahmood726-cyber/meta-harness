"""Eligibility/search scope identity checks.

The screen can audit records only inside the retrieval universe it was given. If
the protocol states open P/I/C/design eligibility but retrieval is a pre-identified
PMID/title set, the page may report the pre-identified set; it may not imply the
open eligibility universe was tested.
"""
from __future__ import annotations

from .topic_registry import topic_id

import json
import os
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

SEEDED_RETRIEVAL_CLASSES = {"KNOWN_ITEM_RETRIEVAL", "TITLE_SEEDED_RETRIEVAL"}
HAND_WRITTEN_RETRIEVAL_CLASS = "HAND_WRITTEN_KEYWORD_SEARCH"
CONCEPT_RETRIEVAL_CLASS = "CONCEPT_SEARCH"
SCOPE_MISMATCH = "SCOPE_MISMATCH"
HAND_WRITTEN_SCOPE = "HAND_WRITTEN_KEYWORD_SCOPE"
OK = "OK"
UNKNOWN_SCOPE = "UNKNOWN_SCOPE"
QUALIFIED_SCOPE_PHRASE = "eligibility over the open scope was NOT tested"
NOAC_REQUIRED_RENDER = (
    "rule stated; both answers were known; standard-dose result AND all-dose result reported"
)

REACH_MISSES = {
    (topic_id('vte_anticoagulation')): [
        {
            "row_type": "REACH_MISS",
            "trial": "Botticelli-DVT",
            "pmid": "18541000",
            "nct": None,
            "reason": "audit-named eligible acute DVT DOAC-vs-VKA dose-ranging trial absent from retrieval ledger",
        },
        {
            "row_type": "REACH_MISS",
            "trial": "ODIXa-DVT",
            "pmid": "17576867",
            "nct": None,
            "reason": "audit-named eligible acute DVT DOAC-vs-VKA dose-ranging trial absent from retrieval ledger",
        },
        {
            "row_type": "REACH_MISS",
            "trial": "EINSTEIN-DVT dose-ranging",
            "pmid": "18621928",
            "nct": None,
            "reason": "audit-named eligible acute DVT DOAC-vs-VKA dose-ranging trial absent from retrieval ledger",
        },
    ],
    (topic_id('af_anticoagulation')): [
        {
            "row_type": "REACH_MISS",
            "trial": "J-ROCKET AF",
            "pmid": "22664783",
            "nct": "NCT00494871",
            "reason": "audit-named eligible Japanese AF DOAC-vs-warfarin trial absent from retrieval ledger",
        },
        {
            "row_type": "REACH_MISS",
            "trial": "ARISTOTLE-J",
            "pmid": "21670542",
            "nct": "NCT00787150",
            "reason": "audit-named eligible Japanese AF DOAC-vs-warfarin trial absent from retrieval ledger",
        },
        {
            "row_type": "REACH_MISS",
            "trial": "PETRO",
            "pmid": "17950801",
            "nct": None,
            "reason": "audit-named dabigatran AF dose-ranging trial absent from retrieval ledger",
        },
    ],
    (topic_id('metformin_ovulation')): [
        {
            "row_type": "REACH_MISS",
            "trial": "Nestler 1998",
            "pmid": "9637806",
            "nct": None,
            "reason": "audit-named eligible PCOS metformin trial absent from retrieval ledger",
        },
    ],
    (topic_id('postoperative_af')): [
        {
            "row_type": "REACH_MISS",
            "trial": "Sarzaeem 2014",
            "pmid": None,
            "nct": None,
            "id_status": "NAME_ONLY",
            "reason": "audit-named eligible colchicine POAF trial; identifier unresolved in committed audit",
        },
        {
            "row_type": "REACH_MISS",
            "trial": "Zarpelon",
            "pmid": "27223641",
            "nct": None,
            "reason": "audit-named eligible colchicine POAF trial absent from retrieval ledger",
        },
    ],
}


def _root(root: str | os.PathLike[str] | None = None) -> Path:
    return Path(root) if root is not None else ROOT


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def _load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return _read_json(path)


def _phase_terms(config: dict[str, Any] | None, protocol_text: str) -> list[str]:
    hay = " ".join(
        str(x)
        for x in [
            protocol_text,
            *((config or {}).get("include") or {}).get("population_any", []),
            *((config or {}).get("include") or {}).get("population_none", []),
        ]
    ).lower()
    terms = []
    for term in (
        "acute",
        "extended treatment",
        "secondary prevention",
        "primary prevention",
        "dose-ranging",
        "dose ranging",
        "phase ii",
        "phase iii",
        "phase 2",
        "phase 3",
    ):
        if term in hay:
            terms.append(term)
    return sorted(set(terms))


def derive_eligibility_scope(
    *,
    config: dict[str, Any] | None = None,
    protocol_text: str = "",
    review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    include = (config or {}).get("include") or {}
    protocol = (review or {}).get("protocol") or {}
    eligibility_text = protocol.get("eligibility") or ""
    has_pic = any(include.get(k) for k in ("population_any", "intervention_any", "comparator_any"))
    return {
        "type": "OPEN_PIC_DESIGN" if has_pic or "P/I/C/design" in eligibility_text or protocol_text else "UNKNOWN",
        "basis": "topics/<slug>.json include + protocols/<slug>.md",
        "population_terms": include.get("population_any") or [],
        "population_exclusions": include.get("population_none") or [],
        "intervention_terms": include.get("intervention_any") or [],
        "comparator_terms": include.get("comparator_any") or [],
        "design_terms": ["randomised controlled trial"] + (
            ["double blind"] if include.get("design_double_blind") else []
        ),
        "phase_terms": _phase_terms(config, protocol_text),
        "outcome_reporting_is_eligibility": False,
        "description": eligibility_text,
    }


def _queries_from_sources(sources: list[dict[str, Any]]) -> list[str]:
    return [str(src.get("query")) for src in sources if src.get("query") not in (None, "")]


def _queries_from_search(search: dict[str, Any] | None) -> list[str]:
    queries = []
    for src in (search or {}).get("sources") or []:
        for query in src.get("queries") or []:
            if query not in (None, ""):
                queries.append(str(query))
    return queries


def _fallback_retrieval_class(ledger: dict[str, Any] | None, search: dict[str, Any] | None) -> str | None:
    sources = (ledger or {}).get("sources") or []
    if any(
        src.get("kind") in {"PUBMED_CONCEPT_QUERY", "EUROPEPMC_CONCEPT_QUERY", "CTGOV_CONDITION_INTERVENTION"}
        and src.get("state") == "RAN_OK"
        for src in sources
    ):
        return CONCEPT_RETRIEVAL_CLASS
    queries = _queries_from_sources(sources) or _queries_from_search(search)
    kinds = {str(src.get("kind")) for src in sources}
    if queries and all("[uid]" in q.lower() for q in queries):
        return "KNOWN_ITEM_RETRIEVAL"
    if any(k == "PUBMED_LEGACY_QUERY" for k in kinds):
        return HAND_WRITTEN_RETRIEVAL_CLASS
    if queries:
        return "TITLE_SEEDED_RETRIEVAL" if any(("[" in q and "title" in q.lower()) for q in queries) else HAND_WRITTEN_RETRIEVAL_CLASS
    return None


def derive_search_scope(
    *,
    search: dict[str, Any] | None = None,
    ledger: dict[str, Any] | None = None,
    retrieval_class: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rc = retrieval_class or ((search or {}).get("retrieval_class") or {})
    rc_class = rc.get("class") or _fallback_retrieval_class(ledger, search) or "UNKNOWN"
    sources = (ledger or {}).get("sources") or []
    queries = _queries_from_sources(sources) or _queries_from_search(search)
    source_kinds = sorted({str(src.get("kind")) for src in sources if src.get("kind")})
    discovery_sources = [src for src in sources if src.get("discovery_capable")]
    if rc_class in SEEDED_RETRIEVAL_CLASSES:
        scope_type = "PRE_IDENTIFIED_SET"
        description = "retrieval can test only named PMIDs/titles/trial identifiers already supplied"
    elif rc_class == HAND_WRITTEN_RETRIEVAL_CLASS:
        scope_type = "UNREGISTERED_HAND_WRITTEN_KEYWORD"
        description = "not a pre-identified PMID set, but not a registered concept search; discovery reach is unmeasured"
    elif rc_class == CONCEPT_RETRIEVAL_CLASS:
        scope_type = "REGISTERED_CONCEPT_SEARCH"
        description = "registered P/I/C concept retrieval with discovery-capable sources"
    else:
        scope_type = "UNKNOWN"
        description = "search scope could not be typed from the committed object"
    return {
        "type": scope_type,
        "retrieval_class": rc_class,
        "retrieval_label": rc.get("label"),
        "query_count": len(queries),
        "queries": queries,
        "source_kinds": source_kinds,
        "discovery_capable_source_count": len(discovery_sources),
        "description": description,
    }


def assess(
    *,
    config: dict[str, Any] | None = None,
    protocol_text: str = "",
    search: dict[str, Any] | None = None,
    ledger: dict[str, Any] | None = None,
    review: dict[str, Any] | None = None,
    slug: str | None = None,
) -> dict[str, Any]:
    eligibility_scope = derive_eligibility_scope(config=config, protocol_text=protocol_text, review=review)
    search_scope = derive_search_scope(search=search, ledger=ledger)
    rc_class = search_scope.get("retrieval_class")
    if eligibility_scope.get("type") == "OPEN_PIC_DESIGN" and rc_class in SEEDED_RETRIEVAL_CLASSES:
        verdict = SCOPE_MISMATCH
        reason = (
            "open P/I/C/design eligibility was evaluated only inside a pre-identified retrieval set; "
            "the open eligibility universe was not tested"
        )
    elif eligibility_scope.get("type") == "OPEN_PIC_DESIGN" and rc_class == HAND_WRITTEN_RETRIEVAL_CLASS:
        verdict = HAND_WRITTEN_SCOPE
        reason = (
            "hand-written keyword retrieval is not a pre-identified PMID/title set, but it was not a "
            "registered concept search; discovery reach remains unmeasured"
        )
    elif eligibility_scope.get("type") == "OPEN_PIC_DESIGN" and rc_class == CONCEPT_RETRIEVAL_CLASS:
        verdict = OK
        reason = "open eligibility and registered concept search scope are the same object"
    else:
        verdict = UNKNOWN_SCOPE
        reason = "scope identity could not be evaluated from committed inputs"
    out = {
        "slug": slug or (review or {}).get("slug"),
        "eligibility_scope": eligibility_scope,
        "search_scope": search_scope,
        "verdict": verdict,
        "reason": reason,
    }
    if verdict == SCOPE_MISMATCH:
        out["render_requirement"] = qualification_text(out, "N")
    return out


def _load_inputs(slug: str, root: str | os.PathLike[str] | None = None) -> tuple[dict[str, Any] | None, str, dict[str, Any] | None, dict[str, Any] | None]:
    base = _root(root)
    config = _load_json_if_exists(base / "topics" / f"{slug}.json")
    protocol_path = base / "protocols" / f"{slug}.md"
    protocol_text = _read_text(protocol_path) if protocol_path.exists() else ""
    ledger = _load_json_if_exists(base / "cache" / slug / "retrieval_ledger.json")
    review = _load_json_if_exists(base / "docs" / "reviews" / slug / "review.json")
    return config, protocol_text, ledger, review


def assess_review(
    review: dict[str, Any],
    *,
    root: str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    embedded = review.get("scope_identity")
    if isinstance(embedded, dict) and embedded.get("verdict"):
        return embedded
    slug = review.get("slug")
    config = None
    protocol_text = ((review.get("protocol") or {}).get("text") or "")
    ledger = None
    if slug:
        config, loaded_protocol, ledger, _loaded_review = _load_inputs(str(slug), root)
        protocol_text = protocol_text or loaded_protocol
    return assess(
        config=config,
        protocol_text=protocol_text,
        search=review.get("search") or {},
        ledger=ledger,
        review=review,
        slug=slug,
    )


def requires_qualification(scope_identity: dict[str, Any] | None) -> bool:
    return bool(scope_identity and scope_identity.get("verdict") == SCOPE_MISMATCH)


def qualification_text(scope_identity: dict[str, Any] | None, n: int | str | None) -> str:
    cls = (((scope_identity or {}).get("search_scope") or {}).get("retrieval_class")) or "UNKNOWN"
    return (
        f"{n} of the pre-identified set met eligibility; "
        f"{QUALIFIED_SCOPE_PHRASE} (search class {cls})"
    )


def rendered_block(scope_identity: dict[str, Any] | None) -> str:
    if not scope_identity:
        return ""
    verdict = scope_identity.get("verdict")
    rc = ((scope_identity.get("search_scope") or {}).get("retrieval_class")) or "UNKNOWN"
    if verdict == SCOPE_MISMATCH:
        return (
            "<div class='scope-identity'><strong>Scope identity mismatch.</strong> "
            "Eligibility is open P/I/C/design, but retrieval is a pre-identified set. "
            f"{QUALIFIED_SCOPE_PHRASE} (search class {rc}).</div>"
        )
    if verdict == HAND_WRITTEN_SCOPE:
        return (
            "<div class='scope-identity'><strong>Search scope not registered.</strong> "
            "The retrieval is hand-written keyword search: not a pre-identified PMID/title set, "
            f"but not a registered concept search; discovery reach is unmeasured (search class {rc}).</div>"
        )
    if verdict == OK:
        return (
            "<p class='muted'><strong>Scope identity:</strong> open eligibility and concept-search "
            f"scope match. Verdict: <code>{OK}</code>.</p>"
        )
    return ""


def check_scope_identity(
    review: dict[str, Any],
    html: str | None = None,
    *,
    root: str | os.PathLike[str] | None = None,
) -> list[dict[str, Any]]:
    scope = assess_review(review, root=root)
    if scope.get("verdict") != SCOPE_MISMATCH:
        return []
    if html and QUALIFIED_SCOPE_PHRASE in html and "pre-identified set met eligibility" in html:
        return []
    return [
        {
            "code": SCOPE_MISMATCH,
            "slug": review.get("slug"),
            "detail": scope.get("reason"),
            "retrieval_class": (scope.get("search_scope") or {}).get("retrieval_class"),
            "required_text": qualification_text(scope, "N"),
        }
    ]


def gate_reasons(
    review: dict[str, Any],
    html: str | None = None,
    *,
    root: str | os.PathLike[str] | None = None,
) -> list[str]:
    return [
        "L1(scope_identity): "
        + v["detail"]
        + " -- render the pre-identified-set qualification before claiming screening count = k"
        for v in check_scope_identity(review, html, root=root)
    ]


def _review_slugs(root: Path) -> list[str]:
    review_root = root / "docs" / "reviews"
    return sorted(p.name for p in review_root.iterdir() if (p / "review.json").exists())


def _reach_misses(slug: str) -> list[dict[str, Any]]:
    rows = []
    for row in REACH_MISSES.get(slug, []):
        rows.append(
            {
                **row,
                "phase": "Phase 2B search repair",
                "fetched": False,
                "pooled": False,
            }
        )
    return rows


def sweep(root: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    base = _root(root)
    pages = []
    for slug in _review_slugs(base):
        config, protocol_text, ledger, review = _load_inputs(slug, base)
        assert review is not None
        scope = assess(
            config=config,
            protocol_text=protocol_text,
            search=review.get("search") or {},
            ledger=ledger,
            review=review,
            slug=slug,
        )
        pages.append(
            {
                "slug": slug,
                "eligibility_scope": scope["eligibility_scope"],
                "search_scope": scope["search_scope"],
                "verdict": scope["verdict"],
                "reason": scope["reason"],
                "reach_miss": _reach_misses(slug),
            }
        )
    n_mismatch = sum(1 for row in pages if row["verdict"] == SCOPE_MISMATCH)
    return {
        "generated_from": "committed topics/protocols/cache retrieval ledgers/review objects",
        "n_pages": len(pages),
        "n_scope_mismatch": n_mismatch,
        "summary": f"{n_mismatch} pages SCOPE_MISMATCH of {len(pages)}",
        "pages": pages,
    }


_AMENDMENT_RE = re.compile(
    r"^## Amendment (?P<date>\d{4}-\d{2}-\d{2})(?: \((?P<label>[^)]*)\))?(?P<body>.*?)(?=^## |\Z)",
    re.MULTILINE | re.DOTALL,
)


def _date_prefix(value: Any) -> str | None:
    if not value:
        return None
    m = re.search(r"\d{4}-\d{2}-\d{2}", str(value))
    return m.group(0) if m else None


def _after_cache(amendment_date: str, fetched_utc: str | None) -> bool:
    if not fetched_utc:
        return False
    return date.fromisoformat(amendment_date) > date.fromisoformat(fetched_utc)


def _git_log_for_protocol(root: Path, slug: str) -> list[str]:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(root), "log", "--date=short", "--pretty=format:%h %ad %s", "--", f"protocols/{slug}.md"],
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except Exception:
        return []
    return [line for line in out.splitlines() if line.strip()]


def _short_changed(slug: str, label: str | None, body: str) -> str:
    if slug == (topic_id('af_anticoagulation')):
        return "dose/analysis selection rule changed the estimand to standard-dose DOAC-vs-warfarin"
    if slug == (topic_id('spironolactone_heart_failure')):
        return "identifier scope widened from single-agent spironolactone to steroidal MRA class"
    clean = re.sub(r"\s+", " ", body).strip()
    return label or clean[:220]


def _noac_lower_dose_status(records: dict[str, Any]) -> dict[str, Any]:
    rows = {str(r.get("id")): r for r in records.get("records") or []}
    rely = rows.get("19717844") or {}
    engage = rows.get("24251359") or {}
    rely_text = " ".join([str(rely.get("title") or ""), str(rely.get("abstract") or "")])
    engage_text = " ".join([str(engage.get("title") or ""), str(engage.get("abstract") or "")])
    rely_found = bool(re.search(r"110 mg.*?relative risk.*?0\.91.*?0\.74.*?1\.11", rely_text, re.I | re.S))
    edox_low_found = bool(re.search(r"low-dose edoxaban.*?hazard ratio,\s*1\.13.*?0\.96.*?1\.34", engage_text, re.I | re.S))
    edox_30_label_found = bool(re.search(r"\b30\s*mg\b", engage_text, re.I))
    available = []
    if rely_found:
        available.append({"trial": "RE-LY", "arm": "dabigatran 110 mg", "effect": 0.91, "ci_low": 0.74, "ci_high": 1.11, "scale": "RR"})
    if edox_low_found:
        available.append({"trial": "ENGAGE AF-TIMI 48", "arm": "low-dose edoxaban", "effect": 1.13, "ci_low": 0.96, "ci_high": 1.34, "scale": "HR"})
    if rely_found and edox_30_label_found:
        status = "READY_TO_COMPUTE"
        reason = "RE-LY 110 mg and edoxaban 30 mg effects are both explicitly present in committed sources."
    else:
        status = "NOT_COMPUTED_SOURCE_INCOMPLETE"
        reason = (
            "RE-LY 110 mg effect found; ENGAGE low-dose edoxaban effect found, but the committed source "
            "does not explicitly identify that lower-dose arm as edoxaban 30 mg."
        )
    return {
        "status": status,
        "reason": reason,
        "available_lower_dose_rows": available,
        "edoxaban_30_mg_explicit_in_committed_source": edox_30_label_found,
    }


def _standard_dose_result(review: dict[str, Any] | None) -> dict[str, Any] | None:
    if not review:
        return None
    primary = next((o for o in review.get("outcomes") or [] if o.get("primary")), None)
    res = (primary or {}).get("result") or {}
    return {
        "k": res.get("k"),
        "estimate": res.get("estimate"),
        "scale": res.get("scale"),
        "ci_low": res.get("ci_low"),
        "ci_high": res.get("ci_high"),
        "tau2": res.get("tau2"),
    }


def posthoc_amendment_sweep(root: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    base = _root(root)
    rows = []
    for protocol_path in sorted((base / "protocols").glob("*.md")):
        slug = protocol_path.stem
        protocol_text = _read_text(protocol_path)
        cache = _load_json_if_exists(base / "cache" / slug / "records.json") or {}
        fetched = _date_prefix(cache.get("fetched_utc"))
        review = _load_json_if_exists(base / "docs" / "reviews" / slug / "review.json")
        for match in _AMENDMENT_RE.finditer(protocol_text):
            amendment_date = match.group("date")
            if not _after_cache(amendment_date, fetched):
                continue
            label = match.group("label")
            body = match.group("body")
            row = {
                "type": "POST_HOC_AMENDMENT",
                "slug": slug,
                "amendment_date": amendment_date,
                "cache_fetched_utc": fetched,
                "heading": f"Amendment {amendment_date}" + (f" ({label})" if label else ""),
                "changed": _short_changed(slug, label, body),
                "git_log_protocol": _git_log_for_protocol(base, slug),
            }
            if slug == (topic_id('af_anticoagulation')):
                row["required_render"] = NOAC_REQUIRED_RENDER
                row["standard_dose_result"] = _standard_dose_result(review)
                row["all_dose_alternative"] = _noac_lower_dose_status(cache)
            rows.append(row)
    return {
        "generated_from": "dated protocol amendment sections + cache/<slug>/records.json fetched_utc + git log protocols/*.md",
        "n_post_hoc_amendments": len(rows),
        "amendments": rows,
    }


def write_sweeps(root: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    base = _root(root)
    docs = base / "docs"
    docs.mkdir(exist_ok=True)
    scope = sweep(base)
    posthoc = posthoc_amendment_sweep(base)
    (docs / "scope_identity_sweep.json").write_text(
        json.dumps(scope, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (docs / "posthoc_amendment_sweep.json").write_text(
        json.dumps(posthoc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return {"scope_identity_sweep": scope, "posthoc_amendment_sweep": posthoc}


def main() -> int:
    written = write_sweeps(ROOT)
    print(written["scope_identity_sweep"]["summary"])
    print(f"{written['posthoc_amendment_sweep']['n_post_hoc_amendments']} post-hoc amendments")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
