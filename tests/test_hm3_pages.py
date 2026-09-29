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
        # V1.0.1 (SGLT2-HFrEF review): a pinned registry record whose trial is now represented by its LINKED publication
        # (same trial family; the registry twin is dropped by dedup) is compared as that record
        b_ids = {str(x['id']) for x in b_recs}
        a_ids = {str(x['id']) for x in a_recs}
        a_recs = [dict(y, id=y['trial_family_id'], _linked_publication=y['id'])
                  if str(y['id']) not in b_ids and str(y.get('trial_family_id')) in b_ids - a_ids else y for y in a_recs]
        a_order = {str(y['id']): y for y in a_recs}
        a_recs = [a_order[str(x['id'])] for x in b_recs if str(x['id']) in a_order] +                  [y for y in a_recs if str(y['id']) not in b_ids]
        # V1.0.1 (semaglutide-weight review): on a topic whose exclusions are traced to the protocol (harness/rule_trace.py),
        # an exclusion by a term that traces to no protocol text becomes NEEDS_ADJUDICATION -- same record, rule
        # X-UNTRACED, and the reason names a term the topic's own trace lists as untraced
        untraced = set((after.get('rule_trace') or {}).get('untraced') or [])
        def _untraced_adjudication(x, y):
            return (x['id'] == y['id'] and x['decision'] == 'exclude' and y['decision'] == 'adjudicate'
                    and y['rule_id'] == 'X-UNTRACED' and any(f"'{t}'" in y['reason'] for t in untraced)) or (
                # V1.0.1 (SGLT2-HFrEF review): an arm LABELLED placebo that receives only background therapy is refused
                # at the comparison level (harness/comparison_contrast.py) -- the one allowed include -> exclude
                x['id'] == y['id'] and x['decision'] == 'include' and y['decision'] == 'exclude'
                and y['rule_id'] == 'X3-CONTRAST')
        # V1.0.1 (statins-older-adults review): design_key.registry_designs had overwritten registry records' ids with
        # AACT design-row ids. With the record intact, three things may differ from the pinned control, and only these:
        #  - an included registry record's completeness now comes from its own AACT status (the pinned value was the
        #    "publication record" fallback, which called RECRUITING / NOT_YET_RECRUITING trials 'completed');
        #  - a registry record's family label is its own registration ('REC:NCTx' -> 'NCTx', the same id);
        #  - a report's family is the parent registration recorded with evidence (cache/<slug>/parent_registrations.json)
        # and one include: an X2 on a registered condition the trial's own exclusion criteria refuse is withdrawn
        # (harness/condition_role.py, CONDITION_AS_OUTCOME)
        from harness import parent_registration, identity
        _rj = json.loads((ROOT/'cache'/slug/'records.json').read_text(encoding='utf-8'))
        held = {str(r.get('id')): r for v in _rj.values() if isinstance(v, list) for r in v if isinstance(r, dict)}
        parents ={k: v['nct'] for k, v in parent_registration.by_pmid(ROOT, slug).items()}
        completeness = ('completeness_basis', 'completeness_state', 'completion_date', 'registry_status',
                        'results_first_posted_date')

        def _condition_withdrawn(x, y):
            cr = y.get('condition_role') or {}
            return (x['id'] == y['id'] and x['decision'] == 'exclude' and x['rule_id'] == 'X2'
                    and y['decision'] == 'include' and cr.get('rule') == 'CONDITION_AS_OUTCOME'
                    and (cr.get('withdrawn') or {}).get('rule_id') == 'X2' and cr.get('prevention_targets'))

        # V1.0.1 (tocilizumab-COVID review): an X3 'no eligible comparator' becomes an include ONLY when the harness's
        # normalised comparator wording of the SAME held record matches a registered comparator term ('standard-of-care
        # (SOC)' -> 'standard of care'); re-proved here, never taken from the page
        from harness import screen as _screen, term_normal as _tn
        _inc = (json.loads((ROOT/'topics'/f'{slug}.json').read_text(encoding='utf-8')).get('include') or {})
        _terms = list(_inc.get('comparator_any') or []) + list(_inc.get('comparator_any_extra') or [])

        def _comparator_normalised(x, y):
            rec = held.get(str(y['id']).split('·')[-1].strip())
            return (x['id'] == y['id'] and x['decision'] == 'exclude' and x['rule_id'] == 'X3'
                    and str(x.get('reason') or '').startswith('no eligible comparator') and y['decision'] == 'include'
                    and rec is not None and not _screen._has(_screen._text(rec), _terms)
                    and bool(_screen._has(_tn.comparator_text(_screen._text_raw(rec), _terms), _terms)))

        def _normalised(x, y):
            y = dict(y)
            if (y.get('completeness_basis') == 'CT.gov status/results dates from local AACT snapshot'
                    and y.get('registry_status') and 'NCT' in str(y['id'])):
                y.update({k: x.get(k) for k in completeness})
                y = {k: v for k, v in y.items() if k in x or v is not None}
            rec = held.get(str(y['id']).split('·')[-1].strip())
            if (rec is not None and 'NCT' in str(y['id']) and x.get('publication_role') != y.get('publication_role')
                    and identity._role_from_record(rec) == y.get('publication_role')):
                # the registry record's role read from its OWN title ('... Heart Sub-study' is secondary)
                y['publication_role'] = x.get('publication_role')
            fx, fy = str(x.get('trial_family_id')), str(y.get('trial_family_id'))
            if fx == 'REC:' + fy or (fx.startswith('PMID:') and parents.get(fx[5:]) == fy):
                y['trial_family_id'] = x.get('trial_family_id')
            return y
        assert len(b_recs) == len(a_recs), slug
        assert all((x['id'], x['decision']) == (y['id'], y['decision']) or _untraced_adjudication(x, y)
                   or _condition_withdrawn(x, y) or _comparator_normalised(x, y) for x, y in zip(b_recs, a_recs)), slug
        for x, y in zip(b_recs, a_recs):
            if x != y and (_condition_withdrawn(x, y) or _comparator_normalised(x, y)):
                continue
            y = _normalised(x, y)
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
