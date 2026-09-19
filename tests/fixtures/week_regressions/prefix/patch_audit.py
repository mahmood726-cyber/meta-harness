from pathlib import Path
import difflib
import subprocess

root = Path.cwd()
out = root / '.tmp/patches'
out.mkdir(parents=True, exist_ok=True)
pin = root / '.tmp/prefix/adjustment/design_key.py'
pin.parent.mkdir(parents=True, exist_ok=True)
pin.write_bytes(subprocess.check_output(['git', 'show', '3f8add72^:harness/design_key.py']))

def patch(name, rel, transform):
    old = (root / rel).read_text(encoding='utf-8')
    new = transform(old)
    assert new != old
    (out / (name + '.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile='a/' + rel, tofile='b/' + rel)), encoding='utf-8')
    p = root / '.tmp/prefix/patched' / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(new, encoding='utf-8')

patch('harm-endpoint', 'harness/harms.py', lambda s: s.replace('        if not _matches(sent, terms):', '''        name = str(spec.get("name") or "").lower()
        folded = lexicon.fold(sent).lower()
        if "gastro" in name and not any(t in folded for t in ("gastrointestinal", "nausea", "vomiting", "diarrh")):
            continue
        if "discontinu" in name and not (any(t in folded for t in ("discontinu", "withdraw")) and any(t in folded for t in ("adverse", "side effect", "toxicity"))):
            continue
        if not _matches(sent, terms):'''))
patch('missing-family', 'harness/known_missing.py', lambda s: s.replace('    out: list[dict[str, Any]] = []\n    seen: set[str] = set()', '''    aliases = {str(row.get("trial_family_id")): key for key, row in screen.items() if row.get("trial_family_id")}
    out: list[dict[str, Any]] = []
    seen: set[str] = set()''').replace('        key = str(x.get("trial") or "").strip()', '        key = str(x.get("trial") or "").strip()\n        key = aliases.get(key, key)'))
patch('comparator-overlap', 'harness/comparator_second_pass.py', lambda s: s.replace('"shared_k": profile.get("shared_k", len(found)),', '"shared_k": None,').replace('"shared_trials": profile.get("shared_trials", found),', '"shared_trials": [],').replace('"only_ours": profile.get("only_ours", []),', '"only_ours": [],').replace('"only_theirs": profile.get("only_theirs", []),', '"only_theirs": [],'))
patch('screen-title', 'harness/screen.py', lambda s: s.replace('    if population_any and not popok:\n', '''    if population_any and not popok and _has(_text(rec), population_any):
        return ("review", "MANUAL_REVIEW", "Population appears in abstract; source eligibility adjudication required.", raw_all)
    if population_any and not popok:
''').replace('    if inc.get("intervention_any") and not matched_int:\n', '''    if inc.get("intervention_any") and not matched_int and _has_intervention(text, inc["intervention_any"]):
        return ("review", "MANUAL_REVIEW", "Intervention appears in abstract; source eligibility adjudication required.", raw_all)
    if inc.get("intervention_any") and not matched_int:
'''))
patch('reason-endpoint', 'harness/reason_audit.py', lambda s: s.replace('            if not _has_numeric_outcome(sent):', '''            if "major adverse cardiovascular" in (outcome_name or "").lower():
                if not any(term in sent.lower() for term in ("mace", "major adverse cardiovascular")):
                    continue
            if not _has_numeric_outcome(sent):'''))
