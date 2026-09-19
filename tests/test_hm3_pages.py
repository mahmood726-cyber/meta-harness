"""End-to-end contract on the 17 rebuilt HM3 pages and their held inputs."""
import hashlib
import json
import subprocess
from pathlib import Path

from harness import harms

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/evidence/hm3-held-source-audit'
BASE = 'f6f7b14c820bdadd258122ac0bb54c7e4d2a989a'


def test_rebuilt_pages_account_for_every_baseline_harm():
    decisions = json.loads((EVIDENCE/'decisions.json').read_text(encoding='utf-8'))
    for d in decisions:
        folder = ROOT/'docs/reviews'/d['topic']
        review = json.loads((folder/'review.json').read_text(encoding='utf-8'))
        outcome = next(o for o in review['outcomes'] if o['name'] == d['outcome'])
        if outcome['result'].get('harms_incomplete'):
            # The HM3 contract is that every HM3-DECIDED trial stays accounted for. A later landing may expose
            # an extraction debt HM3 never saw: ws/ABSFB (2026-09-19) removed the absence classifier's
            # widening fallback, and SMART's (29485925) acute-kidney-injury counts -- previously masked by
            # MAKE30's OR 0.91 attributed to this outcome -- surfaced as KNOWN_REPORTED_NOT_YET_EXTRACTED.
            # That debt must be NAMED in the result and must not be an HM3-decided trial.
            import re
            unresolved = set(re.findall(r'\d{8}', outcome['result'].get('reason') or ''))
            decided = {e['trial'] for e in decisions if e['topic'] == d['topic'] and e['outcome'] == d['outcome']}
            assert unresolved and not (unresolved & decided), (d['topic'], d['outcome'], unresolved, decided)
        if d['entry'].get('absent'):
            row = next(t for t in outcome['declared_absent_trials'] if t['id'].replace('PMID ','')==d['trial'])
            assert row['harm_absence_state'] in (harms.RETRIEVED_REFUSED_WITH_REASON,harms.RETRIEVED_INCOMPATIBLE_STRUCTURE)
            assert row['reason_code'] == d['entry']['provenance']
            assert row['source_span'] == d['entry']['source_span']
            html = (folder/'index.html').read_text(encoding='utf-8')
            assert d['trial'] in html
        else:
            row = next(t for t in outcome['trials'] if t['id'].replace('PMID ','')==d['trial'])
            for field in ('ai','n1i','ci','n2i','effect','ci_low','ci_high','scale'):
                if field in d['entry']:
                    assert row[field] == d['entry'][field]
            assert row['verified'] == 'verified'


def test_primary_trial_values_and_membership_are_unchanged():
    slugs = {r['slug'] for r in json.loads((EVIDENCE/'baseline-debt.json').read_text(encoding='utf-8'))}
    fields = ('id','effect','ci_low','ci_high','scale','ai','n1i','ci','n2i','mean1','mean2','sd1','sd2','nc1','nc2')
    for slug in slugs:
        rel = f'docs/reviews/{slug}/review.json'
        # The baseline is a committed fixture pinned to BASE (a lane-base commit CI never fetches), captured once
        # from `git show`; a control must be pinned to an immutable version, never read from a live ref.
        snap = json.loads((EVIDENCE/'primary-baseline-f6f7b14c.json').read_text(encoding='utf-8'))
        assert snap['pinned_commit'] == BASE
        before = snap['pages'][slug]
        after = json.loads((ROOT/rel).read_text(encoding='utf-8'))
        assert before['screening_records'] == after['screening']['records'], slug
        b = next(o for o in after['outcomes'] if o.get('primary'))
        values = lambda o: [{k:t.get(k) for k in fields} for t in o['trials']]
        sup = (snap.get('superseded') or {}).get(slug)
        if sup:
            # a LATER landing may change a primary only by a declared, named supersession that records the
            # values it moved to; the pinned HM3 values are never rewritten (the control stays immutable)
            assert sup.get('landing') and sup.get('reason'), slug
            assert sup['primary_values_after'] == values(b), slug
            assert before['primary_values'] != values(b), (slug, 'supersession declared but nothing moved')
            continue
        assert before['primary_values'] == values(b), slug


def test_retained_aact_rows_match_audit_hashes():
    manifest = json.loads((EVIDENCE/'aact/manifest.json').read_text(encoding='utf-8'))
    for name, meta in manifest['tables'].items():
        data = (EVIDENCE/'aact'/name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == meta['sha256']
