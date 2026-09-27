"""End-to-end contract on the 17 rebuilt HM3 pages and their held inputs."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

from harness import harms

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/evidence/hm3-held-source-audit'
BASE = 'f6f7b14c820bdadd258122ac0bb54c7e4d2a989a'
# A LATER landing may change the pinned HM3 controls only by a DECLARED supersession that names every change (the
# snapshot itself is never rewritten): docs/evidence/hm3-held-source-audit/screening_roles_supersession.json, the V1.0.1
# screening-roles landing -- each screening row it changed (before/after), the key it added to every row, and each
# harms outcome it made HARMS_INCOMPLETE with the reports that did it. Anything NOT declared still fails.
_SS_PATH = EVIDENCE / 'screening_roles_supersession.json'
SUPERSESSION = json.loads(_SS_PATH.read_text(encoding='utf-8')) if _SS_PATH.exists() else {'pages': {}}


def _declared(slug):
    return (SUPERSESSION.get('pages') or {}).get(slug) or {}


def test_rebuilt_pages_account_for_every_baseline_harm():
    decisions = json.loads((EVIDENCE/'decisions.json').read_text(encoding='utf-8'))
    for d in decisions:
        folder = ROOT/'docs/reviews'/d['topic']
        review = json.loads((folder/'review.json').read_text(encoding='utf-8'))
        outcome = next(o for o in review['outcomes'] if o['name'] == d['outcome'])
        # a DECIDED harm row that a later landing moved must be declared by name, with the values it moved to
        sup = (_declared(d['topic']).get('harm_decisions_superseded') or {}).get(f"{d['outcome']}|{d['trial']}")
        if sup:
            assert sup.get('reason') and sup.get('after') == 'POOLED', (d['topic'], d['outcome'], d['trial'])
            row = next(t for t in outcome['trials'] if t['id'].replace('PMID ', '') == d['trial'])
            assert {k: row.get(k) for k in sup['values_after']} == sup['values_after'], (d['topic'], d['trial'])
            continue
        if outcome['result'].get('harms_incomplete'):
            declared = (_declared(d['topic']).get('harms_incomplete_by_entered_reports') or {}).get(d['outcome'])
            assert declared, (d['topic'], d['outcome'], 'HARMS_INCOMPLETE without a declared supersession')
            named = re.search(r"unresolved \(([^)]*)\)", outcome['result'].get('reason') or '')
            assert named and sorted(x.strip() for x in named.group(1).split(',')) == declared, (d['topic'], d['outcome'])
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
                assert row.get('reason_code') in ('ENDPOINT_UNBOUND','RESULT_INCOMPATIBLE'), (d['topic'],d['trial'],row.get('reason_code'))
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
        ss = _declared(slug)
        added = tuple(ss.get('added_keys') or ())
        changed = ss.get('screening_rows_changed') or {}
        strip = lambda r: {k: v for k, v in r.items() if k not in added}
        b_rows = {str(r['id']): r for r in before['screening_records']}
        a_rows = {str(r['id']): strip(r) for r in after['screening']['records']}
        assert set(b_rows) == set(a_rows), slug
        for rid in b_rows:
            if rid in changed:
                c = changed[rid]
                assert {k: b_rows[rid].get(k) for k in ('decision', 'rule_id', 'reason')} == c['before'], (slug, rid)
                assert {k: a_rows[rid].get(k) for k in ('decision', 'rule_id', 'reason')} == c['after'], (slug, rid)
                # every OTHER field that moved is declared with its before/after value, and nothing undeclared moved
                ks = sorted((set(b_rows[rid]) | set(a_rows[rid])) - {'decision', 'rule_id', 'reason'})
                moved = {k: [b_rows[rid].get(k), a_rows[rid].get(k)] for k in ks if b_rows[rid].get(k) != a_rows[rid].get(k)}
                assert json.loads(json.dumps(moved)) == (c.get('other_fields_changed') or {}), (slug, rid, 'undeclared field change')
            else:
                assert b_rows[rid] == a_rows[rid], (slug, rid, 'screening row changed without a declared supersession')
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
