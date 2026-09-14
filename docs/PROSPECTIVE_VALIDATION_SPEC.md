# Prospective validation — freeze requirements and protocol (specified 2026-09-14)

This file records the requirements the external auditor has set for prospective validation of the search engine and the
harness, as REQUIREMENTS, so that whoever reaches freeze builds against the actual specification and not a summary. Where a
requirement is build work, its implementation status is stated with the file that carries it; a status is a claim, and
this document says what evidence backs it.

**Standing caveat, recorded at the auditor's request:** our claim of "frozen" will be treated as a claim requiring
evidence, on the strength of the fact that both the gate-authority fix and the artifact-identity fix contained defects
after we announced them (see `evidence/gate-authority-2026-09-14/`, `evidence/artifact-identity-2026-09-14/01-*`).

## Part A — requirements that are build work

### A1. Architecture identity is not a commit SHA
Two runs at the same SHA can execute materially different systems. The frozen identity MUST bind, as one computed value
that can be printed and checked:
- the commit SHA and tree SHA;
- dependency lockfiles or a container image digest (today: `requirements.txt` carries no exact pins and there is no
  lockfile — a mutable dependency until pinned);
- workflow and action versions (today: `uses: …@v4` tags, which are mutable refs — mutable until pinned to 40-hex SHAs);
- configuration (`topics/`, `protocols/`, `registry/`);
- model identifiers, provider, the most specific available snapshot/version, parameters, tool configuration and the
  verbatim prompts for ANY model-driven stage (see A5);
- retrieval-adapter versions and the external endpoints they call (mutable external dependencies, declared);
- the exact production build and deploy path (`.github/workflows/verify.yml`, the `deploy` job's `needs`/`if`).
Every prospective run records the identity. **A batch whose runs carry two different identities is a failed batch.**
Status: LANDED — `harness/architecture_identity.py` computes it (`python -m harness.architecture_identity`, `--check`);
it is carried in every production record from c6e1cdef. It names 31 mutable dependencies today (unpinned requirements,
tag-based action refs, external APIs, unpinned model snapshots); "frozen" cannot be claimed until those are pinned or
declared in the batch declaration. Not yet carried in retrieval-ledger snapshots.

### A2. Raw external inputs must be preserved, not only parsed records
Search APIs and websites change under a frozen architecture. Each run MUST retain: the raw retrieval responses as
received (bytes, HTTP status), the verbatim query strings, timestamps to the second, the adapter identity (module,
function, blob SHA) and the source snapshots — enough to tell "the system behaved differently" from "the world changed".
This extends the retrieval ledger (`harness/acquisition.py`): the ledger points at `raw/` under the snapshot directory.
Status: LANDED (f928a536) — every live fetch records each HTTP call raw (URL, params, status, body bytes, timestamp,
adapter identity + blob sha) under `raw/` beside the snapshot, indexed and hashed; legacy snapshots carry `raw_calls: 0`.

### A3. The defect ledger sits OUTSIDE the frozen architecture
During a batch, defects are appended; no commit, config, prompt, mapping table, query template or data-cleaning rule may
change — including ones that look harmless. If the ledger lived inside the frozen tree, recording a defect would modify
the system under test. Design: the batch defect ledger is an append-only store that the architecture identity does NOT
cover — an orphan branch of this repository (`prospective-defects`, written the way `production-records` is written by
CI: no checkout of the frozen tree, one JSON per defect, never rewritten) or an external store the custodian holds.
Appending must be possible without touching any path in A1's coverage. Status: DESIGNED, NOT BUILT.

### A4. No silent reruns — the rerun policy, written before any run exists
A crashed, timed-out or obviously-wrong run is part of the result. Policy, fixed now:
1. Every run is retained with all its artefacts (raw inputs, ledger, outputs, logs, exit state) and its identity.
2. A run that crashes, exceeds the predeclared time limit (to be set in the batch declaration, before the first run,
   and recorded there), or yields an obviously-wrong output is recorded as `FAILED` with the failure class. It COUNTS
   in every batch metric as a failure. It is never deleted, hidden, or replaced.
3. A rerun of the same topic is permitted ONLY when the failure is attributable to infrastructure outside the
   architecture (a network outage, a provider 5xx, a runner killed) AND the attribution is declared in the defect ledger
   BEFORE any output of the failed run is inspected. At most one rerun per topic. The rerun is a separate run with its
   own record; the original stays and is reported beside it. Reruns are counted and reported as reruns.
4. "Obviously wrong" is judged against predeclared invariants only (the harness gates and the census), never against
   the answer. A run that passes the gates and produces a surprising result is a result.
5. No human may select which failures to rescue after seeing outputs. Any deviation from 1–4 converts the batch to
   `FAILED prospective validation`.
Status: POLICY RECORDED; the batch declaration template (time limit, invariants) is to be written with A1.

### A5. Model-driven stages need more than a model name
If any stage calls an external model during a prospective batch, the architecture identity MUST bind the most specific
available model snapshot or version, the provider, the parameters and the tool configuration; a hosted model name does
not mean the underlying model is immutable. Complete requests and outputs are archived. If the provider cannot guarantee
an immutable snapshot, that component is declared a **mutable external dependency**, exactly as search APIs are.
Status: INVENTORY LANDED — `docs/model_stage_inventory.json`: 11 model-driven stages; NONE calls a model at build time
(every one reads a committed artefact produced earlier); providers Anthropic (Fable 5.1), OpenAI (GPT-5 via Codex),
Google (Gemini 3.1 Pro via AGY), plus a local sentence-transformers embedding; NONE is pinned to an immutable snapshot;
prompts are in the tree for none of the hosted-model stages; requests/outputs are archived only as the committed
output artefacts. Therefore every model-driven component is a MUTABLE EXTERNAL DEPENDENCY today, declared as such.

### A6. The eligibility universe is frozen and bound into the commitment
Otherwise the random draw stays fixed while what it was drawn from quietly changes. The custodian's commitment binds the
universe definition and its version (the enumeration the sample was drawn from, with its date and digest) as well as the
hidden sample. Status: PROTOCOL; the commitment format is to be agreed with the custodian before selection.

## Part B — protocol (not build)

### B1. Custody, release and termination
- The custodian controls release of held-out topics and issues `batch-complete`.
- A catastrophic system-wide defect discovered during a batch lets the custodian terminate the batch. Termination is a
  **FAILED prospective validation**, not licence to repair and continue.
- Ordering: (1) the custodian selects and commits the sealed set (and the frozen eligibility universe, A6);
  (2) we freeze and publish the architecture identity (A1); (3) the auditor tests the freeze claim; (4) release begins.

### B2. Release timing is a leak channel
Cadence tells us things even with the count secret, and our asking "is there another?" tells the custodian something.
Release timing follows a predeclared rule held by the custodian and does not respond to our requests. Our side MUST be
able to run a topic and return its package without initiating anything, and MUST NOT log or infer from inter-release
intervals. Requirement on the harness: a run is started by an external trigger carrying the topic; the harness records
the run's own timestamps (A2) but keeps no schedule, queue or "next expected" state.

### B3. Custody decision and its consequence for what we may claim
No external human custodian is available to us. Mahmood's decision: a blinded model acts as custodian. The auditor's
position: developer-controlled infrastructure gives tamper-evidence, not blinding. Both are right. Resolution, recorded so
it cannot be quietly upgraded later by someone who was not here:
- the mechanism is used, and the claim is downgraded;
- **the prospective test is never described as blinded, only as tamper-evident**;
- wherever a result of the prospective test is published, it carries this limitation in its own words in the body of
  the result, not in a footnote: "This prospective validation is tamper-evident, not blinded: the custodian ran on
  infrastructure the developers control."

### B4. What the held-out mechanism guarantees, and what it does not (from `harness/heldout.py`)
The in-repo component is a leak detector, not the register. Guaranteed: no identifier whose HMAC is sealed can land in a
tracked text file or a commit message after enforcement (CI runs the detector with the key; the ruleset makes CI
mandatory); the register's plaintext is not readable from the repository. Not guaranteed: anyone holding the key or the
external register can read the names; names not sealed are not protected; being told a name out of band is not
preventable. All 32 current topics are disqualified as prospective validation and remain the adversarial regression
corpus only.

## Part C — fix states, applied to today's claims (four-state rule)
`REPORTED` → `LANDED` (code on main, author-demonstrated) → `VERIFIED` (invariant independently demonstrated, not by the
test that was written with the fix) → `GENERALIZED` (holds on something the fix was not authored against). Mechanically
enforced on commits by `harness/fixstate.py`. Current states are stated in each evidence README under
`docs/evidence/`; an independent re-demonstration lane (Codex, fresh clone) is recorded under
`docs/evidence/independent-verification-2026-09-14/` when it lands and is the evidence the VERIFIED step requires.
