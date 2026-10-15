"""REGULATORY source route (scripts/g1_regulatory_source.py + g1_trial_acquire.regulatory_gate + the licence guard):
an FDA review is a PRIMARY-grade source for a trial it NAMES, admitted only against the WHOLE held document; the licence
follows from the url's HOST and the held record (FDA open; EMA shown with its acknowledgement; NICE only if
its own text states OGL/CC); a prompt cannot declare itself open."""
import base64
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_regulatory_source as rs  # noqa: E402
import g1_trial_acquire as ga  # noqa: E402
from reproducible_ai import record_licence as rl  # noqa: E402

FDA = "https://www.accessdata.fda.gov/drugsatfda_docs/nda/2099/000000Orig1s000MedR.pdf"
EMA = "https://www.ema.europa.eu/en/documents/assessment-report/x-epar-public-assessment-report_en.pdf"
CFG = {"primary_outcome": {"name": "All-cause mortality", "estimand": "RR", "population": "intention-to-treat",
                           "keywords": ["mortality at day 28"]}}
FILL = "Pharmacokinetic and other discussion unrelated to outcomes. " * 400
DOC = ("8.1 Study WA42380 (COVACTA). " + FILL[:3000] + " In Study WA42380, mortality at day 28 was 58/294 in the "
       "tocilizumab arm and 28/144 in the placebo arm. " + FILL + " 8.2 Study ML42528 (EMPACTA). " + FILL[:3000] +
       " In Study ML42528, mortality at day 28 was 26/249 in the tocilizumab arm and 11/128 in the placebo arm.")
NAMES = ["COVACTA", "NCT04320615", "WA42380"]


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Discovery tests must use fixtures, never live source records."""
    import socket

    def blocked(*a, **k):
        pytest.fail("network access in regulatory source tests")
    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket, "getaddrinfo", blocked)
    from harness import http
    import subprocess
    monkeypatch.setattr(http, "get_raw", blocked)
    monkeypatch.setattr(subprocess, "run", blocked)


def _held(doc=DOC, url=FDA, sha=None):
    rec = {"url": url, "agency": rs.agency_of(url), "licence": rs.licence_of(url), "state": "TEXT", "doc_sha256": "d",
           "text_sha256": sha or rs.text_sha256(doc)}
    return {"text": "", "sha": None, "terms": ["mortality at day 28"], "comp": "33933206", "aact": {},
            "reg": {url: {"text": doc, "record": rec, "names": NAMES}}}


def _resp(**kw):
    base = {"verdict": "FOUND", "source": "REGULATORY", "source_ref": FDA, "aact_outcome_id": None, "measure": "COUNTS",
            "events_t": 58, "n_t": 294, "events_c": 28, "n_c": 144, "effect": None, "lower": None, "upper": None,
            "quote": "In Study WA42380, mortality at day 28 was 58/294 in the tocilizumab arm and 28/144 in the placebo arm.",
            "scope_rule_key": None, "scope_span": None}
    base.update(kw)
    return base


def test_licence_follows_the_host_only():
    assert rs.licence_of(FDA) == "US_GOV_PUBLIC_DOMAIN" and rs.prompt_open(FDA)
    # EMA: shown since 6 Oct (Mahmood: 'European drug agency can be used'), always with the source acknowledgement
    assert rs.licence_of(EMA) == "EMA_REUSE_WITH_ACKNOWLEDGEMENT" and rs.prompt_open(EMA)
    # NICE: notice of rights -> held, never shown, unless the document's own text states OGL / CC
    nice = "https://www.nice.org.uk/guidance/ta394/documents/committee-papers"
    assert rs.licence_of(nice) == "NICE_NOTICE_OF_RIGHTS" and not rs.prompt_open(nice)
    assert rs.licence_from_text(nice, "(c) NICE 2016. All rights reserved. Subject to Notice of rights.") == \
        "NICE_NOTICE_OF_RIGHTS"
    assert rs.licence_from_text(nice, "available under the Open Government Licence v3.0") == "OGL"
    assert rs.prompt_open(nice, {"licence": "OGL"}) and not rs.prompt_open(nice, {"licence": "NICE_NOTICE_OF_RIGHTS"})
    assert rs.licence_of("https://example.org/www.accessdata.fda.gov/review.pdf") is None      # host, not path


def test_a_named_trials_counts_in_the_whole_document_are_admitted_as_regulatory():
    v, adm = ga.gate(_resp(), _held(), CFG, "tocilizumab-covid19-mortality")
    assert v == "ADMITTED" and adm["kind"] == "REGULATORY"
    assert adm["url"] == FDA and adm["licence"] == "US_GOV_PUBLIC_DOMAIN" and adm["text_sha256"] == rs.text_sha256(DOC)


def test_regulatory_refusals():
    g = lambda r, h=None: ga.gate(r, h or _held(), CFG, "x")[0]  # noqa: E731
    assert g(_resp(source_ref=FDA + "?other")) == "REFUSED:REGULATORY_DOC_NOT_HELD"
    assert g(_resp(), _held(sha="0" * 64)) == "REFUSED:REGULATORY_DIGEST_MISMATCH"
    assert g(_resp(quote="mortality at day 28 was 58 of 294")) == "REFUSED:QUOTE_NOT_VERBATIM_IN_WHOLE_DOCUMENT"
    assert g(_resp(n_c=145)) == "REFUSED:NUMBERS_NOT_IN_QUOTE"
    # ANOTHER study's row in the same review (EMPACTA, far from any COVACTA name) is never COVACTA's result
    other = _resp(events_t=26, n_t=249, events_c=11, n_c=128,
                  quote="mortality at day 28 was 26/249 in the tocilizumab arm and 11/128 in the placebo arm.")
    assert g(other) == "REFUSED:TRIAL_NOT_NAMED_NEAR_QUOTE"


def test_windows_are_centred_on_a_naming_mention_with_an_outcome_term():
    ws = rs.evidence_windows(DOC, NAMES, ["mortality at day 28"])
    assert ws and all(any(n in w["text"] for n in NAMES) for w in ws)
    assert "26/249" not in "".join(w["text"] for w in ws)                   # EMPACTA's row is not shown for COVACTA
    assert rs.evidence_windows(DOC, NAMES, ["stroke"]) == []


def test_trial_names_take_the_registrys_sponsor_codes():
    n = rs.trial_names("FOURIER [12]", ["NCT01764633"], codes=["20110118", "Study", "2012-005094-11"])
    assert {"FOURIER", "NCT01764633", "20110118", "2012-005094-11"} <= set(n) and "Study" not in n


def _rec(url, licence_claim):
    ev = {"trial": "COVACTA", "regulatory": [{"url": url, "agency": "FDA", "licence": licence_claim,
                                              "windows": [{"offset": 0, "text": "mortality at day 28 " * 50}]}]}
    p = "INSTR\n\n=== EVIDENCE ===\n" + json.dumps(ev)
    return {"record_id": "mc-reg", "prompt": {"b64": base64.b64encode(p.encode()).decode()}, "input_digests": []}


def test_licence_guard_admits_fda_windows_and_refuses_any_other_host_whatever_the_prompt_claims():
    assert rl.record_problems(_rec(FDA, "US_GOV_PUBLIC_DOMAIN"), {}) == []
    assert rl.record_problems(_rec(EMA, "US_GOV_PUBLIC_DOMAIN"), {})           # a claimed licence counts for nothing
    assert rl.record_problems(_rec("https://example.org/review.pdf", "CC"), {})


def test_an_fda_toc_template_is_expanded_to_its_review_documents_and_an_anda_is_never_read(monkeypatch):
    from harness import http
    import k_gap_regulatory_probe as rp
    toc = "https://www.accessdata.fda.gov/drugsatfda_docs/nda/2023/125276Orig1s137TOC.cfm"
    api = {"results": [
        {"application_number": "BLA125276", "submissions": [{"application_docs": [
            {"type": "Review", "url": toc.replace("https://", "http://"), "date": "20230101"}]}]},
        {"application_number": "ANDA090548", "submissions": [{"application_docs": [
            {"type": "Review", "url": "https://www.accessdata.fda.gov/anda.pdf", "date": "20240101"}]}]}]}
    monkeypatch.setattr(http, "get_json", lambda *a, **k: api)
    monkeypatch.setattr(rs, "_nice_html", lambda u: "")
    page = ('<script>pdfBaseName = "125276Orig1s137";\n'
            "x = '<a href=\"' + pdfBaseName + 'MedR.pdf\" title=\"Go to clinical review(s)\">'</script>")
    monkeypatch.setattr(rp, "fetch_text", lambda u: (page, {"state": "NOT_PDF"}))
    urls = rs.fda_review_urls("tocilizumab")
    base = "https://www.accessdata.fda.gov/drugsatfda_docs/nda/2023/125276Orig1s137"
    assert base + "MedR.pdf" in urls and base + "StatR.pdf" in urls
    assert not any("'" in u or "+" in u or " " in u for u in urls)            # an unexpanded template href is no url
    assert not any("anda" in u for u in urls)


def test_nice_discovery_reads_published_guidance_and_its_evidence_documents():
    search = ('<a href="/guidance/ta394">x</a><a href="/guidance/indevelopment/gid-ta11482">y</a>'
              '<a href="/guidance/NG238">z</a><a href="/guidance/ta394/chapter/1">c</a>')
    assert rs.nice_guidance("evolocumab", html=search) == ["ta394", "ng238"]
    hist = ('<a href="/guidance/ta394/documents/committee-papers">a</a><a href="/guidance/ta394/documents/'
            'committee-papers-2">b</a><a href="/guidance/ta394/documents/final-appraisal-determination-document">c</a>'
            '<a href="/guidance/ta394/documents/draft-scope">d</a>')
    assert rs.nice_docs("ta394", history_html=hist) == [rs.NICE + "/guidance/ta394/documents/committee-papers",
                                                        rs.NICE + "/guidance/ta394/documents/committee-papers-2",
                                                        rs.NICE + "/guidance/ta394/documents/final-appraisal-determination"
                                                                  "-document"]
    ev = ('<a href="/guidance/ng238/evidence/d-escalation-of-lipid-treatment-pdf-13253908141">r</a>'
          '<a href="/guidance/ng238/evidence/appendix-b-stakeholders-comments-pdf-4724759775">s</a>')
    assert rs.nice_docs("ng238", evidence_html=ev) == [rs.NICE + "/guidance/ng238/evidence/d-escalation-of-lipid-"
                                                                 "treatment-pdf-13253908141"]


def test_typed_counts_need_a_header_naming_both_arms_and_corroborated_cells():
    w = ("Table 12. Study WA42380 (COVACTA) outcomes\nOutcome Tocilizumab (N=294) Placebo (N=144)\n"
         "Mortality at day 28 58/294 (19.7) 28/144 (19.4)\n")
    got = rs.typed_counts(w, ["mortality at day 28"], ["tocilizumab"], ["placebo"])
    assert got and got[0] == {"events_t": 58, "n_t": 294, "events_c": 28, "n_c": 144}
    swapped = w.replace("Tocilizumab (N=294) Placebo (N=144)", "Placebo (N=144) Tocilizumab (N=294)")
    assert rs.typed_counts(swapped, ["mortality at day 28"], ["tocilizumab"], ["placebo"])[0]["events_t"] == 28
    assert rs.typed_counts(w.replace("(19.7)", "(25.0)"), ["mortality at day 28"], ["tocilizumab"], ["placebo"]) is None
    assert rs.typed_counts(w.replace("Outcome Tocilizumab (N=294) Placebo (N=144)\n", ""),
                           ["mortality at day 28"], ["tocilizumab"], ["placebo"]) is None   # no arm order: no tuple


def test_licence_guard_needs_the_ema_acknowledgement_and_checks_a_shown_unpaywall_doi():
    ev = {"regulatory": [{"url": EMA, "agency": "EMA", "windows": [{"offset": 0, "text": "mortality " * 300}]}]}
    p = "I\n\n=== EVIDENCE ===\n" + json.dumps(ev)
    r = {"record_id": "mc-e", "prompt": {"b64": base64.b64encode(p.encode()).decode()}, "input_digests": []}
    assert rl.record_problems(r, {}, {}, {})                                      # no acknowledgement: refused
    ev["regulatory"][0]["acknowledgement"] = rs.EMA_ACK
    p = "I\n\n=== EVIDENCE ===\n" + json.dumps(ev)
    r["prompt"]["b64"] = base64.b64encode(p.encode()).decode()
    assert rl.record_problems(r, {}, {}, {}) == []
    ft = {"full_text": {"doi": "10.1/x", "licence": "cc-by", "text": "results " * 400}}
    q = "I\n\n=== EVIDENCE ===\n" + json.dumps(ft)
    rq = {"record_id": "mc-u", "prompt": {"b64": base64.b64encode(q.encode()).decode()}, "input_digests": []}
    assert rl.record_problems(rq, {}, {"10.1/x": "cc-by"}, {}) == []
    assert rl.record_problems(rq, {}, {"10.1/x": "other-oa"}, {})                 # the prompt's own claim is ignored


def test_typed_first_admits_a_regulator_table_without_a_model_and_checks_the_randomised_n(monkeypatch):
    doc = ("Study WA42380 (COVACTA) results. " + FILL[:2000] + "\nOutcome Tocilizumab (N=294) Placebo (N=144)\n"
           "Mortality at day 28 58/294 (19.7) 28/144 (19.4)\n" + FILL[:2000])
    held = _held(doc)
    cfg = dict(CFG, intervention_terms=["tocilizumab"], comparator_terms=["placebo"])
    t = {"slug": "tocilizumab-covid19-mortality", "pmid": None, "label": "COVACTA"}
    monkeypatch.setattr(ga, "posted_population_short", lambda *a: None)
    v, adm = ga.typed_first(t, cfg, held)
    assert v == "ADMITTED" and adm["kind"] == "REGULATORY_TABLE" and adm["row"].events_t == 58 and adm["url"] == FDA
    monkeypatch.setattr(ga, "posted_population_short", lambda *a: {"randomised_total": 900})
    assert ga.typed_first(t, cfg, held) == (None, None)                       # a subpopulation is never the trial's


def test_gba_amnog_documents_are_typed_only_and_discovered_from_gbas_own_search_words():
    # G-BA Impressum (13 Oct 2026): citing and linking only, so the AMNOG documents are held, never shown to a model
    u = "https://www.g-ba.de/downloads/92-975-4/2011-06-30_Modul4-A_Ticagrelor.pdf"
    assert rs.agency_of(u) == "GBA" and rs.licence_of(u) == "GBA_IQWIG_CITE_AND_LINK_ONLY"
    assert not rs.prompt_open(u) and not rs.prompt_open(u, {"licence": rs.licence_from_text(u, "Creative Commons Attribution")})
    words = ["Ticagrelor", "Icosapent-Ethyl", "Evolocumab", "Tiotropium", "Ticagrelorum X"]
    assert rs.gba_search_words("ticagrelor", words) == ["Ticagrelor"]
    assert rs.gba_search_words("icosapent ethyl", words) == ["Icosapent-Ethyl"]
    assert rs.gba_search_words("tico", words) == []
    listing = '<a href="/bewertungsverfahren/nutzenbewertung/18/">x</a><a href="/bewertungsverfahren/nutzenbewertung/225/">y</a>'
    assert rs.gba_procedures(listing) == ["18", "225"]
    page = ('<a href="/downloads/92-975-1/M1.pdf">Modul 1<span>(PDF)</span></a>'
            '<a href="/downloads/92-975-4/M4.pdf">Mo&shy;dul 4<span>(PDF 4 MB)</span></a>'
            '<a href="/downloads/92-975-5/NB.pdf">Nutzen­bewertung IQWiG(PDF)</a>'
            '<a href="/downloads/40-268-1/ZD.pdf">Zusammenfassende Dokumentation</a>')
    assert rs.gba_docs(page) == ["https://www.g-ba.de/downloads/92-975-4/M4.pdf",
                                 "https://www.g-ba.de/downloads/92-975-5/NB.pdf"]


def test_PLANT_a_programme_token_never_names_a_sibling_trial():
    # 13 Oct (G-BA pilot): 'ODYSSEY' / 'COMBO' / 'JAPAN' were each a name, so every ODYSSEY trial was 'named' in every
    # alirocumab document, and the gate's named-near-the-quote check could pass a COMBO II quote for COMBO I
    combo2 = "In ODYSSEY COMBO II the rate was 4/241 v 16/479. Table: COMBO II 4/241."
    for lab, nct in [("ODYSSEY COMBO I NCT01644175", "NCT01644175"), ("ODYSSEY JAPAN NCT02107898", "NCT02107898"),
                     ("ODYSSEY FH I NCT01623115", "NCT01623115")]:
        assert rs.named_at(combo2, rs.trial_names(lab, [nct])) == [], lab
    names = rs.trial_names("ODYSSEY COMBO I NCT01644175", ["NCT01644175"])
    assert rs.named_at("Study ODYSSEY COMBO I randomised 316.", names) and rs.named_at("COMBO I: 6/207 v 3/107", names)
    assert rs.named_at("FH I 3/163", rs.trial_names("ODYSSEY FH I NCT01623115", ["NCT01623115"]))
    assert "DESCARTES" in rs.trial_names("DESCARTES NCT01516879", ["NCT01516879"])      # a one-word acronym still names


def test_PLANT_pbac_is_typed_only():
    for host in ("pbs.gov.au", "www.pbs.gov.au"):
        u = f"https://{host}/industry/pbac/psd/2026/07/example.pdf?variant=3"
        assert rs.agency_of(u) == "PBAC"
        assert rs.licence_of(u) == "PBS_COPYRIGHT_PERSONAL_REFERENCE_ONLY"
        assert not rs.prompt_open(u)
        assert not rs.prompt_open(u, {"licence": rs.licence_from_text(u, "Creative Commons Attribution")})


def test_pbac_urls_keep_only_the_exact_inn(monkeypatch):
    h = ""
    for date, slug, name in [("2025/03", "older", "EVOLOCUMAB"), ("2026/07", "newer", "EVOLOCUMAB"),
                             ("2026/09", "analogue", "EVOLOCUMAB-LIKE THING"),
                             ("2026/10", "other", "ALIROCUMAB")]:
        p = f"/industry/pbac/psd/{date}/{slug}"
        h += f'<a href="{p}">{name}</a><a href="{p}.docx?variant=3">DOCX</a>'
        h += f'<a href="{p}.pdf?variant=3">PDF</a>'
    calls = []

    def listing(url):
        calls.append(url)
        return h
    monkeypatch.setattr(rs, "_nice_html", listing)
    assert rs.pbac_urls("evolocumab") == [
        rs.PBAC + "/industry/pbac/psd/2026/07/newer.pdf?variant=3",
        rs.PBAC + "/industry/pbac/psd/2025/03/older.pdf?variant=3"]
    assert calls == [rs.PBAC + "/industry/pbac/psd?term=evolocumab"]


def test_pbac_urls_fold_fallback_deduplicate_and_cap(monkeypatch):
    h = ""
    for month in range(1, 13):
        p = f"/industry/pbac/psd/2026/{month:02d}/salt"
        h += (f"<a href='{p}'>ICOSAPENT-ETHYL SODIUM</a>"
              f"<a href='https://pbs.gov.au{p}.docx?variant=3'>DOCX</a>") * 2
    h += ('<a href="/industry/pbac/psd/2025/12/old">ICOSAPENT ETHYL</a>'
          '<a href="/industry/pbac/psd/2025/12/old.pdf?variant=3">PDF</a>')
    calls = []
    monkeypatch.setattr(rs, "_nice_html", lambda u: calls.append(u) or h)
    assert rs.MAX_PBAC_DOCS == 12
    assert rs.pbac_urls("icosapent ethyl") == [
        rs.PBAC + f"/industry/pbac/psd/2026/{m:02d}/salt.docx?variant=3" for m in range(12, 0, -1)]
    assert calls == [rs.PBAC + "/industry/pbac/psd?term=icosapent%20ethyl"]
    assert rs.pbac_urls("icosapent ethyl", html="") == []


def test_nice_condition_query_runs_first_and_is_capped(monkeypatch):
    calls, docs = [], []

    def guidance(q):
        calls.append(q)
        return ["ng1", "ta1", "ng1"] if q == "evolocumab hypercholesterolaemia" else [
            f"ta{i}" for i in range(1, 25)]
    monkeypatch.setattr(rs, "nice_guidance", guidance)
    monkeypatch.setattr(rs, "nice_docs", lambda g: docs.append(g) or [rs.NICE + "/guidance/" + g])
    assert rs.MAX_NICE_GUIDANCE == 15
    expected = ["ng1"] + [f"ta{i}" for i in range(1, 15)]
    assert rs.nice_urls("evolocumab", "hypercholesterolaemia") == [rs.NICE + "/guidance/" + g for g in expected]
    assert calls == ["evolocumab hypercholesterolaemia", "evolocumab"]
    assert docs == expected
    calls.clear()
    docs.clear()
    rs.nice_urls("evolocumab")
    assert calls == ["evolocumab"] and docs == [f"ta{i}" for i in range(1, 16)]


def test_topic_condition_uses_first_population():
    assert rs.topic_condition({"include": {"population_any": ["first", "second"]}}) == "first"
    for cfg in ({}, {"include": {}}, {"include": {"population_any": []}}):
        assert rs.topic_condition(cfg) is None


HR_SENTENCE = ("The rate of MACE was 48% lower with alirocumab than with placebo (27 (1.7%) vs. 26 (3.3%); "
               "hazard ratio, 0.52; 95% confidence interval, 0.31 to 0.90; nominal P = 0.02)")
HR_DOC = "ODYSSEY LONG TERM" + " " * 200 + HR_SENTENCE


def test_PLANT_hr_sentence_found():
    hits = rs.typed_effect(HR_DOC, ["ODYSSEY LONG TERM"], ["MACE"])
    assert len(hits) == 1
    assert tuple(hits[0][k] for k in ("effect", "lower", "upper")) == (0.52, 0.31, 0.90)
    assert hits[0]["offset"] == 0 and hits[0]["span"] in HR_DOC


@pytest.mark.parametrize("pool", ["in the placebo-controlled pool", "POOLED", "meta-analysis", "global",
                                   "integrated", "across studies", "combined analysis"])
def test_pooled_hr_refused(pool):
    assert rs.typed_effect("ODYSSEY LONG TERM " + pool + HR_SENTENCE, ["ODYSSEY LONG TERM"], ["MACE"]) == []


def test_or_wording_not_hr():
    assert rs.typed_effect("TRIALX MACE odds ratio 0.52 (95% CI 0.31 to 0.90)", ["TRIALX"], ["MACE"]) == []


@pytest.mark.parametrize("line", ["HR: 0.52 (95% CI: 0.31, 0.90)", "HR 0.52 (95% CI 0.31–0.90)",
                                  "95% CI: HR 0.52 (0.31 to 0.90)", "95% CI: HR 0.52 (0.31-0.90)",
                                  "hazard ratio 0.52; 95% CI 0.31 to 0.90."])
def test_hr_patterns(line):
    assert rs.typed_effect("TRIALX MACE " + line, ["TRIALX"], ["mace"])


@pytest.mark.parametrize("line", ["HR 0.52 (0.31 to 0.90)", "HR 0.52 (90% CI 0.31 to 0.90)",
                                  "HR 0,52 (95% CI 0,31 to 0,90)", "HR 0.52 (95% CI 0.52 to 0.90)",
                                  "HR 0.52 (95% CI 0 to 0.90)", "RR 0.52 (95% CI 0.31 to 0.90)"])
def test_hr_invalid_or_unstated_ci_refused(line):
    assert rs.typed_effect("TRIALX MACE " + line, ["TRIALX"], ["MACE"]) == []


def test_hr_name_and_outcome_reach():
    assert rs.typed_effect("TRIALX " + "x" * 601 + HR_SENTENCE, ["TRIALX"], ["MACE"]) == []
    assert rs.typed_effect(HR_DOC, ["ODYSSEY LONG TERM"], ["stroke"]) == []
    assert rs.typed_effect(HR_DOC, ["ODYSSEY LONG TERM"], ["MACE"], measure="OR") == []
    assert rs.typed_effect(HR_SENTENCE + " TRIALX", ["TRIALX"], ["MACE"]) == []
    assert rs.typed_effect("TRIALX pooled discussion. TRIALX " + HR_SENTENCE, ["TRIALX"], ["MACE"])


def test_two_documents_disagree_returns_none():
    h = {"text": HR_DOC, "names": ["ODYSSEY LONG TERM"], "record": {}}
    held = {"a": h, "b": dict(h, text=HR_DOC.replace("0.52", "0.60"))}
    assert rs.regulatory_typed_effect(held, ["MACE"]) is None
    held["b"] = h
    got = rs.regulatory_typed_effect(held, ["MACE"])
    assert got[0] == "a" and got[2] == {"measure": "HR", "effect": 0.52, "lower": 0.31, "upper": 0.90}


def test_typed_first_hr_is_held_not_admitted(monkeypatch):
    rec = _held()["reg"][FDA]["record"]
    value = {"measure": "HR", "effect": 0.52, "lower": 0.31, "upper": 0.90}
    monkeypatch.setattr(rs, "regulatory_typed_effect", lambda *a: (FDA, rec, value, HR_DOC))
    v, adm = ga.typed_first({"label": "TRIALX", "pmid": None, "slug": "x"},
                            {"primary_outcome": {"estimand": "HR", "keywords": ["MACE"]}}, _held())
    assert v == "HELD_FOR_BINDING" and adm["kind"] == "REGULATORY_EFFECT"
    assert adm["value"] == value and adm["quote"] is None and adm["span"] == HR_DOC[:600]
    for k in ("url", "agency", "licence", "doc_sha256", "text_sha256"):
        assert adm[k] == rec[k]


def test_binding_requires_complete_digest_keyed_ruling(monkeypatch):
    ruling = dict.fromkeys(("arm", "outcome", "timepoint", "population", "analysis_set", "ruled_by", "ruled_on", "reason"),
                           "synthetic")
    ruling["decision"] = "BOUND"
    monkeypatch.setattr(rs, "_load", lambda p: {"x|TRIALX|digest": ruling})
    assert rs.binding_for("x", "TRIALX", FDA, "digest") == ruling
    assert rs.binding_for("x", "TRIALX", FDA, "changed") is None
    for k in list(ruling):
        partial = {key: val for key, val in ruling.items() if key != k}
        monkeypatch.setattr(rs, "_load", lambda p: {"x|TRIALX|digest": partial})
        assert rs.binding_for("x", "TRIALX", FDA, "digest") is None


@pytest.fixture
def discoveries(monkeypatch, tmp_path):
    import k_gap_regulatory_probe as rp
    monkeypatch.setattr(rs, "ROOT", str(tmp_path))
    monkeypatch.setattr(rs, "SOURCES", str(tmp_path / "sources.json"))
    monkeypatch.setattr(rp, "REG", str(tmp_path / "text"))
    for name in ("fda_review_urls", "nice_urls", "gba_urls", "pbac_urls", "cadth_urls", "iqwig_urls"):
        monkeypatch.setattr(rs, name, lambda *a: [])
    monkeypatch.setattr(rp, "_j_ema", lambda: [])
    monkeypatch.setattr(ga, "disk_ok", lambda: True)
    return rp


def test_fda_overview_reviews_first_labels_capped(monkeypatch):
    from harness import http
    import k_gap_regulatory_probe as rp
    base = "https://www.accessdata.fda.gov/drugsatfda_docs/"
    reviews = [base + "nda/2099/000000MedR.pdf", base + "bla/2099/000000StatR.pdf"]
    toc = base + "nda/2099/000000TOC.cfm"
    labels = [base + f"label/{year}/000000lbl.pdf" for year in range(2095, 2100)]
    letters = [base + f"appletter/2099/000000s{i}.pdf" for i in range(2)]
    calls = []
    def overview(url):
        calls.append(url)
        return "".join(f'<a href="{u}">document</a>' for u in reviews + [toc] + labels + letters)
    monkeypatch.setattr(rs, "_nice_html", overview)
    monkeypatch.setattr(http, "get_json", lambda *a, **k: {"results": [{"application_number": "NDA000000"}]})
    monkeypatch.setattr(rp, "fetch_text", lambda u: ('<script>pdfBaseName = "000000";</script>', {}))
    got = rs.fda_review_urls("synthetic")
    assert got[-3:] == labels[::-1][:3]
    assert set(reviews) <= set(got[:-3])
    assert base + "nda/2099/000000MedR.pdf" in got
    assert base + "nda/2099/000000IntegratedR.pdf" in got
    assert not set(letters) & set(got)
    assert calls == ["https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo=000000"]


@pytest.mark.parametrize("reason,expected", [({"http_status": 503}, "503"),
                                           ({"error": "TimeoutError: " + "x" * 180}, ("TimeoutError: " + "x" * 180)[:120])])
def test_fetch_failed_records_reason(monkeypatch, discoveries, reason, expected):
    monkeypatch.setattr(rs, "fda_review_urls", lambda a: [FDA])
    monkeypatch.setattr(discoveries, "fetch_text", lambda u: ("", dict(reason, state="FETCH_FAILED")))
    got = rs.hold_topic("synthetic", {"intervention_agents": ["synthetic"]})
    assert got[0]["fetch_error"] == expected


def test_fda_topic_cap_prioritizes_all_agents_reviews(monkeypatch, discoveries):
    labels = [f"https://www.accessdata.fda.gov/drugsatfda_docs/label/2099/{i}.pdf" for i in range(120)]
    reviews = [f"https://www.accessdata.fda.gov/drugsatfda_docs/nda/2099/{i}MedR.pdf" for i in range(119)]
    monkeypatch.setattr(rs, "fda_review_urls", lambda a: labels if a == "first" else reviews)
    monkeypatch.setattr(discoveries, "fetch_text", lambda u: ("text", {"state": "TEXT"}))
    got = rs.hold_topic("synthetic", {"intervention_agents": ["first", "second"]})
    assert len(got) == 120 and [r["url"] for r in got[:119]] == reviews


def test_cadth_urls_select_reviews_only(monkeypatch, tmp_path):
    import csv
    import io
    from harness import http
    monkeypatch.setattr(rs, "ROOT", str(tmp_path))
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["File", "Title", "Publisher", "Publication Year", "Accession ID", "Last Updated"])
    publisher = "Canadian Agency for Drugs and Technologies in Health"
    titles = ["Synthetic Clinical Review", "Synthetic Reimbursement Review", "Synthetic Rapid Review",
              "Synthetic Review of Clinical Effectiveness", "Synthetic Health Technology Review",
              "Synthetic Pharmacoeconomic Clinical Review", "Synthetic Recommendation Clinical Review",
              "Synthetical Clinical Review", "Synthetic Patient Group Input Clinical Review",
              "Synthetic Environmental Scan Clinical Review", "Synthetic Clinical Review"]
    for i, title in enumerate(titles):
        writer.writerow([f"NBK{i:06d}.tar.gz", title, publisher if i != 10 else "Other", "2099", f"NBK{i:06d}", f"2099-01-{i+1:02d}"])
    calls = []
    def fetch(url, **kw):
        calls.append(url)
        assert http.UA == rs.USER_AGENT
        return 200, buf.getvalue().encode()
    monkeypatch.setattr(http, "get_raw", fetch)
    expected = [rs.LITARCH_BASE + f"NBK{i:06d}.tar.gz" for i in reversed(range(5))]
    assert rs.cadth_urls("synthetic") == expected
    assert rs.cadth_urls("synthetic") == expected and len(calls) == 1
    fp = rs._reg_dir() / "litarch_file_list.csv"
    os.utime(fp, (0, 0))
    assert rs.cadth_urls("synthetic") == expected and len(calls) == 2


def _tar(members):
    import io
    import tarfile
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as archive:
        for name, text in members:
            body = text.encode()
            info = tarfile.TarInfo(name)
            info.size = len(body)
            archive.addfile(info, io.BytesIO(body))
    return buf.getvalue()


def _nxml(text, licence="CC BY 4.0"):
    return f'<book-part><permissions><license>{licence}</license></permissions><body>{text}</body></book-part>'


def test_PLANT_litarch_tar_traversal_refused():
    body = _tar([(n, _nxml("evil")) for n in ("../evil.nxml", "/absolute.nxml", "C:/drive.nxml", "a\\..\\bad.nxml")]
                + [("good.nxml", _nxml("<p>Good</p><table><tr><td>1</td><td>2</td></tr></table>"))])
    text, licence = rs._litarch_text(body)
    assert "evil" not in text and "Good" in text and "1 | 2" in text and licence == "CC"


def test_litarch_toc_order_and_size_cap(monkeypatch):
    toc = '<book><permissions>CC BY 4.0</permissions><book-toc><xref rid="second"/><xref rid="first"/></book-toc></book>'
    body = _tar([("first.nxml", _nxml("FIRST")), ("second.nxml", _nxml("SECOND")), ("toc.nxml", toc)])
    text, _ = rs._litarch_text(body)
    assert text.index("SECOND") < text.index("FIRST")
    monkeypatch.setattr(rs, "MAX_LITARCH_BYTES", 10)
    with pytest.raises(ValueError, match="50 MB"):
        rs._litarch_text(body)


@pytest.mark.parametrize("licence,expected", [("CC BY-NC-ND 4.0", "CADTH_CC_BY_NC_ND_TYPED_ONLY"),
                                               ("Copyright", "CADTH_COPYRIGHT_TYPED_ONLY"), ("CC BY 4.0", "CC"), ("CC0", "CC")])
def test_cadth_licence_nc_nd_is_typed_only(licence, expected):
    _, actual = rs._litarch_text(_tar([("good.nxml", _nxml("Content", licence))]))
    assert actual == expected
    assert rs.prompt_open(rs.LITARCH_BASE + "NBK000000.tar.gz", {"licence": actual}) == (expected == "CC")
    # A citation outside permissions cannot grant a licence.
    _, actual = rs._litarch_text(_tar([("good.nxml", _nxml("CC BY 4.0", "Copyright"))]))
    assert actual == "CADTH_COPYRIGHT_TYPED_ONLY"


def test_redaction_blocks_counted(monkeypatch, discoveries):
    from harness import http
    url = rs.LITARCH_BASE + "NBK000000.tar.gz"
    monkeypatch.setattr(rs, "cadth_urls", lambda a: [url])
    monkeypatch.setattr(http, "get_raw", lambda *a, **k: (200, _tar([("good.nxml", _nxml("Redacted \u2588\u2588\u2588"))])))
    held = rs.hold_topic("synthetic", {"intervention_agents": ["synthetic"]})
    assert held[0]["redaction_blocks"] == 3 and held[0]["licence"] == "CC"
    assert rs.doc_text(url).count("\u2588") == 3


def test_iqwig_codes_from_gba_text_and_project_pdfs(monkeypatch):
    pages = {rs.GBA_NB + "suchworte.json": '["Synthetic"]',
             rs.GBA_NB + "?suchwort=Synthetic": '<a href="/bewertungsverfahren/nutzenbewertung/1/">x</a>',
             rs.GBA_NB + "1/": '<p>Assessment A15-47</p><a href="/A99-99/">not a code in text</a>',
             rs.IQWIG + "/en/search/?q=synthetic": "<p>No hits</p>",
             rs.IQWIG + "/en/projects/a15-47.html": '<a href="/download/a15-47_assessment.pdf">German</a>'
                 '<a href="/download/a15-47_extract.pdf">English</a><a href="https://other.org/download/x.pdf">other</a>'}
    calls = []
    def fetch(u):
        calls.append(u)
        return pages[u]
    monkeypatch.setattr(rs, "_GBA_PAGES", {})
    monkeypatch.setattr(rs, "_nice_html", fetch)
    rs.gba_urls("synthetic")
    assert rs.iqwig_urls("synthetic") == [rs.IQWIG + "/download/a15-47_extract.pdf", rs.IQWIG + "/download/a15-47_assessment.pdf"]
    assert calls.count(rs.GBA_NB + "1/") == 1
    assert not rs.prompt_open(rs.IQWIG + "/download/a15-47_extract.pdf")


def _hc_page():
    heads = ["Control number", "Brand name", "Manufacturer", "Medicinal ingredients", "Activity", "Decision", "Decision date", "Release date"]
    rows = []
    for ingredient in ("Synthetic hydrochloride", "Synthetical"):
        cells = ['<a href="/ci-rc/terms/000000">000000</a>', 'Brand', 'Maker', ingredient, 'Review', 'Approved', '2099-01-01', '2099-02-01']
        rows.append('<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>')
    return '<div class="view-content"><table><thead><tr>' + ''.join(f'<th>{h}</th>' for h in heads) + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>'


def test_PLANT_hc_listing_never_requests_terms(monkeypatch, tmp_path):
    monkeypatch.setattr(rs, "ROOT", str(tmp_path))
    calls = []
    def fetch(url):
        calls.append(url)
        assert "/terms" not in url
        return _hc_page()
    monkeypatch.setattr(rs, "_hc_fetch", fetch)
    assert len(rs.hc_listing("synthetic")) == 1
    assert calls == [rs.HC_SEARCH + "?dpq=synthetic"]



def test_hc_listing_parses_rows(monkeypatch, tmp_path):
    monkeypatch.setattr(rs, "ROOT", str(tmp_path))
    monkeypatch.setattr(rs, "_hc_fetch", lambda url: _hc_page())
    assert rs.hc_listing("synthetic") == [{"control_number": "000000", "brand": "Brand", "manufacturer": "Maker",
        "ingredients": "Synthetic hydrochloride", "activity": "Review", "decision": "Approved",
        "decision_date": "2099-01-01", "release_date": "2099-02-01"}]
    cache = json.loads((rs._reg_dir() / "hc_listing.json").read_text())
    assert len(cache["synthetic"]["rows"]) == 1


def test_hc_fetch_refuses_terms_before_transport():
    with pytest.raises(ValueError, match="listing only"):
        rs._hc_fetch("https://clinical-information.canada.ca/ci-rc/terms/000000")


def test_hc_tls_unavailable_is_recorded(monkeypatch, tmp_path):
    monkeypatch.setattr(rs, "ROOT", str(tmp_path))
    monkeypatch.setitem(sys.modules, "truststore", None)
    monkeypatch.setattr(sys, "platform", "linux")
    assert rs.hc_listing("synthetic") == []
    assert json.loads((rs._reg_dir() / "hc_listing.json").read_text())["synthetic"]["error"] == "HC_TLS_UNAVAILABLE"


def test_iqwig_search_form_fallback(monkeypatch):
    monkeypatch.setattr(rs, "_GBA_PAGES", {"synthetic": []})
    pages = {rs.IQWIG + "/en/search/?q=synthetic": "", rs.IQWIG + "/en/":
             '<form action="/en/find/"><input type="search" name="term"></form>',
             rs.IQWIG + "/en/find/?term=synthetic": '<p>A99-123</p>'}
    monkeypatch.setattr(rs, "_nice_html", lambda u: pages[u])
    assert rs.iqwig_codes("synthetic") == ["A99-123"]


def test_cadth_unknown_permissions_fail_closed():
    url = rs.LITARCH_BASE + "NBK000000.tar.gz"
    assert rs.licence_from_text(url, '<p>CC BY 4.0</p>') == "CADTH_COPYRIGHT_TYPED_ONLY"
    assert rs.licence_from_text(url, '<permissions>CC BY-NC-ND 4.0</permissions>') == "CADTH_CC_BY_NC_ND_TYPED_ONLY"
    assert rs.licence_from_text(url, '<permissions>CC BY 4.0</permissions>') == "CC"


def test_fda_labels_use_overview_approval_dates(monkeypatch):
    from harness import http
    base = "https://www.accessdata.fda.gov/drugsatfda_docs/label/2099/"
    rows = ''.join(f'<tr><td>01/{day:02d}/2099</td><td><a href="{base}{name}.pdf">label</a></td></tr>'
                   for day, name in [(1, "z"), (2, "y"), (3, "x"), (4, "a"), (5, "b")])
    monkeypatch.setattr(http, "get_json", lambda *a, **k: {"results": [{"application_number": "NDA000000"}]})
    monkeypatch.setattr(rs, "_nice_html", lambda u: '<table>' + rows + '</table>')
    assert rs.fda_review_urls("synthetic") == [base + name + '.pdf' for name in ('b', 'a', 'x')]
