"""Plants for the OPEN-SOURCE routes (scripts/g1_open_sources.py) and their wiring into the acquisition gates
(scripts/g1_trial_acquire.py) and the licence guard (reproducible_ai/record_licence.py). One plant per rule; no network.

  OPEN_LOCATION  licence of record = the HOST page's own licence tag (never the discovery index); a bot challenge is
                 recorded and never retried; the copy must carry the report's title words; one stated NCT only
  EUCTR          typed parse of the results page (arms, Ns, units, categories, 95% two-sided analyses; stops at the
                 adverse-event section); counts only under people units; arms oriented by terms with the page's own
                 abbreviations; an effect is never inverted; admission only through the AACT binding gates
  guard          a prompt may carry an open-location copy only when THAT copy's record is a CC text of THAT DOI
  regex first    the pinned extractor's reading of an open text goes through the same gate as a model answer
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_open_sources as O  # noqa: E402
import g1_trial_acquire as A  # noqa: E402
from reproducible_ai import record_licence as RL  # noqa: E402

JSTAGE = ('<meta name="cc_license_type" content="Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND '
          '4.0)" />\n<meta name="cc_license_url" content="https://creativecommons.org/licenses/by-nc-nd/4.0/" />')
FOOTER_ONLY = '<footer><a href="https://creativecommons.org/licenses/by/4.0/">our blog is CC BY</a></footer>'
CF = b'<!DOCTYPE html><html lang="en-US"><head><title>Just a moment...</title></head><body>cf-chl</body></html>'


def test_licence_of_record_is_the_host_pages_own_licence_tag():
    assert O.page_licence(JSTAGE)[0] == "cc-by-nc-nd"
    assert O.page_licence('<link rel="license" href="https://creativecommons.org/publicdomain/zero/1.0/">')[0] == "cc0"
    # a creativecommons.org link that is not a licence tag licenses nothing
    assert O.page_licence(FOOTER_ONLY) == (None, None)
    assert O.page_licence("") == (None, None)


def test_a_bot_challenge_is_recognised_and_a_pdf_is_not():
    assert O.is_challenge(403, CF)
    assert O.is_challenge(200, CF)
    assert not O.is_challenge(200, b"%PDF-1.7 ...")
    assert not O.is_challenge(404, b"<html><title>Not found</title></html>")


def _isolate(monkeypatch, tmp_path):
    monkeypatch.setattr(O, "SOURCES", str(tmp_path / "open_sources.json"))
    monkeypatch.setattr(O, "TEXTS", str(tmp_path / "_open"))


def test_a_challenged_copy_is_recorded_once_and_never_retried(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    calls = []
    monkeypatch.setattr(O, "oa_locations", lambda doi: [{"via": "OpenAlex", "pdf_url": "https://pub.example/a.pdf",
                                                         "landing_url": "https://pub.example/a", "version":
                                                         "publishedVersion", "index_licence": "cc-by"}])

    def fake_fetch(url, timeout=60, accept=None):
        calls.append(url)
        return 403, "text/html", CF, url
    monkeypatch.setattr(O, "fetch", fake_fetch)
    assert O.open_location("1", "10.1/x", "A trial of something in some patients") == ("", None)
    assert O._load()["https://pub.example/a.pdf"]["state"] == "BOT_CHALLENGE"
    n = len(calls)
    assert O.open_location("1", "10.1/x", "A trial of something in some patients") == ("", None)
    assert len(calls) == n                                 # recorded once: never fetched again


def test_the_index_licence_is_not_of_record(monkeypatch, tmp_path):
    # OpenAlex says cc-by; the host page states no licence -> NOT_OPEN, the PDF is never fetched, no text is held
    _isolate(monkeypatch, tmp_path)
    monkeypatch.setattr(O, "oa_locations", lambda doi: [{"via": "OpenAlex", "pdf_url": "https://pub.example/b.pdf",
                                                         "landing_url": "https://pub.example/b", "version": None,
                                                         "index_licence": "cc-by"}])
    fetched = []

    def fake_fetch(url, timeout=60, accept=None):
        fetched.append(url)
        return 200, "text/html", b"<html><head><title>Article</title></head></html>", url
    monkeypatch.setattr(O, "fetch", fake_fetch)
    assert O.open_location("1", "10.1/y", "A trial") == ("", None)
    assert O._load()["https://pub.example/b.pdf"]["state"] == "NOT_OPEN"
    assert fetched == ["https://pub.example/b"]


def test_identity_needs_the_reports_title_words_and_one_stated_registration():
    title = "Efficacy and Safety of Sacubitril/Valsartan in Japanese Patients With Chronic Heart Failure"
    assert O.identity_ok("efficacy and safety of sacubitril/valsartan in japanese patients with chronic heart failure "
                         "and reduced ejection fraction", title)
    assert not O.identity_ok("an editorial about something else entirely", title)
    assert O.stated_registration("registered (NCT02468232). Methods ... NCT02468232") == "NCT02468232"
    assert O.stated_registration("as in PARADIGM-HF (NCT01035255) and in our trial (NCT02468232)") is None


EUCTR_PAGE = """
<table><tr><td class="labelColumn"><div> Arm title</div></td><td class="valueColumn">Ferric carboxymaltose (FCM)</td></tr>
<tr><td class="labelColumn"><div> Arm title</div></td><td class="valueColumn">Standard of Care (SoC)</td></tr></table>
<table>
<tr><td class="labelColumn"><div> End point title</div></td><td class="valueColumn">Hospitalisation for worsening heart failure</td></tr>
<tr><td class="labelColumn"><div> End point type</div></td><td class="valueColumn"><div> Secondary </div></td></tr>
<tr><td class="labelColumn"><div> End point timeframe</div></td><td class="valueColumn"><div> From Baseline until Week 24 </div></td></tr>
<tr><td colspan="2" class="embeddedTableContainer"><table class="embeddedTable">
<tr><td class="header labelColumn"><div> End point values</div></td><td class="valueColumn">Full analysis set - FCM</td><td class="valueColumn">Full analysis set - SoC</td></tr>
<tr><td class="labelColumn"><div> Number of subjects analysed</div></td><td><div> 100 </div></td><td><div> 100 </div></td></tr>
<tr><td class="labelColumn"><div> Units: subjects</div></td><td><div></div></td><td><div></div></td></tr>
<tr><td class="labelColumn"><div>&nbsp;&nbsp;&nbsp;&nbsp;Hospitalised</div></td><td><div> 10 </div></td><td><div> 20 </div></td></tr>
</table></td></tr>
<tr><td class="header labelColumn"><div> Statistical analysis title</div></td><td class="valueColumn">HR</td></tr>
<tr><td class="labelColumn"><div> Comparison groups</div></td><td class="valueColumn"><div> Full analysis set - SoC v Full analysis set - FCM </div></td></tr>
<tr><td class="labelColumn"><div> Parameter type</div></td><td class="valueColumn"> Hazard ratio (HR) </td></tr>
<tr><td class="labelColumn"><div> Point estimate</div></td><td class="valueColumn"><div> 2.00 </div></td></tr>
<tr><td class="labelColumn"><div>&nbsp;&nbsp;&nbsp;&nbsp; level</div></td><td class="valueColumn">95%</td></tr>
<tr><td class="labelColumn"><div>&nbsp;&nbsp;&nbsp;&nbsp; sides</div></td><td class="valueColumn"><div> 2-sided </div></td></tr>
<tr><td class="labelColumn"><div>&nbsp;&nbsp;&nbsp;&nbsp; lower limit</div></td><td class="valueColumn"> 1.10 </td></tr>
<tr><td class="labelColumn"><div>&nbsp;&nbsp;&nbsp;&nbsp; upper limit</div></td><td class="valueColumn"> 3.60 </td></tr>
<tr><td class="labelColumn"><div> End point title</div></td><td class="valueColumn">Death rate</td></tr>
<tr><td class="labelColumn"><div> End point timeframe</div></td><td class="valueColumn"><div> Week 24 </div></td></tr>
<tr><td class="header labelColumn"><div> End point values</div></td><td class="valueColumn">Safety Set - FCM</td><td class="valueColumn">Safety Set - SoC</td></tr>
<tr><td class="labelColumn"><div> Number of subjects analysed</div></td><td><div> 100 </div></td><td><div> 100 </div></td></tr>
<tr><td class="labelColumn"><div> Units: percent</div></td><td><div></div></td><td><div></div></td></tr>
<tr><td class="labelColumn"><div>&nbsp;&nbsp;&nbsp;&nbsp;Any death</div></td><td><div> 5 </div></td><td><div> 6 </div></td></tr>
<tr><td class="labelColumn"><div> Adverse events information</div></td><td></td></tr>
<tr><td class="labelColumn"><div> End point title</div></td><td class="valueColumn">never parsed</td></tr>
</table>"""


def test_the_euctr_page_is_parsed_typed_and_stops_at_adverse_events():
    eps = O.parse_euctr(EUCTR_PAGE)
    assert [e["title"] for e in eps] == ["Hospitalisation for worsening heart failure", "Death rate"]
    e = eps[0]
    assert e["arms"] == ["Full analysis set - FCM", "Full analysis set - SoC"] and e["n"] == [100, 100]
    assert e["units"] == "subjects" and e["categories"] == [("Hospitalised", ["10", "20"])]
    a = e["analyses"][0]
    assert (a["param_type"], a["value"], a["lower"], a["upper"], a["level"], a["sides"]) == \
        ("Hazard ratio (HR)", "2.00", "1.10", "3.60", "95%", "2-sided")
    assert O.arm_aliases(EUCTR_PAGE) == {"FCM": "Ferric carboxymaltose", "SoC": "Standard of Care"}


def test_counts_only_under_people_units_and_a_percent_is_never_a_count():
    reg = O.euctr_registry(O.parse_euctr(EUCTR_PAGE), "2011-000000-00", "d", O.arm_aliases(EUCTR_PAGE))
    with_counts = {reg["outcomes"][k]["title"] for k in reg["groups"]}
    assert with_counts == {"Hospitalisation for worsening heart failure: Hospitalised"}
    assert reg["analyses"][0]["groups"] == ["2011-000000-00:0:g0", "2011-000000-00:0:g1"] or \
        len(reg["analyses"][0]["groups"]) == 2


CFG = {"primary_outcome": {"name": "Heart-failure hospitalization", "estimand": "RR",
                           "keywords": ["hospitalisation for worsening heart failure"]},
       "intervention_terms": ["ferric carboxymaltose"], "comparator_terms": ["standard of care", "placebo"]}


def _held(reg):
    return {"euctr": {"2011-000000-00": {"_reg": reg, "record": {"url": "https://www.clinicaltrialsregister.eu/x"},
                                         "found_by": "AACT id_information"}}}


def test_euctr_counts_are_admitted_through_the_registry_gate_with_arms_from_the_pages_own_abbreviations():
    reg = O.euctr_registry(O.parse_euctr(EUCTR_PAGE), "2011-000000-00", "d", O.arm_aliases(EUCTR_PAGE))
    v, adm = A.euctr_typed({"slug": "no-such-topic", "pmid": None}, CFG, _held(reg))
    assert v == "ADMITTED" and adm["kind"] == "EUCTR" and adm["licence"] == O.THIRD_PARTY
    r = adm["row"]
    assert (r.events_t, r.n_t, r.events_c, r.n_c) == (10, 100, 20, 100)
    # without the page's own definitions 'SoC' names no comparator term: no orientation, nothing admitted
    reg2 = dict(reg, arm_aliases={})
    assert A.euctr_typed({"slug": "no-such-topic", "pmid": None}, CFG, _held(reg2)) == (None, None)


def test_an_effect_is_never_inverted():
    # the page's HR is SoC v FCM (control first): never read as FCM v SoC
    reg = O.euctr_registry(O.parse_euctr(EUCTR_PAGE), "2011-000000-00", "d", O.arm_aliases(EUCTR_PAGE))
    cfg = dict(CFG, primary_outcome=dict(CFG["primary_outcome"], estimand="HR"))
    v, adm = A.euctr_typed({"slug": "no-such-topic", "pmid": None}, cfg, _held(reg))
    assert v is None or adm["row"].effect is None


def test_two_different_admitted_tuples_are_ambiguous():
    reg = O.euctr_registry(O.parse_euctr(EUCTR_PAGE), "2011-000000-00", "d", O.arm_aliases(EUCTR_PAGE))
    oid = next(iter(reg["groups"]))
    reg["outcomes"][oid + "b"] = dict(reg["outcomes"][oid], title=reg["outcomes"][oid]["title"] + " (2)")
    reg["groups"][oid + "b"] = [dict(g, count=g["count"] + 1) for g in reg["groups"][oid]]
    assert A.euctr_typed({"slug": "no-such-topic", "pmid": None}, CFG, _held(reg)) == (None, None)


def test_the_guard_admits_an_open_location_copy_only_on_its_own_cc_record(tmp_path, monkeypatch):
    src = tmp_path / "open_sources.json"
    src.write_text(json.dumps({
        "https://j.example/a.pdf": {"route": "OPEN_LOCATION", "state": "CC_TEXT", "doi": "10.1/a", "licence": "cc-by-nc-nd"},
        "https://j.example/b.pdf": {"route": "OPEN_LOCATION", "state": "NOT_OPEN", "doi": "10.1/b", "licence": None}}),
        encoding="utf-8")
    monkeypatch.setattr(RL, "OPEN_SOURCES", str(src))
    assert RL.open_location_licence("https://j.example/a.pdf", "10.1/A") == "cc-by-nc-nd"
    assert RL.open_location_licence("https://j.example/b.pdf", "10.1/b") is None
    assert RL.open_location_licence("https://j.example/a.pdf", "10.1/other") is None     # another DOI's copy

    import base64

    def rec(url, doi):
        ev = {"full_text": {"doi": doi, "copy_url": url, "licence": "cc-by", "text": "x" * 3000}}
        p = "INSTR\n\n=== EVIDENCE ===\n" + json.dumps(ev)
        return {"record_id": "plant", "prompt": {"b64": base64.b64encode(p.encode()).decode()}, "input_digests": []}
    assert not [p for p in RL.record_problems(rec("https://j.example/a.pdf", "10.1/a"), lic={}, dlic={})
                if "copy" in p]
    assert [p for p in RL.record_problems(rec("https://j.example/b.pdf", "10.1/b"), lic={}, dlic={}) if "copy" in p]


SACVAL = json.load(open(os.path.join(ROOT, "topics", "sacubitril-valsartan-hfref.json"), encoding="utf-8"))
# PARALLEL-HF (Tsutsui 2021, Circ J, CC BY-NC-ND 4.0): one sentence of the abstract
PARALLEL = ("Over a median follow up of 33.9 months, no significant between-group difference was observed for the primary "
            "composite outcome of CV death and HF hospitalization (HR 1.09; 95% CI 0.65-1.82; P=0.6260). Early and "
            "sustained reductions in NT-proBNP were observed.")


def test_regex_first_the_extractor_reading_goes_through_the_model_gate():
    held = {"text": PARALLEL * 1, "terms": A.outcome_terms(SACVAL), "comp": "36722326", "pmid": "33731544",
            "slug": "sacubitril-valsartan-hfref", "sha": "s", "text_origin": "OPEN_LOCATION",
            "text_url": "https://j.example/a.pdf", "doi_licence": "cc-by-nc-nd"}
    v, adm = A.extractor_proposal({"slug": "sacubitril-valsartan-hfref", "pmid": "33731544"}, SACVAL, held)
    assert v == "ADMITTED" and adm["kind"] == "TEXT_EXTRACTOR"
    assert (adm["row"].effect, adm["row"].lower, adm["row"].upper) == ("1.09", "0.65", "1.82")
    assert "open-location copy" in adm["source"] and "extract_trial" in adm["source"]
    # the admitted source names the copy the text came from (an Unpaywall copy was labelled 'PMC OA' before 7 Oct)
    v, adm = A.extractor_proposal({"slug": "sacubitril-valsartan-hfref", "pmid": "33731544"}, SACVAL,
                                  dict(held, text_origin="UNPAYWALL", doi="10.1253/circj.cj-20-0854"))
    assert v == "ADMITTED" and "Unpaywall copy DOI 10.1253/circj.cj-20-0854" in adm["source"]
    assert "PMC OA" not in adm["source"]
    # a quote the extractor cannot locate verbatim in the held text proposes nothing
    held2 = dict(held, text=PARALLEL.replace("HR 1.09", "HR\n1.09").replace(" ", "  "))
    assert A._sentence_of(held2["text"], "composite outcome of CV death") is not None   # whitespace-normalised


def test_printed_numbers_keep_their_printed_form():
    assert A._printed(0.7, "HR 0.70 (0.54-0.90)") == "0.70"
    assert A._printed(1.82, "0.65–1.82") == "1.82"
    assert A._printed(2.5, "HR 0.70") is None


def test_a_managed_challenge_page_is_a_challenge_not_a_plain_403():
    # ANZCTR (8 Oct): HTTP 403 with 'Managed Challenge / I'm Under Attack Mode' and no Cloudflare title
    page = b"<html><head><title>Oops</title></head><body>Managed Challenge / I'm Under Attack Mode - Enable JavaScript</body></html>"
    assert O.is_challenge(403, page)
