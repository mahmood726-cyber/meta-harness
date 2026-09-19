# LANE CON — one defect, one increment on the served harness (base ca63b7cf = main, increment 3): the registered protocol's B-prime prose is not ENFORCED. Every clause compiles to a constraint object with a status the page renders: IMPLEMENTED (with the code path that enforces it and a test) / REQUIRES_ADJUDICATION / UNIMPLEMENTED. No clause is ever claimed IMPLEMENTED without a test that fails when its enforcement is removed.

Report file: `LANE-CON-REPORT.md`. Fresh checkout of main at ca63b7cf. Record `git rev-parse HEAD`. Never reset/checkout/stash. No commit.
No network. Extend `harness/protocol_compiler.py` (exists: `eligibility_clause`, `eligibility_rule_sentence` -- keep them), `harness/page.py`
(one hook after the Protocol comparison block), `harness/gate.py` (a page whose constraint registry is missing or stale refuses) --
existing modules only.

## Sources to read, not copy blindly
Lane AUD3 built this on the landing-4 candidate tree (parked at `F:\claude-temp\lanes-parked\mh-r-AUD3`: read `LANE-AUD3-REPORT.md`
sections "MEASURED changes" and "Plants", its `harness/protocol_compiler.py`, `registry/protocol_constraints/glp1-ra-mace-t2d.json`
(24 clauses: IMPLEMENTED 4 / REQUIRES_ADJUDICATION 4 / UNIMPLEMENTED 16), `tests/test_protocol_constraints*.py`). That tree is ~740
paths from this base and its compiler leaned on modules this base does not have (effect_type, strands declarations): re-derive what
this base can enforce. An independent Gemini audit of AUD3's registry (`C:\mh-base\outputs\handover\agy\protocol_constraints_audit_aud3_2026-09-18.txt`)
found 3 OVER-CLAIMS (clauses marked IMPLEMENTED without enforcement), 1 CONTRADICTION and 11 MISSING clauses: every one must be
resolved in your registry (downgrade the over-claims to their true status; add the missing clauses; resolve the contradiction) and
listed in the report with its resolution.

## Required end state
1. `registry/protocol_constraints/glp1-ra-mace-t2d.json` generated at build time from the committed protocol prose
   (`protocols/glp1-ra-mace-t2d*.md` and its amendments) by `protocol_compiler.compile(md_text)`: one object per clause with
   `clause_id`, verbatim `span` (tested to be a substring of the protocol), `status` in IMPLEMENTED / REQUIRES_ADJUDICATION /
   UNIMPLEMENTED, and for IMPLEMENTED the `enforced_by` (module.function) and `test` (test node id) that prove it.
2. A clause is IMPLEMENTED only if removing its enforcement makes the named test fail (prove it for every IMPLEMENTED clause by
   a mutation run recorded in `.tmp/con/implemented_mutations.txt`: comment out / bypass the enforcement, run the test, restore).
3. The glp1 page renders the conformance table (every clause, its status, its enforcement or the reason it is not enforced); the
   headline gains no numeral. Other topics: render the same table if they have a protocol; a topic with no compiled clauses renders
   "no compiled constraints" -- never an empty pass.
4. `gate.py`: a page whose constraint registry is missing, or whose protocol sha differs from the one the registry was compiled
   from, refuses with a typed reason.

## Plants (FIRST, untouched base; `.tmp/con/prefix_pytest.txt`) -- `tests/test_protocol_constraints_enforced.py`
- the glp1 page carries no conformance table and no clause status (FIRES);
- a protocol clause the page claims to satisfy (e.g. the ascertainment axis, the 3-point endpoint identity, the no-fingerprint rule)
  has no registry object naming its enforcement (FIRES);
- the registry, once generated, has zero clauses marked IMPLEMENTED without an `enforced_by` + `test` (HOLDS by construction --
  assert it anyway);
- span verbatim test: every clause span is a substring of the committed protocol text.
Record FIRED / HELD per case; a fix that clears every failure is a loosened test.

## Then
Rebuild all 32 (`--now 2026-09-11`); record which `review_sha256`/`html_sha256` moved and why; `python scripts/retraction_survival.py
ca63b7cf` => 32 of 32 or STOP; targeted pytest counts; full `python -m pytest tests -q -p no:cacheprovider` if time allows (counts
verbatim; every failure explained); list every honest-ratchet block that changes with a proposed reason (unsigned).

## Report (MEASURED / INFERRED / CLAIMED; `n of N`)
The clause table (id, status, enforcement, test, mutation result), the audit-finding resolutions (3+1+11), pages moved, what the
increment does NOT establish. Never a backslash escape through a heredoc; write regexes to files; LF line endings. No commit.
