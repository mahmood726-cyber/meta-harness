"""REGULATORY source route (scripts/g1_regulatory_source.py + g1_trial_acquire.regulatory_gate + the licence guard):
an FDA review is a PRIMARY-grade source for a trial it NAMES, admitted only against the WHOLE held document; the licence
follows from the url's HOST and the held record (FDA open; EMA shown with its acknowledgement; NICE only if
its own text states OGL/CC); a prompt cannot declare itself open."""
import base64
import json
import os
import sys

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


def test_PLANT_an_application_without_openfda_names_is_found_by_its_active_ingredient(monkeypatch):
    # R9-4 (9 Oct): KERENDIA NDA215341 carries no openfda.generic_name, so the generic-name search returned nothing and
    # no finerenone label or review was ever held. The application's OWN products.active_ingredients names the drug.
    from harness import http
    lbl = "http://www.accessdata.fda.gov/drugsatfda_docs/label/2021/215341s000lbl.pdf"
    hit = {"results": [{"application_number": "NDA215341", "submissions": [{"application_docs": [
        {"type": "Label", "url": lbl, "date": "20210712"}]}]},
        {"application_number": "ANDA220684", "submissions": [{"application_docs": [
            {"type": "Label", "url": "https://www.accessdata.fda.gov/anda_label.pdf", "date": "20250101"}]}]}]}

    def get_json(url, params=None, **k):
        if "generic_name" in (params or {}).get("search", ""):
            raise RuntimeError("HTTP 404 NOT_FOUND: No matches found!")
        assert 'products.active_ingredients.name:"FINERENONE"' == params["search"]
        return hit
    monkeypatch.setattr(http, "get_json", get_json)
    urls = rs.fda_review_urls("finerenone")
    assert urls == [lbl.replace("http://", "https://")]
