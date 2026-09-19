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
        assert not outcome['result'].get('harms_incomplete'), (d['topic'],d['outcome'])
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
        old_records = {row['id']: row for row in before['screening_records']}
        new_records = {row['id']: row for row in after['screening']['records']}
        assert old_records.keys() == new_records.keys(), slug
        # A title omission may now request manual review. It must not admit new trials,
        # alter source identities, or weaken the pinned primary-value contract below.
        assert {key for key, row in old_records.items() if row['decision'] == 'include'} == {
            key for key, row in new_records.items() if row['decision'] == 'include'}, slug
        for key, old_row in old_records.items():
            new_row = new_records[key]
            if old_row == new_row:
                continue
            assert old_row['decision'] == 'exclude' and old_row['rule_id'] in ('X2', 'X3'), (slug, key)
            assert new_row['decision'] == 'review' and new_row['rule_id'] == 'MANUAL_REVIEW', (slug, key)
            mutable = {'decision', 'rule_id', 'reason', 'span'}
            assert {k: v for k, v in old_row.items() if k not in mutable} == {
                k: v for k, v in new_row.items() if k not in mutable}, (slug, key)
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
