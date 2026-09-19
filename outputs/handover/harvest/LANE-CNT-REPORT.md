# LANE CNT report

## MEASURED

HEAD: `237e90946f5b257265b0a3b1c986a8907d12eded`. No commit, reset, checkout, or stash. Replays blocked socket connections; test execution used the existing offline guard. No network retrieval was performed.
Offline baseline and changed-code replay: 32 of 32 review cores and pages rebuilt from committed cache, with AACT_DIR=.tmp/empty_aact (existing empty directory). Output: `.tmp/cnt/docs/reviews/`; baseline: `.tmp/cnt-before/docs/reviews/`. Production docs/ was not rebuilt.
32 of 32 pages changed visible text; 32 of 32 pass the membership consumer check. Full old/new visible text blocks are recorded below (repeated occurrences retained).

### The original contradiction

`harness/grade.py::missing_family_count` read `outcomes[0].known_missing_sensitivity.rows`: FLOW, FREEDOM-CVO, and 26630143. `stale_heterogeneity` printed that set size (3), consumed by page, limitations, and manuscript. The outcome legend read `declared_absent_trials`, through identity.outcome_counts/count_phrase, yielding 1 (ELIXA, PMID 26630143; family NCT01147250). The known-missing panel combines concept-query signals with declared-absent rows; it is not itself a never-retrieved-only list.
The baseline page contains the STALE sentence 12 times and the “a further 1 trial family” sentence once. Their denominators differed and were unnamed.

### Resulting object

```json
{
  "pooled": [
    "PMID 31185157",
    "PMID 27633186",
    "PMID 27295427",
    "PMID 34215025",
    "PMID 31189511",
    "PMID 30291013",
    "PMID 28910237",
    "PMID 40162642"
  ],
  "declared_absent": [
    "PMID 26630143"
  ],
  "refused": [],
  "screened_in_not_pooled": [],
  "input_set_version": "cd88e2cb40b8dc9016438f5be9353d1722a8c75c680014ca971bc5dfabc50112",
  "sets": {
    "pooled": [
      "NCT01144338",
      "NCT01179048",
      "NCT01394952",
      "NCT01720446",
      "NCT02465515",
      "NCT02692716",
      "NCT03496298",
      "SOUL"
    ],
    "screened_in_not_poolable": [
      "NCT01147250"
    ],
    "eligible_not_retrieved": [
      "FLOW",
      "FREEDOM-CVO"
    ],
    "eligible_not_in_pool": [
      "FLOW",
      "FREEDOM-CVO",
      "NCT01147250"
    ]
  },
  "counts": {
    "pooled": 8,
    "screened_in_not_poolable": 1,
    "eligible_not_retrieved": 2,
    "eligible_not_in_pool": 3
  },
  "denominators": {
    "pooled": "outcome trial families with pooled rows",
    "screened_in_not_poolable": "screened-in trial families with declared-absent outcome rows",
    "eligible_not_retrieved": "known eligible outcome families outside pooled and screened-in absent sets",
    "eligible_not_in_pool": "union of screened_in_not_poolable and eligible_not_retrieved"
  }
}
```
All updated count sentences read this object. The STALE sentence consumer now lives in invalidation.py, leaving grade.py untouched as required. The limitations GRADE basis renderer replaces its legacy missing-count prose using the shared object. PRISMA reports the named union and its two subsets rather than subtracting pooled k from screening counts. Per-outcome HTML sections allow the consistency check to distinguish legitimate differences between outcomes.

### Plants, verbatim

```python
import copy
import json
import os
from pathlib import Path

import pytest

from harness import consumer_consistency as cc
from harness import membership
from harness.page import render_page

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'glp1-ra-mace-t2d'


def artifact_root():
    return ROOT / os.environ.get('CNT_DOCS', '.tmp/cnt/docs') / 'reviews'


def glp1_artifact():
    folder = artifact_root() / SLUG
    if folder.exists() or 'CNT_DOCS' in os.environ:
        return (json.loads((folder / 'review.json').read_text(encoding='utf-8')),
                (folder / 'index.html').read_text(encoding='utf-8'))
    from scripts.reproduce_review import replay_core
    review = replay_core(SLUG)
    return review, render_page(review)


def test_rendered_glp1_counts_resolve_to_one_object():
    review, page = glp1_artifact()
    cc.check_membership_counts(review, page)
    assert membership.membership_sentence(review['outcomes'][0]) in page


def test_mutated_membership_refuses():
    review, _ = glp1_artifact()
    outcome = review['outcomes'][0]
    membership.outcome_membership(outcome, review)
    bad = copy.deepcopy(review)
    bad['outcomes'][0]['membership']['sets']['eligible_not_in_pool'].append('PLANTED_DRIFT')
    with pytest.raises(ValueError, match='MEMBERSHIP_COUNT_MISMATCH'):
        render_page(bad)


def test_rendered_sentence_drift_refuses():
    outcome = {'primary': True, 'trials': [], 'declared_absent_trials': [{'id': 'PMID 12345678'}]}
    review = {'outcomes': [outcome]}
    text = membership.membership_sentence(outcome)
    with pytest.raises(ValueError, match='MEMBERSHIP_RENDER_MISMATCH'):
        cc.check_membership_counts(review, text + ' 2 eligible families not in the pool')


def test_aliases_and_family_deduplication():
    outcome = {'trials': [{'id': 'PMID 12345678', 'trial_family_id': 'NCT12345678'},
                          {'id': 'PMID 12345679', 'trial_family_id': 'NCT12345678'}],
               'declared_absent_trials': [{'id': 'PMID 22345678', 'trial_family_id': 'NCT22345678'}],
               'known_missing_sensitivity': {'rows': [{'trial_key': '22345678'}, {'trial_key': 'FLOW'}]}}
    counts = membership.build_outcome_membership(outcome)['counts']
    assert counts == {'pooled': 1, 'screened_in_not_poolable': 1,
                      'eligible_not_retrieved': 1, 'eligible_not_in_pool': 2}


def test_all_rebuilt_pages_browser_contract():
    import functools
    import http.server
    import socket
    import threading
    pytest.importorskip('playwright')
    from playwright.sync_api import sync_playwright
    candidates = [Path(os.environ.get('PROGRAMFILES(X86)', '')) / 'Microsoft/Edge/Application/msedge.exe',
                  Path(os.environ.get('PROGRAMFILES', '')) / 'Google/Chrome/Application/chrome.exe']
    executable = next((p for p in candidates if p.is_file()), None)
    if executable is None:
        pytest.skip('No installed browser; downloads prohibited')
    paths = sorted(artifact_root().glob('*/review.json'))
    if not paths:
        pytest.skip('Run offline CNT rebuild before corpus browser check')
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 8000),
        functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(artifact_root().parent)),
        bind_and_activate=False)
    server.allow_reuse_address = False
    if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
        server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    server.server_bind()
    server.server_activate()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=str(executable), headless=True)
            try:
                page = browser.new_page()
                page.route('**/*', lambda route: route.continue_()
                           if route.request.url.startswith('http://127.0.0.1:8000/') else route.abort())
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                for path in paths:
                    assert page.goto(f'http://127.0.0.1:8000/reviews/{path.parent.name}/index.html').status == 200
                    review = json.loads(path.read_text(encoding='utf-8'))
                    check = page.content()
                    cc.check_membership_counts(review, check)
                    assert page.locator('nav button').count() > 0
                assert not errors
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()

```
```text
PRE: MEMBERSHIP_RENDER_AMBIGUOUS: further trial family count has no named set
POST: PASS
MUTATION: MEMBERSHIP_COUNT_MISMATCH: 3-point major adverse cardiovascular events sets disagree with rows
```
Pre-fix plant: the focused rendered-page test fails against baseline pages (see pre-plant.txt); the refusal is the unqualified “further 1 trial family” beside the 3-family union. Post-fix: the page passes; a scratch mutation of the union sets refuses in render_page before emitting a page. No source records or source values were mutated.

### Verification

Targeted command: `python -X utf8 -m pytest tests/test_membership_counts_single_source.py tests/test_consumer_consistency*.py -q` (the wildcard resolves to test_consumer_consistency.py). Full-suite commands: `python -X utf8 -m pytest -q`, then `python -X utf8 -m pytest tests -q` after the existing duplicate-module collection error. Targeted browser validation serves the rebuilt corpus at http://127.0.0.1:8000 with external requests blocked.

`.tmp/cnt/pre-plant.txt`:
```text
F                                                                        [100%]
================================== FAILURES ===================================
_______________ test_rendered_glp1_counts_resolve_to_one_object _______________

    def test_rendered_glp1_counts_resolve_to_one_object():
        review, page = glp1_artifact()
>       cc.check_membership_counts(review, page)

tests\test_membership_counts_single_source.py:32: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

review = {'arm_contrast': {'metric_label': 'parser-confirmed contrast', 'metric_scope': 'AACT arm-label parser output; this mea...supplied by lane adjudication; complete citation not held)', 'document_ref': None, 'document_sha256': None, ...}], ...}
rendered = "<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=...===id)});}\n(function(){var f=document.querySelector('nav button');if(f)show(f.dataset.t);})();</script></body></html>"
outcome = None

    def check_membership_counts(review, rendered=None, outcome=None):
        """Fail closed on row/set drift and on conflicting named rendered counts."""
        from html import unescape
        from .membership import _family_sets, outcome_membership
        outcomes = [outcome] if outcome is not None else review.get("outcomes") or []
        for item in outcomes:
            member = outcome_membership(item, review)
            expected = _family_sets(item)
            for field in ("sets", "counts", "denominators"):
                if member.get(field) != expected[field]:
                    raise ValueError(f"MEMBERSHIP_COUNT_MISMATCH: {item.get('name')} {field} disagree with rows")
        if rendered is None:
            return
        if outcome is None:
            by_name = {o.get("name"): o for o in outcomes}
            def check_block(match):
                name = unescape(match.group(1))
                if name not in by_name:
                    raise ValueError("MEMBERSHIP_RENDER_UNKNOWN_OUTCOME: " + name)
                check_membership_counts(review, match.group(2), by_name[name])
                return ""
            rendered = re.sub(r'<section data-membership-outcome="([^"]*)">(.*?)</section>',
                              check_block, rendered, flags=re.S)
        item = outcome if outcome is not None else next((o for o in outcomes if o.get("primary")), {})
        counts = outcome_membership(item, review)["counts"]
        text = unescape(re.sub(r"<[^>]*>", " ", rendered))
        patterns = {"eligible_not_in_pool": r"(\d+) eligible families not in the pool",
                    "screened_in_not_poolable": r"(\d+) screened-in with no poolable value",
                    "eligible_not_retrieved": r"(\d+) known eligible but not retrieved"}
        for name, pattern in patterns.items():
            values = [int(n) for n in re.findall(pattern, text)]
            if any(n != counts[name] for n in values):
                raise ValueError(f"MEMBERSHIP_RENDER_MISMATCH: {name}: {values} vs {counts[name]}")
        if re.search(r"further\s+\d+\s+trial famil", text):
>           raise ValueError("MEMBERSHIP_RENDER_AMBIGUOUS: further trial family count has no named set")
E           ValueError: MEMBERSHIP_RENDER_AMBIGUOUS: further trial family count has no named set

harness\consumer_consistency.py:661: ValueError
=========================== short test summary info ===========================
FAILED tests/test_membership_counts_single_source.py::test_rendered_glp1_counts_resolve_to_one_object
1 failed, 4 deselected in 15.62s

```
`.tmp/cnt/targeted.txt`:
```text
...........                                                              [100%]
11 passed in 69.57s (0:01:09)

```
`.tmp/cnt/full-suite.txt`:
```text

=================================== ERRORS ====================================
_______________ ERROR collecting tests/test_search_v2_isrctn.py _______________
import file mismatch:
imported module 'test_search_v2_isrctn' has this __file__ attribute:
  C:\mh-w-CNT\outputs\search_v2\lanes\R2\test_search_v2_isrctn.py
which is not the same as the test file we want to collect:
  C:\mh-w-CNT\tests\test_search_v2_isrctn.py
HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules
=========================== short test summary info ===========================
ERROR tests/test_search_v2_isrctn.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 56.85s

```
`.tmp/cnt/full-tests.txt`:
```text
F..........................................................F.......F.... [  7%]
........................................................................ [ 14%]
........................................................................ [ 22%]
........................................................................ [ 29%]
............................F...........................FF.............. [ 36%]
................................................F....................... [ 44%]
........................................................................ [ 51%]
........................................................................ [ 58%]
.............................F.......................................... [ 66%]
..F..................................................................... [ 73%]
........................................................................ [ 80%]
........................................................................ [ 88%]
........................................................................ [ 95%]
..........................................                               [100%]
================================== FAILURES ===================================
_________________ test_replay_with_snapshot_access_forbidden __________________

monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001F7B5DC9E00>

    def test_replay_with_snapshot_access_forbidden(monkeypatch):
        forbid_snapshot(monkeypatch)
        ok, reasons = reproduce(SLUG)
>       assert ok, reasons
E       AssertionError: ['review_sha256 mismatch: replay b8f704b45b9c41acd11369402ce3fb854302d4e5f5f584188b46c80a6b8a75f8 vs committed bc9c2fc...0b77e4ee7423b6c23b5ed2756cf261cc1bf272049', 'served index.html does not byte-match a re-render from the replayed core']
E       assert False

tests\test_aact_cache.py:22: AssertionError
__________________ test_held_document_byte_mutation_refuses ___________________

tmp_path = WindowsPath('C:/mh-w-CNT/.tmp/pytest-of-mahmo/pytest-0/test_held_document_byte_mutati0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001F7B5830590>

    def test_held_document_byte_mutation_refuses(tmp_path, monkeypatch):
        # Copy held inputs only; the statistical replay continues using its unchanged cache.
        for folder in ("cache/" + SLUG, "topics", "protocols", "harness", "scripts",
                       "outputs/handover/glp1_regulatory"):
            shutil.copytree(ROOT / folder, tmp_path / folder)
        held = next((tmp_path / "outputs/handover/glp1_regulatory").rglob("*.txt"))
        before = held.read_bytes()
        held.write_bytes(bytes([before[0] ^ 1]) + before[1:])
        try:
            certificate = importlib.import_module("harness.certificate")
        except ModuleNotFoundError:
            certificate = None
        if certificate:
            monkeypatch.setattr(certificate, "ROOT", tmp_path)
            review = json.loads((ROOT / "docs/reviews" / SLUG / "review.json").read_text(encoding="utf-8"))
            saved = review["reproduction"]["certificate"]
            changed = certificate.compute(SLUG, review, saved["protocol_sha"])
            assert changed["release_sha256"] != saved["release_sha256"]
>           assert {k for k in saved if saved[k] != changed[k]} == {"held_documents", "release_sha256"}
E           AssertionError: assert {'held_docume...eview_sha256'} == {'held_docume...lease_sha256'}
E             
E             Extra items in the left set:
E             'review_sha256'
E             'manuscript_sha256'
E             Use -v to get more diff

tests\test_certificate.py:33: AssertionError
______________ test_all_certificate_inputs_and_manuscript_match _______________

    def test_all_certificate_inputs_and_manuscript_match():
        from harness import certificate, manuscript
        from harness.canonical import canonical_json, sha256_text
        for directory in sorted((ROOT / "docs/reviews").iterdir()):
            cert = json.loads((directory / "CERTIFICATE.json").read_text(encoding="utf-8"))
            review = json.loads((directory / "review.json").read_text(encoding="utf-8"))
>           assert not certificate.verify(directory)
E           AssertionError: assert not ['CERTIFICATE.json release_sha256 mismatch: recomputed c51b7d14b3175a4e98b5ebd5b5bc39cd250cc7fec0d24d1d67f06f12e6b6ef82 vs saved 1fc4bb496a9ec2aeb2c5a2afab157a6bac7e02b0db3c64fc13f526f071a2ba67']
E            +  where ['CERTIFICATE.json release_sha256 mismatch: recomputed c51b7d14b3175a4e98b5ebd5b5bc39cd250cc7fec0d24d1d67f06f12e6b6ef82 vs saved 1fc4bb496a9ec2aeb2c5a2afab157a6bac7e02b0db3c64fc13f526f071a2ba67'] = <function verify at 0x000001F7B5E811C0>(WindowsPath('C:/mh-w-CNT/docs/reviews/balanced-crystalloids-vs-saline-mortality'))
E            +    where <function verify at 0x000001F7B5E811C0> = <module 'harness.certificate' from 'C:\\mh-w-CNT\\harness\\certificate.py'>.verify

tests\test_certificate.py:103: AssertionError
__________________________ test_real_store_validates __________________________

    def test_real_store_validates() -> None:
        ok, reasons = fixstate.check(ROOT)
    
>       assert ok, "\n".join(reasons)
E       AssertionError: docs/fix_ledger.json is stale; run python scripts/render_fix_ledger.py
E       assert False

tests\test_fixstate.py:457: AssertionError
___________________ test_valid_page_passes_non_replay_limbs ___________________

    def test_valid_page_passes_non_replay_limbs():
        # The synthetic fixture has no committed topic/cache, so the Level-B replay limb cannot
        # run against it (correctly: a page with no reproducible pipeline is not publishable).
        # Here we assert the fixture satisfies every OTHER limb; full reproduction is tested
        # against a real committed review below.
        from harness.gate import check_limb1, check_limb2, check_primary_result, _load
        with tempfile.TemporaryDirectory() as tmp:
            d = _build(tmp)
            manifest, html, rep = _load(d)
            reasons = (check_limb1(d, manifest, html, rep)
                       + check_primary_result(d) + check_limb2(manifest, html))
>           assert not reasons, f"valid page should pass non-replay limbs, got: {reasons}"
E           AssertionError: valid page should pass non-replay limbs, got: ['L1: live census reproduced 1 failure(s): review_sha256 reproduces from committed review.json']
E           assert not ['L1: live census reproduced 1 failure(s): review_sha256 reproduces from committed review.json']

tests\test_gate.py:98: AssertionError
______________ test_real_review_reproduces_and_passes_full_gate _______________

    def test_real_review_reproduces_and_passes_full_gate():
        # A real committed page must pass the WHOLE gate including Level-B replay (the pipeline
        # re-run from committed cache regenerates the committed numbers). Skips only if run
        # outside the repo (no docs/reviews present).
        import os as _os
        root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
        d = _os.path.join(root, "docs", "reviews", "noac-vs-warfarin-af-stroke")
        if not _os.path.isdir(d):
            return
        ok, reasons = gate_page(d)
>       assert ok, f"real committed review must pass the full gate, got: {reasons}"
E       AssertionError: real committed review must pass the full gate, got: ['L1: live census reproduced 1 failure(s): served index.html byte-matches re-render of review.json', 'CERTIFICATE.json release_sha256 mismatch: recomputed e98a365a936327b8d2d1f7718388433f581d428e57ade0d838832a0900508d0c vs saved 838a39d427d7f1048813605bed6877ca02f74b4ce074e855474c20d32a6379dc', 'L1: offline replay does NOT regenerate the committed numbers (replay 756ccf5cc54bf2d8c2a6d84b6ddef62d99238a1536b990ead4dea0a18bead917 vs committed 91da662722bdb1f494cfe525adaf5ce7b0f27e7fc99e7370ea84d973e98da806)']
E       assert False

tests\test_gate.py:111: AssertionError
_____________ test_acknowledgement_renders_from_limitation_object _____________

    def test_acknowledgement_renders_from_limitation_object():
        obj = _uoa_obj()
        obj["unwired"] = True
        obj["unwired_acknowledged"] = {
            "signed_by": "test signer",
            "date": "2026-09-15",
            "reason": "plant acknowledgement",
            "tranche": "TRANCHE-hazard-consumers",
        }
>       html = render_page(
            {
                "slug": "plant",
                "title": "Plant",
                "question": "Plant?",
                "limitations": [obj],
                "outcomes": [{"primary": True, "result": {"present": False, "reason": "none"}}],
            }
        )

tests\test_hazard_consumers.py:90: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
harness\page.py:2732: in render_page
    ???
harness\consumer_consistency.py:648: in check_membership_counts
    rendered = re.sub(r'<section data-membership-outcome="([^"]*)">(.*?)</section>',
C:\Users\mahmo\AppData\Local\Programs\Python\Python313\Lib\re\__init__.py:208: in sub
    return _compile(pattern, flags).sub(repl, string, count)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

match = <re.Match object; span=(4524, 4691), match='<section data-membership-outcome=""><div data-pri>

    def check_block(match):
        name = unescape(match.group(1))
        if name not in by_name:
>           raise ValueError("MEMBERSHIP_RENDER_UNKNOWN_OUTCOME: " + name)
E           ValueError: MEMBERSHIP_RENDER_UNKNOWN_OUTCOME:

harness\consumer_consistency.py:645: ValueError
__ test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews __

    def test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews():
        rows = []
        for review_dir in _review_dirs():
            review = json.loads((review_dir / "review.json").read_text(encoding="utf-8"))
            assert "limitations" in review, review["slug"]
            page_texts = _page_limitation_block_texts(review)
            object_texts = _limitation_block_texts(review)
            rows.append((review["slug"], sum(page_texts.values()), sum(object_texts.values())))
            if object_texts == page_texts:
                continue
            stale_codes = {v["code"] for v in claimgraph.check(review)}
            extra_objects = object_texts - page_texts
            extra_pages = page_texts - object_texts
>           assert not review.get("claimgraph"), review["slug"]
E           AssertionError: balanced-crystalloids-vs-saline-mortality
E           assert not {'objects': [{'claim_id': 'a29165ecd31799dd', 'depends_on': {'input_set_version': 'b6c7145842a2d8ea1b8c83b26799692a4bb..._version': 'b6c7145842a2d8ea1b8c83b26799692a4bb8428a12358195beba01e4cb46a9d2'}, 'kind': 'manuscript_result_sentence'}]}
E            +  where {'objects': [{'claim_id': 'a29165ecd31799dd', 'depends_on': {'input_set_version': 'b6c7145842a2d8ea1b8c83b26799692a4bb..._version': 'b6c7145842a2d8ea1b8c83b26799692a4bb8428a12358195beba01e4cb46a9d2'}, 'kind': 'manuscript_result_sentence'}]} = <built-in method get of dict object at 0x000001F7B61E2D40>('claimgraph')
E            +    where <built-in method get of dict object at 0x000001F7B61E2D40> = {'arm_contrast': {'current_pooled_trial_ids': ['34375394', '35041780'], 'metric_label': 'parser-confirmed contrast', '...rator_fulltext.txt', 'document_sha256': 'd49ee735ce7d94b2da0ec89ffcf30dfde140b9064408882040266f290b84aa54', ...}], ...}.get

tests\test_limitations_legacy_compare.py:49: AssertionError
______________ test_reconciliation_when_included_exceeds_pooled _______________

    def test_reconciliation_when_included_exceeds_pooled():
        # 2 pooled + 1 declared-absent = 3 included; the gap must be stated on the page
        r = _review(2, [{"label": "A", "id": "PMID 1", "ai": 1, "n1i": 10, "ci": 2, "n2i": 10},
                        {"label": "B", "id": "PMID 2", "ai": 1, "n1i": 10, "ci": 2, "n2i": 10}],
                    [{"label": "C", "id": "PMID 3", "reason": "no poolable value in abstract"}])
        html = render_page(r)
        assert "Screened-in → pooled" in html
        assert "3 trials met P/I/C/design" in html
>       assert "the remaining 1" in html
E       assert 'the remaining 1' in "<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=...===id)});}\n(function(){var f=document.querySelector('nav button');if(f)show(f.dataset.t);})();</script></body></html>"

tests\test_page.py:87: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_aact_cache.py::test_replay_with_snapshot_access_forbidden
FAILED tests/test_certificate.py::test_held_document_byte_mutation_refuses - ...
FAILED tests/test_certificate.py::test_all_certificate_inputs_and_manuscript_match
FAILED tests/test_fixstate.py::test_real_store_validates - AssertionError: do...
FAILED tests/test_gate.py::test_valid_page_passes_non_replay_limbs - Assertio...
FAILED tests/test_gate.py::test_real_review_reproduces_and_passes_full_gate
FAILED tests/test_hazard_consumers.py::test_acknowledgement_renders_from_limitation_object
FAILED tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews
FAILED tests/test_page.py::test_reconciliation_when_included_exceeds_pooled
9 failed, 969 passed in 1073.87s (0:17:53)

```
`.tmp/cnt/source-review.txt`:
```text
32 of 32: source trial rows, declared-absent rows, statistical results and known-missing panels match baseline. Differences: []
```
`.tmp/cnt/current-render.txt`:
```text
32 of 32 current-code renders exactly match rebuilt pages; git diff --check PASS.
```
`.tmp/cnt/compatibility-rerun.txt`:
```text
.............                                                            [100%]
13 passed in 15.84s

```
`.tmp/cnt/failures-rerun.txt`:
```text
FFFF.F.F.                                                                [100%]
================================== FAILURES ===================================
_________________ test_replay_with_snapshot_access_forbidden __________________

monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001DEAABA9220>

    def test_replay_with_snapshot_access_forbidden(monkeypatch):
        forbid_snapshot(monkeypatch)
        ok, reasons = reproduce(SLUG)
>       assert ok, reasons
E       AssertionError: ['review_sha256 mismatch: replay b8f704b45b9c41acd11369402ce3fb854302d4e5f5f584188b46c80a6b8a75f8 vs committed bc9c2fc...0b77e4ee7423b6c23b5ed2756cf261cc1bf272049', 'served index.html does not byte-match a re-render from the replayed core']
E       assert False

tests\test_aact_cache.py:22: AssertionError
__________________ test_held_document_byte_mutation_refuses ___________________

tmp_path = WindowsPath('C:/mh-w-CNT/.tmp/pytest-of-mahmo/pytest-1/test_held_document_byte_mutati0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001DE98FC4510>

    def test_held_document_byte_mutation_refuses(tmp_path, monkeypatch):
        # Copy held inputs only; the statistical replay continues using its unchanged cache.
        for folder in ("cache/" + SLUG, "topics", "protocols", "harness", "scripts",
                       "outputs/handover/glp1_regulatory"):
            shutil.copytree(ROOT / folder, tmp_path / folder)
        held = next((tmp_path / "outputs/handover/glp1_regulatory").rglob("*.txt"))
        before = held.read_bytes()
        held.write_bytes(bytes([before[0] ^ 1]) + before[1:])
        try:
            certificate = importlib.import_module("harness.certificate")
        except ModuleNotFoundError:
            certificate = None
        if certificate:
            monkeypatch.setattr(certificate, "ROOT", tmp_path)
            review = json.loads((ROOT / "docs/reviews" / SLUG / "review.json").read_text(encoding="utf-8"))
            saved = review["reproduction"]["certificate"]
            changed = certificate.compute(SLUG, review, saved["protocol_sha"])
            assert changed["release_sha256"] != saved["release_sha256"]
>           assert {k for k in saved if saved[k] != changed[k]} == {"held_documents", "release_sha256"}
E           AssertionError: assert {'held_docume...lease_sha256'} == {'held_docume...lease_sha256'}
E             
E             Extra items in the left set:
E             'manuscript_sha256'
E             Use -v to get more diff

tests\test_certificate.py:33: AssertionError
______________ test_all_certificate_inputs_and_manuscript_match _______________

    def test_all_certificate_inputs_and_manuscript_match():
        from harness import certificate, manuscript
        from harness.canonical import canonical_json, sha256_text
        for directory in sorted((ROOT / "docs/reviews").iterdir()):
            cert = json.loads((directory / "CERTIFICATE.json").read_text(encoding="utf-8"))
            review = json.loads((directory / "review.json").read_text(encoding="utf-8"))
>           assert not certificate.verify(directory)
E           AssertionError: assert not ['CERTIFICATE.json release_sha256 mismatch: recomputed 5639ccae47cc6ebe8c75be05e4721bd7cfe276738c08afec9d12b014deb1b38a vs saved 1fc4bb496a9ec2aeb2c5a2afab157a6bac7e02b0db3c64fc13f526f071a2ba67']
E            +  where ['CERTIFICATE.json release_sha256 mismatch: recomputed 5639ccae47cc6ebe8c75be05e4721bd7cfe276738c08afec9d12b014deb1b38a vs saved 1fc4bb496a9ec2aeb2c5a2afab157a6bac7e02b0db3c64fc13f526f071a2ba67'] = <function verify at 0x000001DEAABEC5E0>(WindowsPath('C:/mh-w-CNT/docs/reviews/balanced-crystalloids-vs-saline-mortality'))
E            +    where <function verify at 0x000001DEAABEC5E0> = <module 'harness.certificate' from 'C:\\mh-w-CNT\\harness\\certificate.py'>.verify

tests\test_certificate.py:103: AssertionError
__________________________ test_real_store_validates __________________________

    def test_real_store_validates() -> None:
        ok, reasons = fixstate.check(ROOT)
    
>       assert ok, "\n".join(reasons)
E       AssertionError: docs/fix_ledger.json is stale; run python scripts/render_fix_ledger.py
E       assert False

tests\test_fixstate.py:457: AssertionError
______________ test_real_review_reproduces_and_passes_full_gate _______________

    def test_real_review_reproduces_and_passes_full_gate():
        # A real committed page must pass the WHOLE gate including Level-B replay (the pipeline
        # re-run from committed cache regenerates the committed numbers). Skips only if run
        # outside the repo (no docs/reviews present).
        import os as _os
        root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
        d = _os.path.join(root, "docs", "reviews", "noac-vs-warfarin-af-stroke")
        if not _os.path.isdir(d):
            return
        ok, reasons = gate_page(d)
>       assert ok, f"real committed review must pass the full gate, got: {reasons}"
E       AssertionError: real committed review must pass the full gate, got: ['L1: live census reproduced 1 failure(s): served index.html byte-matches re-render of review.json', 'CERTIFICATE.json release_sha256 mismatch: recomputed a658b31fc9a5586bbc785d0f82a5ba61c66525d2c7866dcfc9d7055696d58491 vs saved 838a39d427d7f1048813605bed6877ca02f74b4ce074e855474c20d32a6379dc', 'L1: offline replay does NOT regenerate the committed numbers (replay 756ccf5cc54bf2d8c2a6d84b6ddef62d99238a1536b990ead4dea0a18bead917 vs committed 91da662722bdb1f494cfe525adaf5ce7b0f27e7fc99e7370ea84d973e98da806)']
E       assert False

tests\test_gate.py:111: AssertionError
__ test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews __

    def test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews():
        rows = []
        for review_dir in _review_dirs():
            review = json.loads((review_dir / "review.json").read_text(encoding="utf-8"))
            assert "limitations" in review, review["slug"]
            page_texts = _page_limitation_block_texts(review)
            object_texts = _limitation_block_texts(review)
            rows.append((review["slug"], sum(page_texts.values()), sum(object_texts.values())))
            if object_texts == page_texts:
                continue
            stale_codes = {v["code"] for v in claimgraph.check(review)}
            extra_objects = object_texts - page_texts
            extra_pages = page_texts - object_texts
>           assert not review.get("claimgraph"), review["slug"]
E           AssertionError: balanced-crystalloids-vs-saline-mortality
E           assert not {'objects': [{'claim_id': 'a29165ecd31799dd', 'depends_on': {'input_set_version': 'b6c7145842a2d8ea1b8c83b26799692a4bb..._version': 'b6c7145842a2d8ea1b8c83b26799692a4bb8428a12358195beba01e4cb46a9d2'}, 'kind': 'manuscript_result_sentence'}]}
E            +  where {'objects': [{'claim_id': 'a29165ecd31799dd', 'depends_on': {'input_set_version': 'b6c7145842a2d8ea1b8c83b26799692a4bb..._version': 'b6c7145842a2d8ea1b8c83b26799692a4bb8428a12358195beba01e4cb46a9d2'}, 'kind': 'manuscript_result_sentence'}]} = <built-in method get of dict object at 0x000001DEAAC91740>('claimgraph')
E            +    where <built-in method get of dict object at 0x000001DEAAC91740> = {'arm_contrast': {'current_pooled_trial_ids': ['34375394', '35041780'], 'metric_label': 'parser-confirmed contrast', '...rator_fulltext.txt', 'document_sha256': 'd49ee735ce7d94b2da0ec89ffcf30dfde140b9064408882040266f290b84aa54', ...}], ...}.get

tests\test_limitations_legacy_compare.py:49: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_aact_cache.py::test_replay_with_snapshot_access_forbidden
FAILED tests/test_certificate.py::test_held_document_byte_mutation_refuses - ...
FAILED tests/test_certificate.py::test_all_certificate_inputs_and_manuscript_match
FAILED tests/test_fixstate.py::test_real_store_validates - AssertionError: do...
FAILED tests/test_gate.py::test_real_review_reproduces_and_passes_full_gate
FAILED tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews
6 failed, 3 passed in 205.69s (0:03:25)

```

## Remaining full-suite blockers

Full tests/ run: 969 passed, 9 failed in 1073.87s. After compatibility repairs, all nine failures were rerun: 3 passed, 6 failed in 205.69s. The remaining checks compare changed renderers/core hashes with untouched production docs, certificates, the saved limitations, or fix ledger. They are NOT reported as passing or all pre-existing. Production baselines were intentionally not regenerated: LANE_PROMPT.md requires output under .tmp/cnt/docs only. See STUCK_FAILURES.md and the exact failure logs above. Final targeted run: 11 of 11 passed; compatibility run: 13 of 13 passed. No full-suite green claim is made.

## INFERRED / limitations

The stored GLP-1 split is source-backed by the held rows: ELIXA is screened-in/not-poolable, while FLOW and FREEDOM-CVO have no committed-source reference and the known-missing rows explicitly say they are absent from the topic cache. No online eligibility verification was performed. Other topics retain their pre-existing known-missing candidate identities, including audit labels; this lane makes their denominators consistent, not a new eligibility or family-identity adjudication. No TF ledger landed in this worktree; generic sets/denominators are a view over existing outcome rows, ready to consume a future ledger.

## CLAIMED / scope

Shared outcome membership now owns the rendered missing-family counts. Row/set/count disagreement and conflicting rendered counts cause ValueError in the page build. This is a local repair, not a release, certification, or claim that the research search is complete.

| Item | Static or dynamic | Source / validation |
|---|---|---|
| Set names, denominator prose | Static schema | membership.py |
| Members and counts | Dynamic | pooled/declared-absent/known-missing rows; consistency check |
| Alias resolution | Dynamic | IDs, labels, trial_family_id on held outcome rows |
| Effect estimates and study dates | Existing inputs, unchanged | No numerical synthesis edits |
| Test mutation | Deliberate scratch plant | Never added to output data |

## Changed pages and old/new text

- balanced-crystalloids-vs-saline-mortality
- colchicine-postop-af
- colchicine-recurrent-pericarditis
- colchicine-secondary-cv-prevention
- corticosteroids-cap-mortality
- corticosteroids-covid19-mortality
- dapagliflozin-hfpef-hosp
- denosumab-vertebral-fracture
- doac-vte-recurrence
- dpp4-mace-t2d
- empagliflozin-hfpef-hosp
- esketamine-trd-madrs
- finerenone-ckd-t2d-renal
- glp1-ra-mace-t2d
- iv-iron-hfref-hosp
- melatonin-primary-insomnia-sol
- metformin-pcos-ovulation
- noac-vs-warfarin-af-stroke
- omega3-cardiovascular-events
- pcsk9-mace
- probiotics-aad-prevention
- sacubitril-valsartan-hfref
- semaglutide-obesity-mace
- semaglutide-obesity-weight
- sglt2-ckd-progression
- sglt2-hfref-hosp-cvdeath
- sglt2-primary-prevention-hf
- spironolactone-hfref-mortality
- statins-primary-prevention-elderly
- ticagrelor-vs-clopidogrel-acs
- tocilizumab-covid19-mortality
- tranexamic-acid-pph

### balanced-crystalloids-vs-saline-mortality
OLD:
```text
Screened-in → pooled 7 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 2 reported this outcome with an extractable number and were pooled; the remaining 5 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 7 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 2 reported this outcome with an extractable number and were pooled; 5 eligible families not in the pool: the remaining 5 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Between-study τ² 0 STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Between-study τ² 0 STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible with outcome retrieved but refused (engine cannot consume design variance) 3 trial families
Eligible but outcome not extracted from the abstract (full-text pass pending) 5 trial families
```
NEW:
```text
Primary outcome membership 5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved
```
OLD:
```text
τ² 0 STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 0.0% STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
τ² 0 STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 0.0% STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 2: the 2 trial(s) named below were pooled; a further 5 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 2: the 2 trial(s) named below were pooled; 5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. Pooling 2 trials retained the point estimate (HR 0.98), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 5 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. Pooling 2 trials retained the point estimate (HR 0.98), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Pooling 2 trials retained the point estimate (HR 0.98), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Pooling 2 trials retained the point estimate (HR 0.98), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### colchicine-postop-af
OLD:
```text
Screened-in → pooled 6 trial families met P/I/C/design (screening); 3 reported this outcome with an extractable number and were pooled; the remaining 3 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 6 trial families met P/I/C/design (screening); 3 reported this outcome with an extractable number and were pooled; 4 eligible families not in the pool: the remaining 3 screened-in with no poolable value, 1 known eligible but not retrieved.
```
OLD:
```text
Prediction interval 0.09–4.85 STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 0.147 STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.09–4.85 STALE: pooled membership known incomplete (4 eligible families not in the pool: 3 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 0.147 STALE: pooled membership known incomplete (4 eligible families not in the pool: 3 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (4 eligible families not in the pool: 3 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 3 trial families
```
NEW:
```text
Primary outcome membership 4 eligible families not in the pool: 3 screened-in with no poolable value, 1 known eligible but not retrieved
```
OLD:
```text
Prediction interval 0.09–4.85 STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 0.147 STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 68.2% STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.09–4.85 STALE: pooled membership known incomplete (4 eligible families not in the pool: 3 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 0.147 STALE: pooled membership known incomplete (4 eligible families not in the pool: 3 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 68.2% STALE: pooled membership known incomplete (4 eligible families not in the pool: 3 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (4 eligible families not in the pool: 3 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 3: the 3 trial(s) named below were pooled; a further 3 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 3: the 3 trial(s) named below were pooled; 4 eligible families not in the pool: 3 screened-in with no poolable value, 1 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (4 eligible families not in the pool: 3 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. Pooling 3 trials gave RR 0.65 (95% CI 0.21 to 2.05), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.09 to 4.85. STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 3 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. Pooling 3 trials gave RR 0.65 (95% CI 0.21 to 2.05), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.09 to 4.85. STALE: pooled membership known incomplete (4 eligible families not in the pool: 3 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 4 eligible families not in the pool: 3 screened-in with no poolable value, 1 known eligible but not retrieved.
```
OLD:
```text
Pooling 3 trials gave RR 0.65 (95% CI 0.21 to 2.05), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.09 to 4.85. STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Pooling 3 trials gave RR 0.65 (95% CI 0.21 to 2.05), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.09 to 4.85. STALE: pooled membership known incomplete (4 eligible families not in the pool: 3 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.; pooled trials differ on follow_up_window: 14 days / postoperative admission, 3 months, in-hospital / until discharge; pooled trials differ on analysis_set: AVAILABLE_CASE, not_stated; pooled trials differ on endpoint_definition: {'duration_threshold': '>=30 seconds', 'surveillance_window': '1- and 3-month visits'}, {'duration_threshold': '>=5 minutes', 'surveillance_window': 'until hospital discharge'}, {'duration_threshold': 'not_stated', 'surveillance_window': '14-day regimen / analysed population'}. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (4 eligible families not in the pool: 3 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.; pooled trials differ on follow_up_window: 14 days / postoperative admission, 3 months, in-hospital / until discharge; pooled trials differ on analysis_set: AVAILABLE_CASE, not_stated; pooled trials differ on endpoint_definition: {'duration_threshold': '>=30 seconds', 'surveillance_window': '1- and 3-month visits'}, {'duration_threshold': '>=5 minutes', 'surveillance_window': 'until hospital discharge'}, {'duration_threshold': 'not_stated', 'surveillance_window': '14-day regimen / analysed population'}. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (4 eligible families not in the pool: 3 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### colchicine-recurrent-pericarditis
OLD:
```text
Screened-in → pooled 3 trial families met P/I/C/design (screening); 2 reported this outcome with an extractable number and were pooled; the remaining 1 trial family are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 3 trial families met P/I/C/design (screening); 2 reported this outcome with an extractable number and were pooled; 2 eligible families not in the pool: the remaining 1 screened-in with no poolable value, 1 known eligible but not retrieved.
```
OLD:
```text
Between-study τ² 0 STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Between-study τ² 0 STALE: pooled membership known incomplete (2 eligible families not in the pool: 1 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (2 eligible families not in the pool: 1 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 1 trial family
```
NEW:
```text
Primary outcome membership 2 eligible families not in the pool: 1 screened-in with no poolable value, 1 known eligible but not retrieved
```
OLD:
```text
τ² 0 STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 0.0% STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
τ² 0 STALE: pooled membership known incomplete (2 eligible families not in the pool: 1 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 0.0% STALE: pooled membership known incomplete (2 eligible families not in the pool: 1 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (2 eligible families not in the pool: 1 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 2: the 2 trial(s) named below were pooled; a further 1 trial family had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 2: the 2 trial(s) named below were pooled; 2 eligible families not in the pool: 1 screened-in with no poolable value, 1 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
k = 1: the 1 trial(s) named below were pooled; a further 2 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 1: the 1 trial(s) named below were pooled; 2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (2 eligible families not in the pool: 1 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. Pooling 2 trials retained the point estimate (RR 0.46), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 1 trial family were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. Pooling 2 trials retained the point estimate (RR 0.46), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (2 eligible families not in the pool: 1 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 2 eligible families not in the pool: 1 screened-in with no poolable value, 1 known eligible but not retrieved.
```
OLD:
```text
Pooling 2 trials retained the point estimate (RR 0.46), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Pooling 2 trials retained the point estimate (RR 0.46), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (2 eligible families not in the pool: 1 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.; pooled trials differ on prior disease stage: first_recurrence, multiple_recurrences. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (2 eligible families not in the pool: 1 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.; pooled trials differ on prior disease stage: first_recurrence, multiple_recurrences. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (2 eligible families not in the pool: 1 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### colchicine-secondary-cv-prevention
OLD:
```text
Screened-in → pooled 25 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 3 reported this outcome with an extractable number and were pooled; the remaining 22 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 25 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 3 reported this outcome with an extractable number and were pooled; 22 eligible families not in the pool: the remaining 22 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Prediction interval 0.35–1.9 STALE: pooled membership known incomplete (22 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 0.0267 STALE: pooled membership known incomplete (22 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (22 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.35–1.9 STALE: pooled membership known incomplete (22 eligible families not in the pool: 22 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 0.0267 STALE: pooled membership known incomplete (22 eligible families not in the pool: 22 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (22 eligible families not in the pool: 22 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 22 trial families
```
NEW:
```text
Primary outcome membership 22 eligible families not in the pool: 22 screened-in with no poolable value, 0 known eligible but not retrieved
```
OLD:
```text
Prediction interval 0.35–1.9 STALE: pooled membership known incomplete (22 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 0.0267 STALE: pooled membership known incomplete (22 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 77.9% STALE: pooled membership known incomplete (22 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (22 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.35–1.9 STALE: pooled membership known incomplete (22 eligible families not in the pool: 22 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 0.0267 STALE: pooled membership known incomplete (22 eligible families not in the pool: 22 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 77.9% STALE: pooled membership known incomplete (22 eligible families not in the pool: 22 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (22 eligible families not in the pool: 22 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 3: the 3 trial(s) named below were pooled; a further 22 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 3: the 3 trial(s) named below were pooled; 22 eligible families not in the pool: 22 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (22 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (22 eligible families not in the pool: 22 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. Pooling 3 trials gave HR 0.81 (95% CI 0.51 to 1.3), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.35 to 1.9. STALE: pooled membership known incomplete (22 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 22 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. Pooling 3 trials gave HR 0.81 (95% CI 0.51 to 1.3), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.35 to 1.9. STALE: pooled membership known incomplete (22 eligible families not in the pool: 22 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 22 eligible families not in the pool: 22 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Pooling 3 trials gave HR 0.81 (95% CI 0.51 to 1.3), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.35 to 1.9. STALE: pooled membership known incomplete (22 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Pooling 3 trials gave HR 0.81 (95% CI 0.51 to 1.3), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.35 to 1.9. STALE: pooled membership known incomplete (22 eligible families not in the pool: 22 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (22 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.; pooled trials differ on run-in enrichment: active_run_in_gi_intolerance_enriched, not_stated. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (22 eligible families not in the pool: 22 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.; pooled trials differ on run-in enrichment: active_run_in_gi_intolerance_enriched, not_stated. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (22 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (22 eligible families not in the pool: 22 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### corticosteroids-cap-mortality
OLD:
```text
Screened-in → pooled 9 trial families met P/I/C/design (screening); 2 reported this outcome with an extractable number and were pooled; the remaining 7 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 9 trial families met P/I/C/design (screening); 2 reported this outcome with an extractable number and were pooled; 14 eligible families not in the pool: the remaining 7 screened-in with no poolable value, 7 known eligible but not retrieved.
```
OLD:
```text
Between-study τ² 0 STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Between-study τ² 0 STALE: pooled membership known incomplete (14 eligible families not in the pool: 7 screened-in with no poolable value, 7 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (14 eligible families not in the pool: 7 screened-in with no poolable value, 7 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 7 trial families
```
NEW:
```text
Primary outcome membership 14 eligible families not in the pool: 7 screened-in with no poolable value, 7 known eligible but not retrieved
```
OLD:
```text
τ² 0 STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 0.0% STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
τ² 0 STALE: pooled membership known incomplete (14 eligible families not in the pool: 7 screened-in with no poolable value, 7 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 0.0% STALE: pooled membership known incomplete (14 eligible families not in the pool: 7 screened-in with no poolable value, 7 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (14 eligible families not in the pool: 7 screened-in with no poolable value, 7 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 2: the 2 trial(s) named below were pooled; a further 7 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 2: the 2 trial(s) named below were pooled; 14 eligible families not in the pool: 7 screened-in with no poolable value, 7 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
k = 4: the 4 trial(s) named below were pooled; a further 5 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 4: the 4 trial(s) named below were pooled; 5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (14 eligible families not in the pool: 7 screened-in with no poolable value, 7 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. Pooling 2 trials retained the point estimate (RR 0.55), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 7 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. Pooling 2 trials retained the point estimate (RR 0.55), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (14 eligible families not in the pool: 7 screened-in with no poolable value, 7 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 14 eligible families not in the pool: 7 screened-in with no poolable value, 7 known eligible but not retrieved.
```
OLD:
```text
Pooling 2 trials retained the point estimate (RR 0.55), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Pooling 2 trials retained the point estimate (RR 0.55), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (14 eligible families not in the pool: 7 screened-in with no poolable value, 7 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (14 eligible families not in the pool: 7 screened-in with no poolable value, 7 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (14 eligible families not in the pool: 7 screened-in with no poolable value, 7 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### corticosteroids-covid19-mortality
OLD:
```text
Screened-in → pooled 7 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 1 reported this outcome with an extractable number and were pooled; the remaining 6 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 7 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 1 reported this outcome with an extractable number and were pooled; 6 eligible families not in the pool: the remaining 6 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Heterogeneity state STALE: pooled membership known incomplete (6 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Heterogeneity state STALE: pooled membership known incomplete (6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 6 trial families
```
NEW:
```text
Primary outcome membership 6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved
```
OLD:
```text
Note STALE: pooled membership known incomplete (6 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Note STALE: pooled membership known incomplete (6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 1: the 1 trial(s) named below were pooled; a further 6 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 1: the 1 trial(s) named below were pooled; 6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (6 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. A single eligible trial contributed an extractable estimate: RR 0.83 (95% CI 0.75 to 0.93); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (6 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 6 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. A single eligible trial contributed an extractable estimate: RR 0.83 (95% CI 0.75 to 0.93); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
A single eligible trial contributed an extractable estimate: RR 0.83 (95% CI 0.75 to 0.93); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (6 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
A single eligible trial contributed an extractable estimate: RR 0.83 (95% CI 0.75 to 0.93); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (6 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (6 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### dapagliflozin-hfpef-hosp
OLD:
```text
Screened-in → pooled 5 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class KNOWN_ITEM_RETRIEVAL); 1 reported this outcome with an extractable number and were pooled; the remaining 4 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 5 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class KNOWN_ITEM_RETRIEVAL); 1 reported this outcome with an extractable number and were pooled; 4 eligible families not in the pool: the remaining 4 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Heterogeneity state STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Heterogeneity state STALE: pooled membership known incomplete (4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 4 trial families
```
NEW:
```text
Primary outcome membership 4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved
```
OLD:
```text
Note STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Note STALE: pooled membership known incomplete (4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 1: the 1 trial(s) named below were pooled; a further 4 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 1: the 1 trial(s) named below were pooled; 4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. A single eligible trial contributed an extractable estimate: HR 0.88 (95% CI 0.74 to 1.05); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 4 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. A single eligible trial contributed an extractable estimate: HR 0.88 (95% CI 0.74 to 1.05); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
A single eligible trial contributed an extractable estimate: HR 0.88 (95% CI 0.74 to 1.05); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
A single eligible trial contributed an extractable estimate: HR 0.88 (95% CI 0.74 to 1.05); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### denosumab-vertebral-fracture
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 0 trial families
```
NEW:
```text
Primary outcome membership 0 eligible families not in the pool: 0 screened-in with no poolable value, 0 known eligible but not retrieved
```
### doac-vte-recurrence
OLD:
```text
Screened-in → pooled 5 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class KNOWN_ITEM_RETRIEVAL); 6 reported this outcome with an extractable number and were pooled; the remaining 0 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 5 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class KNOWN_ITEM_RETRIEVAL); 6 reported this outcome with an extractable number and were pooled; 0 eligible families not in the pool: the remaining 0 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 0 trial families
```
NEW:
```text
Primary outcome membership 0 eligible families not in the pool: 0 screened-in with no poolable value, 0 known eligible but not retrieved
```
OLD:
```text
k = 2: the 2 trial(s) named below were pooled; a further 4 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 2: the 2 trial(s) named below were pooled; 4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
### dpp4-mace-t2d
OLD:
```text
Screened-in → pooled 5 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class KNOWN_ITEM_RETRIEVAL); 3 reported this outcome with an extractable number and were pooled; the remaining 2 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 5 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class KNOWN_ITEM_RETRIEVAL); 3 reported this outcome with an extractable number and were pooled; 3 eligible families not in the pool: the remaining 2 screened-in with no poolable value, 1 known eligible but not retrieved.
```
OLD:
```text
Prediction interval 0.84–1.21 STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 0 STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.84–1.21 STALE: pooled membership known incomplete (3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 0 STALE: pooled membership known incomplete (3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 2 trial families
```
NEW:
```text
Primary outcome membership 3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved
```
OLD:
```text
Prediction interval 0.84–1.21 STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 0 STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 0.0% STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.84–1.21 STALE: pooled membership known incomplete (3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 0 STALE: pooled membership known incomplete (3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 0.0% STALE: pooled membership known incomplete (3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 3: the 3 trial(s) named below were pooled; a further 2 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 3: the 3 trial(s) named below were pooled; 3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
k = 2: the 2 trial(s) named below were pooled; a further 3 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 2: the 2 trial(s) named below were pooled; 3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. Pooling 3 trials gave HR 1.01 (95% CI 0.84 to 1.21), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.84 to 1.21. STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 2 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. Pooling 3 trials gave HR 1.01 (95% CI 0.84 to 1.21), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.84 to 1.21. STALE: pooled membership known incomplete (3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved.
```
OLD:
```text
Pooling 3 trials gave HR 1.01 (95% CI 0.84 to 1.21), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.84 to 1.21. STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Pooling 3 trials gave HR 1.01 (95% CI 0.84 to 1.21), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.84 to 1.21. STALE: pooled membership known incomplete (3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### empagliflozin-hfpef-hosp
OLD:
```text
Screened-in → pooled 3 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class KNOWN_ITEM_RETRIEVAL); 1 reported this outcome with an extractable number and were pooled; the remaining 2 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 3 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class KNOWN_ITEM_RETRIEVAL); 1 reported this outcome with an extractable number and were pooled; 3 eligible families not in the pool: the remaining 2 screened-in with no poolable value, 1 known eligible but not retrieved.
```
OLD:
```text
Heterogeneity state STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Heterogeneity state STALE: pooled membership known incomplete (3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 2 trial families
```
NEW:
```text
Primary outcome membership 3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved
```
OLD:
```text
Note STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Note STALE: pooled membership known incomplete (3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 1: the 1 trial(s) named below were pooled; a further 2 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 1: the 1 trial(s) named below were pooled; 3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. A single eligible trial contributed an extractable estimate: HR 0.91 (95% CI 0.76 to 1.09); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 2 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. A single eligible trial contributed an extractable estimate: HR 0.91 (95% CI 0.76 to 1.09); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved.
```
OLD:
```text
A single eligible trial contributed an extractable estimate: HR 0.91 (95% CI 0.76 to 1.09); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
A single eligible trial contributed an extractable estimate: HR 0.91 (95% CI 0.76 to 1.09); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (3 eligible families not in the pool: 2 screened-in with no poolable value, 1 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### esketamine-trd-madrs
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 0 trial families
```
NEW:
```text
Primary outcome membership 0 eligible families not in the pool: 0 screened-in with no poolable value, 0 known eligible but not retrieved
```
### finerenone-ckd-t2d-renal
OLD:
```text
Screened-in → pooled 5 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 2 reported this outcome with an extractable number and were pooled; the remaining 3 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 5 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 2 reported this outcome with an extractable number and were pooled; 3 eligible families not in the pool: the remaining 3 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Between-study τ² 0 STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Between-study τ² 0 STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 3 trial families
```
NEW:
```text
Primary outcome membership 3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved
```
OLD:
```text
τ² 0 STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 0.0% STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
τ² 0 STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 0.0% STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 2: the 2 trial(s) named below were pooled; a further 3 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 2: the 2 trial(s) named below were pooled; 3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. Pooling 2 trials retained the point estimate (HR 0.84), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 3 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. Pooling 2 trials retained the point estimate (HR 0.84), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Pooling 2 trials retained the point estimate (HR 0.84), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Pooling 2 trials retained the point estimate (HR 0.84), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### glp1-ra-mace-t2d
OLD:
```text
Screened-in → pooled 9 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class KNOWN_ITEM_RETRIEVAL); 8 reported this outcome with an extractable number and were pooled; the remaining 1 trial family are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 9 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class KNOWN_ITEM_RETRIEVAL); 8 reported this outcome with an extractable number and were pooled; 3 eligible families not in the pool: the remaining 1 screened-in with no poolable value, 2 known eligible but not retrieved.
```
OLD:
```text
Prediction interval 0.81–0.91 STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 4e-05 (non-zero; not 0) STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.81–0.91 STALE: pooled membership known incomplete (3 eligible families not in the pool: 1 screened-in with no poolable value, 2 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 4e-05 (non-zero; not 0) STALE: pooled membership known incomplete (3 eligible families not in the pool: 1 screened-in with no poolable value, 2 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (3 eligible families not in the pool: 1 screened-in with no poolable value, 2 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 1 trial family
```
NEW:
```text
Primary outcome membership 3 eligible families not in the pool: 1 screened-in with no poolable value, 2 known eligible but not retrieved
```
OLD:
```text
Prediction interval 0.81–0.91 STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 4e-05 (non-zero; not 0) STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 0.9% STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.81–0.91 STALE: pooled membership known incomplete (3 eligible families not in the pool: 1 screened-in with no poolable value, 2 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 4e-05 (non-zero; not 0) STALE: pooled membership known incomplete (3 eligible families not in the pool: 1 screened-in with no poolable value, 2 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 0.9% STALE: pooled membership known incomplete (3 eligible families not in the pool: 1 screened-in with no poolable value, 2 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (3 eligible families not in the pool: 1 screened-in with no poolable value, 2 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 8: the 8 trial(s) named below were pooled; a further 1 trial family had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 8: the 8 trial(s) named below were pooled; 3 eligible families not in the pool: 1 screened-in with no poolable value, 2 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool: 1 screened-in with no poolable value, 2 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. Pooling 8 trials gave HR 0.86 (95% CI 0.81 to 0.91), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.81 to 0.91. STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 1 trial family were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. Pooling 8 trials gave HR 0.86 (95% CI 0.81 to 0.91), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.81 to 0.91. STALE: pooled membership known incomplete (3 eligible families not in the pool: 1 screened-in with no poolable value, 2 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 3 eligible families not in the pool: 1 screened-in with no poolable value, 2 known eligible but not retrieved.
```
OLD:
```text
Pooling 8 trials gave HR 0.86 (95% CI 0.81 to 0.91), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.81 to 0.91. STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Pooling 8 trials gave HR 0.86 (95% CI 0.81 to 0.91), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.81 to 0.91. STALE: pooled membership known incomplete (3 eligible families not in the pool: 1 screened-in with no poolable value, 2 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (3 eligible families not in the pool: 1 screened-in with no poolable value, 2 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (3 eligible families not in the pool: 1 screened-in with no poolable value, 2 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### iv-iron-hfref-hosp
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 7 trial families
```
NEW:
```text
Primary outcome membership 9 eligible families not in the pool: 7 screened-in with no poolable value, 2 known eligible but not retrieved
```
OLD:
```text
k = 2: the 2 trial(s) named below were pooled; a further 7 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 2: the 2 trial(s) named below were pooled; 9 eligible families not in the pool: 7 screened-in with no poolable value, 2 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (9 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (9 eligible families not in the pool: 7 screened-in with no poolable value, 2 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. The eligible trials report the primary outcome on INCOMPATIBLE estimand classes (HAZARD_RATIO_FIRST_EVENT + INCIDENCE_RATE_RATIO), so no pooled effect is reported: these effect measures are not one quantity without an explicit, source-backed conversion. The per-trial estimates are reported and each coherent strand must be pooled separately. STALE: pooled membership known incomplete (9 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 7 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. The eligible trials report the primary outcome on INCOMPATIBLE estimand classes (HAZARD_RATIO_FIRST_EVENT + INCIDENCE_RATE_RATIO), so no pooled effect is reported: these effect measures are not one quantity without an explicit, source-backed conversion. The per-trial estimates are reported and each coherent strand must be pooled separately. STALE: pooled membership known incomplete (9 eligible families not in the pool: 7 screened-in with no poolable value, 2 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 9 eligible families not in the pool: 7 screened-in with no poolable value, 2 known eligible but not retrieved.
```
OLD:
```text
The eligible trials report the primary outcome on INCOMPATIBLE estimand classes (HAZARD_RATIO_FIRST_EVENT + INCIDENCE_RATE_RATIO), so no pooled effect is reported: these effect measures are not one quantity without an explicit, source-backed conversion. The per-trial estimates are reported and each coherent strand must be pooled separately. STALE: pooled membership known incomplete (9 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
The eligible trials report the primary outcome on INCOMPATIBLE estimand classes (HAZARD_RATIO_FIRST_EVENT + INCIDENCE_RATE_RATIO), so no pooled effect is reported: these effect measures are not one quantity without an explicit, source-backed conversion. The per-trial estimates are reported and each coherent strand must be pooled separately. STALE: pooled membership known incomplete (9 eligible families not in the pool: 7 screened-in with no poolable value, 2 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (9 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (9 eligible families not in the pool: 7 screened-in with no poolable value, 2 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### melatonin-primary-insomnia-sol
OLD:
```text
Screened-in → pooled 8 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 1 reported this outcome with an extractable number and were pooled; the remaining 7 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 8 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 1 reported this outcome with an extractable number and were pooled; 7 eligible families not in the pool: the remaining 7 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Heterogeneity state STALE: pooled membership known incomplete (7 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Heterogeneity state STALE: pooled membership known incomplete (7 eligible families not in the pool: 7 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 7 trial families
```
NEW:
```text
Primary outcome membership 7 eligible families not in the pool: 7 screened-in with no poolable value, 0 known eligible but not retrieved
```
OLD:
```text
Note STALE: pooled membership known incomplete (7 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Note STALE: pooled membership known incomplete (7 eligible families not in the pool: 7 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 1 (1 pre-specified subgroup of age 65-80 ITT subgroup): the 1 trial(s) named below were pooled; a further 7 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 1 (1 pre-specified subgroup of age 65-80 ITT subgroup): the 1 trial(s) named below were pooled; 7 eligible families not in the pool: 7 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (7 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (7 eligible families not in the pool: 7 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. A single eligible trial contributed an extractable estimate: MD -17.4 (95% CI -28.52 to -6.28); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (7 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 7 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. A single eligible trial contributed an extractable estimate: MD -17.4 (95% CI -28.52 to -6.28); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (7 eligible families not in the pool: 7 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 7 eligible families not in the pool: 7 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
A single eligible trial contributed an extractable estimate: MD -17.4 (95% CI -28.52 to -6.28); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (7 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
A single eligible trial contributed an extractable estimate: MD -17.4 (95% CI -28.52 to -6.28); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (7 eligible families not in the pool: 7 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (7 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (7 eligible families not in the pool: 7 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (7 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (7 eligible families not in the pool: 7 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### metformin-pcos-ovulation
OLD:
```text
Screened-in → pooled 7 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 3 reported this outcome with an extractable number and were pooled; the remaining 4 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 7 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 3 reported this outcome with an extractable number and were pooled; 4 eligible families not in the pool: the remaining 4 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Prediction interval 0.01–549.69 STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 1.16 STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.01–549.69 STALE: pooled membership known incomplete (4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 1.16 STALE: pooled membership known incomplete (4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 4 trial families
```
NEW:
```text
Primary outcome membership 4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved
```
OLD:
```text
Prediction interval 0.01–549.69 STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 1.16 STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 78.4% STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.01–549.69 STALE: pooled membership known incomplete (4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 1.16 STALE: pooled membership known incomplete (4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 78.4% STALE: pooled membership known incomplete (4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 3: the 3 trial(s) named below were pooled; a further 4 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 3: the 3 trial(s) named below were pooled; 4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. Pooling 3 trials gave OR 2.07 (95% CI 0.09 to 46.6), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.01 to 549.69. STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 4 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. Pooling 3 trials gave OR 2.07 (95% CI 0.09 to 46.6), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.01 to 549.69. STALE: pooled membership known incomplete (4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Pooling 3 trials gave OR 2.07 (95% CI 0.09 to 46.6), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.01 to 549.69. STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Pooling 3 trials gave OR 2.07 (95% CI 0.09 to 46.6), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.01 to 549.69. STALE: pooled membership known incomplete (4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.; pooled trials differ on clomifene status: NAIVE, NOT_STATED, RESISTANT. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.; pooled trials differ on clomifene status: NAIVE, NOT_STATED, RESISTANT. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (4 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (4 eligible families not in the pool: 4 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### noac-vs-warfarin-af-stroke
OLD:
```text
Screened-in → pooled 7 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class KNOWN_ITEM_RETRIEVAL); 4 reported this outcome with an extractable number and were pooled; the remaining 3 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 7 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class KNOWN_ITEM_RETRIEVAL); 4 reported this outcome with an extractable number and were pooled; 3 eligible families not in the pool: the remaining 3 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Prediction interval 0.58–1.13 STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 0.00741 STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.58–1.13 STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 0.00741 STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 3 trial families
```
NEW:
```text
Primary outcome membership 3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved
```
OLD:
```text
Prediction interval 0.58–1.13 STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 0.00741 STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 42.4% STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.58–1.13 STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 0.00741 STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 42.4% STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 4: the 4 trial(s) named below were pooled; a further 3 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 4: the 4 trial(s) named below were pooled; 3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
k = 4: the 4 trial(s) named below were pooled; a further 3 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 4: the 4 trial(s) named below were pooled; 3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. Pooling 4 trials gave HR 0.81 (95% CI 0.66 to 0.98), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.58 to 1.13. STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 3 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. Pooling 4 trials gave HR 0.81 (95% CI 0.66 to 0.98), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.58 to 1.13. STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Pooling 4 trials gave HR 0.81 (95% CI 0.66 to 0.98), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.58 to 1.13. STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Pooling 4 trials gave HR 0.81 (95% CI 0.66 to 0.98), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.58 to 1.13. STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### omega3-cardiovascular-events
OLD:
```text
Screened-in → pooled 20 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 6 reported this outcome with an extractable number and were pooled; the remaining 14 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 20 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 6 reported this outcome with an extractable number and were pooled; 14 eligible families not in the pool: the remaining 14 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Prediction interval 0.69–1.29 STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 0.012 STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.69–1.29 STALE: pooled membership known incomplete (14 eligible families not in the pool: 14 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 0.012 STALE: pooled membership known incomplete (14 eligible families not in the pool: 14 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (14 eligible families not in the pool: 14 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 14 trial families
```
NEW:
```text
Primary outcome membership 14 eligible families not in the pool: 14 screened-in with no poolable value, 0 known eligible but not retrieved
```
OLD:
```text
Prediction interval 0.69–1.29 STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 0.012 STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 75.4% STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.69–1.29 STALE: pooled membership known incomplete (14 eligible families not in the pool: 14 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 0.012 STALE: pooled membership known incomplete (14 eligible families not in the pool: 14 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 75.4% STALE: pooled membership known incomplete (14 eligible families not in the pool: 14 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (14 eligible families not in the pool: 14 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 6: the 6 trial(s) named below were pooled; a further 14 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 6: the 6 trial(s) named below were pooled; 14 eligible families not in the pool: 14 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (14 eligible families not in the pool: 14 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. Pooling 6 trials gave HR 0.94 (95% CI 0.82 to 1.08), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.69 to 1.29. STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 14 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. Pooling 6 trials gave HR 0.94 (95% CI 0.82 to 1.08), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.69 to 1.29. STALE: pooled membership known incomplete (14 eligible families not in the pool: 14 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 14 eligible families not in the pool: 14 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Pooling 6 trials gave HR 0.94 (95% CI 0.82 to 1.08), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.69 to 1.29. STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Pooling 6 trials gave HR 0.94 (95% CI 0.82 to 1.08), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.69 to 1.29. STALE: pooled membership known incomplete (14 eligible families not in the pool: 14 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (14 eligible families not in the pool: 14 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (14 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (14 eligible families not in the pool: 14 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### pcsk9-mace
OLD:
```text
Screened-in → pooled 5 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 3 reported this outcome with an extractable number and were pooled; the remaining 2 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 5 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 3 reported this outcome with an extractable number and were pooled; 2 eligible families not in the pool: the remaining 2 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Prediction interval 0.68–0.97 STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 0.00057 (non-zero; not 0) STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.68–0.97 STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 0.00057 (non-zero; not 0) STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 2 trial families
```
NEW:
```text
Primary outcome membership 2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved
```
OLD:
```text
Prediction interval 0.68–0.97 STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 0.00057 (non-zero; not 0) STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 15.7% STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.68–0.97 STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 0.00057 (non-zero; not 0) STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 15.7% STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 3: the 3 trial(s) named below were pooled; a further 2 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 3: the 3 trial(s) named below were pooled; 2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. Pooling 3 trials gave HR 0.81 (95% CI 0.7 to 0.93), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.68 to 0.97. STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 2 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. Pooling 3 trials gave HR 0.81 (95% CI 0.7 to 0.93), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.68 to 0.97. STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Pooling 3 trials gave HR 0.81 (95% CI 0.7 to 0.93), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.68 to 0.97. STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Pooling 3 trials gave HR 0.81 (95% CI 0.7 to 0.93), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.68 to 0.97. STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.; pooled trials differ on composite components: CARDIOVASCULAR_DEATH | MYOCARDIAL_INFARCTION | STROKE; CHD_DEATH | MI | ISCHEMIC_STROKE; CORONARY_HEART_DISEASE_DEATH | MYOCARDIAL_INFARCTION | STROKE | UNSTABLE_ANGINA. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.; pooled trials differ on composite components: CARDIOVASCULAR_DEATH | MYOCARDIAL_INFARCTION | STROKE; CHD_DEATH | MI | ISCHEMIC_STROKE; CORONARY_HEART_DISEASE_DEATH | MYOCARDIAL_INFARCTION | STROKE | UNSTABLE_ANGINA. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### probiotics-aad-prevention
OLD:
```text
Screened-in → pooled 57 trial families met P/I/C/design (screening); 16 reported this outcome with an extractable number and were pooled; the remaining 41 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 57 trial families met P/I/C/design (screening); 16 reported this outcome with an extractable number and were pooled; 41 eligible families not in the pool: the remaining 41 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Prediction interval 0.27–1.74 STALE: pooled membership known incomplete (41 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 0.169 STALE: pooled membership known incomplete (41 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (41 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.27–1.74 STALE: pooled membership known incomplete (41 eligible families not in the pool: 41 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 0.169 STALE: pooled membership known incomplete (41 eligible families not in the pool: 41 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (41 eligible families not in the pool: 41 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 41 trial families
```
NEW:
```text
Primary outcome membership 41 eligible families not in the pool: 41 screened-in with no poolable value, 0 known eligible but not retrieved
```
OLD:
```text
Prediction interval 0.27–1.74 STALE: pooled membership known incomplete (41 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 0.169 STALE: pooled membership known incomplete (41 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 71.8% STALE: pooled membership known incomplete (41 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (41 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.27–1.74 STALE: pooled membership known incomplete (41 eligible families not in the pool: 41 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 0.169 STALE: pooled membership known incomplete (41 eligible families not in the pool: 41 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 71.8% STALE: pooled membership known incomplete (41 eligible families not in the pool: 41 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (41 eligible families not in the pool: 41 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 16: the 16 trial(s) named below were pooled; a further 41 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 16: the 16 trial(s) named below were pooled; 41 eligible families not in the pool: 41 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (41 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (41 eligible families not in the pool: 41 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. Pooling 16 trials gave RR 0.69 (95% CI 0.52 to 0.92), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.27 to 1.74. STALE: pooled membership known incomplete (41 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 41 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. Pooling 16 trials gave RR 0.69 (95% CI 0.52 to 0.92), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.27 to 1.74. STALE: pooled membership known incomplete (41 eligible families not in the pool: 41 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 41 eligible families not in the pool: 41 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Pooling 16 trials gave RR 0.69 (95% CI 0.52 to 0.92), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.27 to 1.74. STALE: pooled membership known incomplete (41 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Pooling 16 trials gave RR 0.69 (95% CI 0.52 to 0.92), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.27 to 1.74. STALE: pooled membership known incomplete (41 eligible families not in the pool: 41 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (41 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (41 eligible families not in the pool: 41 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (41 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (41 eligible families not in the pool: 41 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### sacubitril-valsartan-hfref
OLD:
```text
Pooled result REFUSED (k=2 direction conflict). k=2 pooled row refused because point estimates are on opposite sides of the null At k=2, if point estimates are on opposite sides of the null or trial CIs do not overlap, no pooled row is served. A k=1 anchor is shown only when it is explicitly pre-named in the topic configuration/protocol metadata; otherwise both trials are shown only as named individual results. The invalid pooled row is quarantined for audit only: 0.84 (0.21-3.32), tau^2=0.01177, I^2=24.9%. STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Pooled result REFUSED (k=2 direction conflict). k=2 pooled row refused because point estimates are on opposite sides of the null At k=2, if point estimates are on opposite sides of the null or trial CIs do not overlap, no pooled row is served. A k=1 anchor is shown only when it is explicitly pre-named in the topic configuration/protocol metadata; otherwise both trials are shown only as named individual results. The invalid pooled row is quarantined for audit only: 0.84 (0.21-3.32), tau^2=0.01177, I^2=24.9%. STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 5 trial families
```
NEW:
```text
Primary outcome membership 5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved
```
OLD:
```text
Pooled result REFUSED (k=2 direction conflict). k=2 pooled row refused because point estimates are on opposite sides of the null At k=2, if point estimates are on opposite sides of the null or trial CIs do not overlap, no pooled row is served. A k=1 anchor is shown only when it is explicitly pre-named in the topic configuration/protocol metadata; otherwise both trials are shown only as named individual results. The invalid pooled row is quarantined for audit only: 0.84 (0.21-3.32), tau^2=0.01177, I^2=24.9%. STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
k = 2: the 2 trial(s) named below were pooled; a further 5 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
Pooled result REFUSED (k=2 direction conflict). k=2 pooled row refused because point estimates are on opposite sides of the null At k=2, if point estimates are on opposite sides of the null or trial CIs do not overlap, no pooled row is served. A k=1 anchor is shown only when it is explicitly pre-named in the topic configuration/protocol metadata; otherwise both trials are shown only as named individual results. The invalid pooled row is quarantined for audit only: 0.84 (0.21-3.32), tau^2=0.01177, I^2=24.9%. STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
k = 2: the 2 trial(s) named below were pooled; 5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. | counted as ONE conservative downgrade pending human judgement (a check that could not run cannot raise certainty)
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. The two eligible trials conflict in direction or interval support, so no pooled effect is reported; both trial estimates are reported individually. STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 5 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. The two eligible trials conflict in direction or interval support, so no pooled effect is reported; both trial estimates are reported individually. STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
The two eligible trials conflict in direction or interval support, so no pooled effect is reported; both trial estimates are reported individually. STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
The two eligible trials conflict in direction or interval support, so no pooled effect is reported; both trial estimates are reported individually. STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### semaglutide-obesity-mace
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 0 trial families
```
NEW:
```text
Primary outcome membership 0 eligible families not in the pool: 0 screened-in with no poolable value, 0 known eligible but not retrieved
```
### semaglutide-obesity-weight
OLD:
```text
Screened-in → pooled 7 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 2 reported this outcome with an extractable number and were pooled; the remaining 5 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 7 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 2 reported this outcome with an extractable number and were pooled; 5 eligible families not in the pool: the remaining 5 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Between-study τ² 1.86 STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Between-study τ² 1.86 STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 5 trial families
```
NEW:
```text
Primary outcome membership 5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved
```
OLD:
```text
τ² 1.86 STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 84.5% STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
τ² 1.86 STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 84.5% STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 2: the 2 trial(s) named below were pooled; a further 5 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 2: the 2 trial(s) named below were pooled; 5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. | counted as ONE conservative downgrade pending human judgement (a check that could not run cannot raise certainty)
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. Pooling 2 trials retained the point estimate (MD -11.84), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 5 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. Pooling 2 trials retained the point estimate (MD -11.84), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Pooling 2 trials retained the point estimate (MD -11.84), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Pooling 2 trials retained the point estimate (MD -11.84), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (5 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (5 eligible families not in the pool: 5 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### sglt2-ckd-progression
OLD:
```text
Screened-in → pooled 9 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class KNOWN_ITEM_RETRIEVAL); 3 reported this outcome with an extractable number and were pooled; the remaining 6 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 9 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class KNOWN_ITEM_RETRIEVAL); 3 reported this outcome with an extractable number and were pooled; 6 eligible families not in the pool: the remaining 6 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Prediction interval 0.53–0.89 STALE: pooled membership known incomplete (6 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 0.00134 (non-zero; not 0) STALE: pooled membership known incomplete (6 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (6 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.53–0.89 STALE: pooled membership known incomplete (6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 0.00134 (non-zero; not 0) STALE: pooled membership known incomplete (6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 6 trial families
```
NEW:
```text
Primary outcome membership 6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved
```
OLD:
```text
Prediction interval 0.53–0.89 STALE: pooled membership known incomplete (6 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 0.00134 (non-zero; not 0) STALE: pooled membership known incomplete (6 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 17.5% STALE: pooled membership known incomplete (6 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (6 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.53–0.89 STALE: pooled membership known incomplete (6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 0.00134 (non-zero; not 0) STALE: pooled membership known incomplete (6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 17.5% STALE: pooled membership known incomplete (6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 3: the 3 trial(s) named below were pooled; a further 6 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 3: the 3 trial(s) named below were pooled; 6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
k = 1: the 1 trial(s) named below were pooled; a further 8 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 1: the 1 trial(s) named below were pooled; 8 eligible families not in the pool: 8 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (6 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. Pooling 3 trials gave HR 0.68 (95% CI 0.55 to 0.84), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.53 to 0.89. STALE: pooled membership known incomplete (6 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 6 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. Pooling 3 trials gave HR 0.68 (95% CI 0.55 to 0.84), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.53 to 0.89. STALE: pooled membership known incomplete (6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Pooling 3 trials gave HR 0.68 (95% CI 0.55 to 0.84), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.53 to 0.89. STALE: pooled membership known incomplete (6 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Pooling 3 trials gave HR 0.68 (95% CI 0.55 to 0.84), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.53 to 0.89. STALE: pooled membership known incomplete (6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (6 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (6 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (6 eligible families not in the pool: 6 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### sglt2-hfref-hosp-cvdeath
OLD:
```text
Screened-in → pooled 5 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class KNOWN_ITEM_RETRIEVAL); 2 reported this outcome with an extractable number and were pooled; the remaining 3 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 5 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class KNOWN_ITEM_RETRIEVAL); 2 reported this outcome with an extractable number and were pooled; 3 eligible families not in the pool: the remaining 3 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Between-study τ² 0 STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Between-study τ² 0 STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 3 trial families
```
NEW:
```text
Primary outcome membership 3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved
```
OLD:
```text
τ² 0 STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 0.0% STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
τ² 0 STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 0.0% STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 2: the 2 trial(s) named below were pooled; a further 3 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 2: the 2 trial(s) named below were pooled; 3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. Pooling 2 trials retained the point estimate (HR 0.75), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 3 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. Pooling 2 trials retained the point estimate (HR 0.75), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Pooling 2 trials retained the point estimate (HR 0.75), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Pooling 2 trials retained the point estimate (HR 0.75), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### sglt2-primary-prevention-hf
OLD:
```text
Screened-in → pooled 6 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class KNOWN_ITEM_RETRIEVAL); 4 reported this outcome with an extractable number and were pooled; the remaining 2 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 6 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class KNOWN_ITEM_RETRIEVAL); 4 reported this outcome with an extractable number and were pooled; 2 eligible families not in the pool: the remaining 2 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Prediction interval 0.58–0.84 STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 0 STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.58–0.84 STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Between-study τ² 0 STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 2 trial families
```
NEW:
```text
Primary outcome membership 2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved
```
OLD:
```text
Prediction interval 0.58–0.84 STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 0 STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 0.0% STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Prediction interval 0.58–0.84 STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
τ² 0 STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 0.0% STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 4: the 4 trial(s) named below were pooled; a further 2 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 4: the 4 trial(s) named below were pooled; 2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. Pooling 4 trials gave HR 0.7 (95% CI 0.58 to 0.84), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.58 to 0.84. STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 2 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. Pooling 4 trials gave HR 0.7 (95% CI 0.58 to 0.84), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.58 to 0.84. STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Pooling 4 trials gave HR 0.7 (95% CI 0.58 to 0.84), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.58 to 0.84. STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Pooling 4 trials gave HR 0.7 (95% CI 0.58 to 0.84), random-effects (Paule-Mandel with a Hartung-Knapp interval). The 95% prediction interval was 0.58 to 0.84. STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### spironolactone-hfref-mortality
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 0 trial families
```
NEW:
```text
Primary outcome membership 0 eligible families not in the pool: 0 screened-in with no poolable value, 0 known eligible but not retrieved
```
### statins-primary-prevention-elderly
OLD:
```text
Screened-in → pooled 4 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 2 reported this outcome with an extractable number and were pooled; the remaining 2 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 4 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 2 reported this outcome with an extractable number and were pooled; 2 eligible families not in the pool: the remaining 2 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Between-study τ² 0 STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Between-study τ² 0 STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Heterogeneity state STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 2 trial families
```
NEW:
```text
Primary outcome membership 2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved
```
OLD:
```text
τ² 0 STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 0.0% STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
τ² 0 STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
I² 0.0% STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
Note STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 2 (1 trial + 1 pre-specified subgroup of JUPITER): the 2 trial(s) named below were pooled; a further 2 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 2 (1 trial + 1 pre-specified subgroup of JUPITER): the 2 trial(s) named below were pooled; 2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. Pooling 2 trials retained the point estimate (HR 0.68), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 2 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. Pooling 2 trials retained the point estimate (HR 0.68), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Pooling 2 trials retained the point estimate (HR 0.68), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Pooling 2 trials retained the point estimate (HR 0.68), but the registered PM/HKSJ confidence interval is not served at k=2 because it uses t(1)=12.71; no pooled significance or null-crossing claim is made. STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (2 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (2 eligible families not in the pool: 2 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### ticagrelor-vs-clopidogrel-acs
OLD:
```text
Pooled result REFUSED (k=2 direction conflict). k=2 pooled row refused because point estimates are on opposite sides of the null At k=2, if point estimates are on opposite sides of the null or trial CIs do not overlap, no pooled row is served. A k=1 anchor is shown only when it is explicitly pre-named in the topic configuration/protocol metadata; otherwise both trials are shown only as named individual results. The invalid pooled row is quarantined for audit only: 1.05 (0.03-33.89), tau^2=0.12171, I^2=77.7%. STALE: pooled membership known incomplete (1 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Pooled result REFUSED (k=2 direction conflict). k=2 pooled row refused because point estimates are on opposite sides of the null At k=2, if point estimates are on opposite sides of the null or trial CIs do not overlap, no pooled row is served. A k=1 anchor is shown only when it is explicitly pre-named in the topic configuration/protocol metadata; otherwise both trials are shown only as named individual results. The invalid pooled row is quarantined for audit only: 1.05 (0.03-33.89), tau^2=0.12171, I^2=77.7%. STALE: pooled membership known incomplete (1 eligible families not in the pool: 1 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 1 trial family
```
NEW:
```text
Primary outcome membership 1 eligible families not in the pool: 1 screened-in with no poolable value, 0 known eligible but not retrieved
```
OLD:
```text
Pooled result REFUSED (k=2 direction conflict). k=2 pooled row refused because point estimates are on opposite sides of the null At k=2, if point estimates are on opposite sides of the null or trial CIs do not overlap, no pooled row is served. A k=1 anchor is shown only when it is explicitly pre-named in the topic configuration/protocol metadata; otherwise both trials are shown only as named individual results. The invalid pooled row is quarantined for audit only: 1.05 (0.03-33.89), tau^2=0.12171, I^2=77.7%. STALE: pooled membership known incomplete (1 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Pooled result REFUSED (k=2 direction conflict). k=2 pooled row refused because point estimates are on opposite sides of the null At k=2, if point estimates are on opposite sides of the null or trial CIs do not overlap, no pooled row is served. A k=1 anchor is shown only when it is explicitly pre-named in the topic configuration/protocol metadata; otherwise both trials are shown only as named individual results. The invalid pooled row is quarantined for audit only: 1.05 (0.03-33.89), tau^2=0.12171, I^2=77.7%. STALE: pooled membership known incomplete (1 eligible families not in the pool: 1 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 2: the 2 trial(s) named below were pooled; a further 1 trial family had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 2: the 2 trial(s) named below were pooled; 1 eligible families not in the pool: 1 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (1 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. | counted as ONE conservative downgrade pending human judgement (a check that could not run cannot raise certainty)
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (1 eligible families not in the pool: 1 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. The two eligible trials conflict in direction, so no pooled effect is reported. The pre-named k=1 anchor is PLATO: HR 0.84 (95% CI 0.77 to 0.92); the named remainder is PHILO. STALE: pooled membership known incomplete (1 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 1 trial family were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. The two eligible trials conflict in direction, so no pooled effect is reported. The pre-named k=1 anchor is PLATO: HR 0.84 (95% CI 0.77 to 0.92); the named remainder is PHILO. STALE: pooled membership known incomplete (1 eligible families not in the pool: 1 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 1 eligible families not in the pool: 1 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
The two eligible trials conflict in direction, so no pooled effect is reported. The pre-named k=1 anchor is PLATO: HR 0.84 (95% CI 0.77 to 0.92); the named remainder is PHILO. STALE: pooled membership known incomplete (1 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
The two eligible trials conflict in direction, so no pooled effect is reported. The pre-named k=1 anchor is PLATO: HR 0.84 (95% CI 0.77 to 0.92); the named remainder is PHILO. STALE: pooled membership known incomplete (1 eligible families not in the pool: 1 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (1 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that the confidence interval is wide or crosses the null (imprecision); STALE: pooled membership known incomplete (1 eligible families not in the pool: 1 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (1 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (1 eligible families not in the pool: 1 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### tocilizumab-covid19-mortality
OLD:
```text
Screened-in → pooled 12 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 1 reported this outcome with an extractable number and were pooled; the remaining 11 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 12 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 1 reported this outcome with an extractable number and were pooled; 11 eligible families not in the pool: the remaining 11 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Heterogeneity state STALE: pooled membership known incomplete (11 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Heterogeneity state STALE: pooled membership known incomplete (11 eligible families not in the pool: 11 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 11 trial families
```
NEW:
```text
Primary outcome membership 11 eligible families not in the pool: 11 screened-in with no poolable value, 0 known eligible but not retrieved
```
OLD:
```text
Note STALE: pooled membership known incomplete (11 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Note STALE: pooled membership known incomplete (11 eligible families not in the pool: 11 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 1: the 1 trial(s) named below were pooled; a further 11 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 1: the 1 trial(s) named below were pooled; 11 eligible families not in the pool: 11 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (11 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (11 eligible families not in the pool: 11 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. A single eligible trial contributed an extractable estimate: RR 0.85 (95% CI 0.76 to 0.94); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (11 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 11 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. A single eligible trial contributed an extractable estimate: RR 0.85 (95% CI 0.76 to 0.94); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (11 eligible families not in the pool: 11 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 11 eligible families not in the pool: 11 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
A single eligible trial contributed an extractable estimate: RR 0.85 (95% CI 0.76 to 0.94); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (11 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
A single eligible trial contributed an extractable estimate: RR 0.85 (95% CI 0.76 to 0.94); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (11 eligible families not in the pool: 11 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (11 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (11 eligible families not in the pool: 11 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (11 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (11 eligible families not in the pool: 11 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
### tranexamic-acid-pph
OLD:
```text
Screened-in → pooled 4 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 1 reported this outcome with an extractable number and were pooled; the remaining 3 trial families are listed as declared-absent in Results (they were included but reported no poolable value for this outcome).
```
NEW:
```text
Screened-in → pooled 4 of the pre-identified set met eligibility; eligibility over the open scope was NOT tested (search class TITLE_SEEDED_RETRIEVAL); 1 reported this outcome with an extractable number and were pooled; 3 eligible families not in the pool: the remaining 3 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
Heterogeneity state STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Heterogeneity state STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Eligible but outcome not extracted from the abstract (full-text pass pending) 3 trial families
```
NEW:
```text
Primary outcome membership 3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved
```
OLD:
```text
Note STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Note STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
k = 1: the 1 trial(s) named below were pooled; a further 3 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 1: the 1 trial(s) named below were pooled; 3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
k = 1: the 1 trial(s) named below were pooled; a further 3 trial families had no poolable value for this outcome and are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
NEW:
```text
k = 1: the 1 trial(s) named below were pooled; 3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved. Screened-in families without a poolable value are listed below with an explicit absence/refusal state . These typed states distinguish source silence from effect-present estimand mismatches, uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached abstracts, and other evidence refusals; only no outcome data in source (0 here) is a claim about the trial itself. An unassessed outcome never counts as favourable to the intervention.
```
OLD:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
Inconsistency NOT ASSESSED not assessable: STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
Results. A single eligible trial contributed an extractable estimate: RR 0.81 (95% CI 0.65 to 1); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 3 trial families were declared absent for this outcome (reported reason on each).
```
NEW:
```text
Results. A single eligible trial contributed an extractable estimate: RR 0.81 (95% CI 0.65 to 1); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable. 3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved.
```
OLD:
```text
A single eligible trial contributed an extractable estimate: RR 0.81 (95% CI 0.65 to 1); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
A single eligible trial contributed an extractable estimate: RR 0.81 (95% CI 0.65 to 1); with k=1 no between-trial heterogeneity or prediction interval is estimable. STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
OLD:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
NEW:
```text
This synthesis is limited in that STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.. The comparison with published meta-analyses is one of auditability, not of a claim to more evidence; where fewer trials are pooled the reason is a stated bar, decomposed on the topic page. Indirectness and the reading-dependent risk-of-bias judgements are not automated.
```
OLD:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (3 eligible families not in the pool); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
NEW:
```text
15 Certainty assessment ✓ present GRADE provisional -- not yet fully assessable; see the domain table for assessed and unassessed domains. STALE: pooled membership known incomplete (3 eligible families not in the pool: 3 screened-in with no poolable value, 0 known eligible but not retrieved); tau^2, I^2 and the prediction interval are descriptive only, not interpretable.
```
