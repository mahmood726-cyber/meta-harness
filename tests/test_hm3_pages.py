"""End-to-end contract on the 17 rebuilt HM3 pages and their held inputs."""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # tests/ on the path for _contracts
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
            # a decided harm row is POOLED with the decided values, or SET ASIDE with those values visible as the
            # candidate tuple and a named reason (the hand binder could not bind them to held bytes) -- never
            # silently absent. Until 2026-09-20 this required the row to be pooled; the set-aside state is the
            # binder's honest answer and the reviewer's decision is recorded in docs/error_rate.json.
            row = next((t for t in outcome['trials'] if t['id'].replace('PMID ','')==d['trial']), None)
            if row is not None:
                for field in ('ai','n1i','ci','n2i','effect','ci_low','ci_high','scale'):
                    if field in d['entry']:
                        assert row[field] == d['entry'][field]
                assert row['verified'] == 'verified'
            else:
                row = next(t for t in outcome['declared_absent_trials'] if t['id'].replace('PMID ','')==d['trial'])
                if row.get('admission_verdict'):
                    from _contracts import partition
                    partition(ROOT, d['topic'], outcome)
                    assert row['admission_verdict']['final'] == 'INADMISSIBLE'
                    assert row['reason_code'] in row['admission_verdict']['failing']
                else:
                    assert row.get('reason_code') in ('ENDPOINT_UNBOUND', 'RESULT_INCOMPATIBLE'), (d['topic'], d['trial'], row.get('reason_code'))
                cand = row.get('candidate_tuple') or {}
                for field in ('ai','n1i','ci','n2i','effect','ci_low','ci_high'):
                    if field in d['entry']:
                        assert cand.get(field) == d['entry'][field], (d['trial'], field, cand)
                html = (folder/'index.html').read_text(encoding='utf-8')
                assert d['trial'] in html


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
            assert before['primary_values'] != sup['primary_values_after'], (slug, 'supersession declared but nothing moved')
        expected_values = sup['primary_values_after'] if sup else before['primary_values']
        from _contracts import partition
        pooled, absent = partition(ROOT, slug, b)
        accounted = {t['id']: t for t in pooled}
        for row in absent:
            if row.get('candidate_tuple'):
                accounted[row['id']] = dict(row, **row['candidate_tuple'])
        for old_row in expected_values:
            assert old_row['id'] in accounted, (slug, old_row['id'])
            assert old_row == {k: accounted[old_row['id']].get(k) for k in fields}, (slug, old_row['id'])


def test_retained_aact_rows_match_audit_hashes():
    manifest = json.loads((EVIDENCE/'aact/manifest.json').read_text(encoding='utf-8'))
    for name, meta in manifest['tables'].items():
        data = (EVIDENCE/'aact'/name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == meta['sha256']
