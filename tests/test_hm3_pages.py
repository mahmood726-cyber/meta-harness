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


def test_rebuilt_pages_account_for_every_baseline_harm():
    decisions = json.loads((EVIDENCE/'decisions.json').read_text(encoding='utf-8'))
    for d in decisions:
        folder = ROOT/'docs/reviews'/d['topic']
        review = json.loads((folder/'review.json').read_text(encoding='utf-8'))
        outcome = next(o for o in review['outcomes'] if o['name'] == d['outcome'])
        if outcome['result'].get('harms_incomplete'):
            # V1.0.1 (PCSK9 review): a trial a held comparator names now enters screening; one that reports harms not
            # yet extracted makes the outcome honestly incomplete. That is allowed only for such entrants -- every
            # BASELINE harm must still be accounted for
            entrants = set((review.get('comparator_named') or {}).get('entered') or [])
            open_ = [t['id'] for t in outcome['result']['harm_reporting_trials'] if t['state'] == 'KNOWN_REPORTED_NOT_YET_EXTRACTED']
            assert open_ and set(open_) <= entrants and d['trial'] not in open_, (d['topic'], d['outcome'], open_)
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
        # V1.0.1 (empagliflozin review): a registry record the registry itself states is not randomised (allocation
        # NA / NON_RANDOMIZED) is now excluded on X1 before any later rule. The only allowed difference from the pinned
        # control is exactly that: same record, same decision, rule X1, and a span quoting the registry allocation.
        # V1.0.1 (PCSK9 review): records a held comparator names are APPENDED to screening (found by COMPARATOR_NAMED);
        # every pinned record keeps its place and decision
        b_recs = before['screening_records']
        a_recs = [x for x in after['screening']['records'] if x.get('found_by') != ['COMPARATOR_NAMED']]
        # V1.0.1 (semaglutide-weight review): on a topic whose exclusions are traced to the protocol (harness/rule_trace.py),
        # an exclusion by a term that traces to no protocol text becomes NEEDS_ADJUDICATION -- same record, rule
        # X-UNTRACED, and the reason names a term the topic's own trace lists as untraced
        untraced = set((after.get('rule_trace') or {}).get('untraced') or [])
        def _untraced_adjudication(x, y):
            return (x['id'] == y['id'] and x['decision'] == 'exclude' and y['decision'] == 'adjudicate'
                    and y['rule_id'] == 'X-UNTRACED' and any(f"'{t}'" in y['reason'] for t in untraced))
        assert len(b_recs) == len(a_recs), slug
        assert all((x['id'], x['decision']) == (y['id'], y['decision']) or _untraced_adjudication(x, y)
                   for x, y in zip(b_recs, a_recs)), slug
        for x, y in zip(b_recs, a_recs):
            if x != y and _untraced_adjudication(x, y):
                continue
            if x != y:
                assert y['rule_id'] == 'X1' and y['decision'] == 'exclude', (slug, y['id'])
                assert re.fullmatch(r'registry allocation: (?:NA|N/A|NON_RANDOMIZED|Non-Randomized)', y['span'], re.I), (slug, y)
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
