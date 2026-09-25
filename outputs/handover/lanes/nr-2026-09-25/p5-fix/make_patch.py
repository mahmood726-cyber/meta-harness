"""Write the proposed P5 fix as a real patch to harness/trial_family.py at 1fa77f2c (NOT applied on any branch)."""
from pathlib import Path

src = Path(r"C:/mh-lanes/nr/work/tf_1fa77f2c.py").read_text(encoding="utf-8")
s = src

# FIX-B: randomised_contrasts learns the review's DECLARED comparators
old = '''def randomised_contrasts(arms, agents, randomized=False):
    """Compare COMPLETE linked arm intervention sets; same-drug dose trials fail.

    Missing linkage cannot be treated as placebo. Shared background must be
    explicitly represented by both arms. Matching placebo has no active drug.
    """
    if not randomized:
        return []
    out = []
'''
new = '''def randomised_contrasts(arms, agents, randomized=False, comparators=()):
    """Compare COMPLETE linked arm intervention sets; same-drug dose trials fail.

    Missing linkage cannot be treated as placebo. Shared background must be
    explicitly represented by both arms. Matching placebo has no active drug.
    An arm pair that differs by the agent on one side and by a comparator the
    protocol DECLARES (include.comparator_any) on the other, with identical
    background, is also a randomised contrast: without this, no drug-vs-active-drug
    trial (NOAC vs warfarin, ticagrelor vs clopidogrel, sacubitril/valsartan vs
    enalapril) could ever be shown to contrast what the review compares.
    """
    if not randomized:
        return []
    out = []
'''
assert old in s
s = s.replace(old, new)
old = '''            out.append({'arm_ids':[a['arm_id'], b['arm_id']], 'drug':agent,
                        'background_therapy':sorted(av-aa), 'span':[a['span'], b['span']]})
    return out
'''
new = '''            out.append({'arm_ids':[a['arm_id'], b['arm_id']], 'drug':agent,
                        'background_therapy':sorted(av-aa), 'span':[a['span'], b['span']]})
    if not comparators:
        return out
    seen = {(frozenset(c['arm_ids']), c['drug']) for c in out}
    hit = lambda term, values: {v for v in values if re.search(r'(?<!\\w)'+re.escape(term.lower())+r'(?!\\w)', v)}
    for a, b in itertools.permutations(arms, 2):
        if not a.get('linkage_complete') or not b.get('linkage_complete'):
            continue
        av, bv = set(a['active_interventions']), set(b['active_interventions'])
        for agent in agents:
            aa = hit(agent, av)
            if not aa or hit(agent, bv):
                continue
            cb = set().union(*[hit(c, bv) for c in comparators])
            if not cb or set().union(*[hit(c, av) for c in comparators]) or av-aa != bv-cb:
                continue
            key = (frozenset([a['arm_id'], b['arm_id']]), agent)
            if key in seen:
                continue
            seen.add(key)
            out.append({'arm_ids':[a['arm_id'], b['arm_id']], 'drug':agent, 'comparator':sorted(cb),
                        'background_therapy':sorted(av-aa), 'span':[a['span'], b['span']]})
    return out
'''
assert old in s
s = s.replace(old, new)
old = "        agents = list((config.get('include') or {}).get('intervention_any') or config.get('intervention_terms') or [])\n"
new = old + "        comparators = list((config.get('include') or {}).get('comparator_any') or [])\n"
assert old in s
s = s.replace(old, new)
old = "'randomised_contrasts':randomised_contrasts(arms, agents, held.get('randomized',False)),"
new = "'randomised_contrasts':randomised_contrasts(arms, agents, held.get('randomized',False), comparators),"
assert old in s
s = s.replace(old, new)

# FIX-A: the population test reads the registry's conditions the way screening reads the terms
old = "    if inc.get('population_any') and not any(t.lower() in text for t in inc['population_any']):\n"
new = "    if inc.get('population_any') and not population_matches(inc['population_any'], conditions):\n"
assert old in s
s = s.replace(old, new)
old = "def screen_family(family, config):\n"
new = '''def population_matches(terms, conditions):
    """The protocol's population terms against the registry's conditions, folded as screening folds them
    (lexicon.fold). A term ending in '*' is the protocol's truncation (PubMed honours it at search time) and
    matches as a prefix; a condition written in MeSH inverted form 'X, Y' is also read as 'Y X'
    ('Diabetes Mellitus, Type 2' -> 'type 2 diabetes mellitus'). Only ever ADDS matches to the plain
    substring test it replaces."""
    from . import lexicon
    texts = []
    for c in conditions:
        f = lexicon.fold(str(c))
        texts.append(f)
        if ', ' in f:
            head, tail = f.split(', ', 1)
            texts.append(tail + ' ' + head)
    text = ' | '.join(texts)
    for t in terms:
        f = lexicon.fold(str(t))
        if (f[:-1] in text) if f.endswith('*') else (f in text):
            return True
    return False

def screen_family(family, config):
'''
assert s.count(old) == 1
s = s.replace(old, new)
Path(r"C:/mh-lanes/nr/work/tf_patched.py").write_bytes(s.encode("utf-8"))
print("ok")
