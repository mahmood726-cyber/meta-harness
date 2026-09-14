# Gate authority tranche — proof ledger (2026-09-14)

**Arriving cold?** Read `VERIFY-COLD.md` first: it gives the anonymous API calls and expected values that confirm the
central finding (109053ad: verify failed, Pages deployed) without any narration from us.

**Fix state (four-state rule): VERIFIED** - re-demonstrated by a non-author agent from a fresh clone (`docs/evidence/independent-verification-2026-09-14/01-*`, `02-*`, `06-*`: the legacy-build-on-red-SHA finding, the deploy-gate refusal of a74b5c42, the evidence bytes). The server-side ruleset push rejection could NOT be re-tested there (`docs/evidence/independent-verification-2026-09-14/03-*`, no token) and stays LANDED. Not GENERALIZED: it has refused nothing it was not written against. Independent verification here means a second agent, not an external human party.

Every limb was shown to REFUSE before it was relied on, and shown to PASS on the clean case. Files are
raw captures (API read-backs, push transcripts, CI ledgers), not summaries.

| item | pre-fix failure (recorded) | fix | refusal (recorded) | clean case (recorded) |
|---|---|---|---|---|
| 1 Deploy conditional on verify | `01`: 109053ad — verify FAILED, legacy Pages build SUCCEEDED on the same SHA | Pages source → GitHub Actions (`02`); `deploy` job `needs: verify`, main only | `03`: plant a74b5c42 (failing test, hooks-free clone) → verify failure, deploy **skipped**, no deployment, served hash unchanged | `04`: revert 8af8dfb0 → verify success, deploy success, deployment 6439113037 |
| 2 Survives `git clone` | `03`: the server ACCEPTED a74b5c42 from a hooks-free clone | ruleset 23314494 on `main`: required check `verify`, no bypass, no force-push/deletion (`05`) | `06`: direct push of unchecked failing commit → `GH013 … "verify" is expected`; `07`: same SHA via branch, verified red → `"verify" is failing`; main unchanged | commit 3541540f landed only via branch → green → same SHA to main |
| 3 One standard (hook == CI) | `08`: old hook let a staged failing test through ("nothing to gate", exit 0); `10`: old CI **GREEN** on a hand-edited served `docs/index.html` | `scripts/verify_all.py`, called by both `.githooks/pre-commit` and `verify.yml` | `09`: new standard → `[REFUSED] index currency` / `[REFUSED] unit tests` (hook exit 1); `11`: CI on the same index plant → `[REFUSED] index currency`, deploy skipped, main rejects the SHA | commit 09c5c81b passed the new hook and the new CI, landed via branch → green → main |

## Deployment states (GATE_GAPS.md convention)
- Items 1–3: **LANDED_IN_CODE** (f1166baa, 3541540f, 09c5c81b on main) and **LANDED_IN_SERVED_BYTES**
  (deployments for f1166baa / 8af8dfb0 came from the `deploy` job; `03`/`11` show a red SHA is not served).
- **INDEPENDENTLY_VERIFIED**: not yet — an external party has not re-run these captures.

## What is NOT claimed
- The leak scan, honest-states and percentage-provenance checks were already in CI through pytest
  (`tests/test_leakscan.py` runs on the shipped docs); the named leak-scan limb is a naming change, not a new check.
- The hook runs against the working tree; with partially staged changes it can disagree with CI. CI is the authority.
- The ruleset cannot stop a repository admin from editing or deleting the ruleset itself; that is a settings
  audit item, not a gate. `gh api repos/mahmood726-cyber/meta-harness/rulesets` must keep returning id 23314494
  with `enforcement: active` and `bypass_actors: []`.
- A hooks-free clone `C:\mh-proof-clone` was used for the plants and is left in place as the proof workstation.
