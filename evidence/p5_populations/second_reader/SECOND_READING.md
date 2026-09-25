# Blind second reading of the 53 P5 rows (2026-09-25)

**What was read.** All 165 (row, fact) records -- 147 RECOVERED, 3 ESTABLISHED_ABSENT, 15 UNRESOLVED -- by a reader
that saw the review's topic requirements and the trial's held documents (each projected to the trial's own record,
`make_packets.py`), and never saw evid2's state, EV53's interpretation, or which span the ledger cites.
Every quote a reader gave was re-found verbatim in the document file it named (`compare.py`); none was refused.

**Readers (disclosed).** 34 of 53 rows were read by codex `gpt-6-astra` (openai) -- 114 facts; the codex budget ran out
mid-run, so the other 19 rows (51 facts) were read by Claude subagents under the same brief and the same isolation
rules. Claude is the lane's own model family, so those 19 rows are a blind reading but NOT a cross-family one.
Per row: `SECOND_READING.json` -> `readers`. Two rows (P53-19, P53-42) were read by both: codex finished them just before its
runners were stopped, and a Claude batch then overwrote those two `out.json` files (my batching error). Codex's verdicts,
recovered from its logged command stream, are identical to the Claude readings kept; the counts below use the Claude files.

**Result (final, after the review-tightened comparison).** **163 of 165 facts agree with the ledger** (per reader:
codex 107 of 108; Claude 50 of 51; the 2 rows read by both 6 of 6). Two disagreements remain, both ruled for the ledger:

| row | fact | ledger | reader | ruling |
|---|---|---|---|---|
| P53-43 | randomized_contrast | RECOVERED | NOT_STATED | ledger stands: the registration defines exactly two arms with allocation RANDOMIZED, parallel |
| P53-50 | entry_population | ESTABLISHED_ABSENT | STATED | ledger stands: the reader's own note gives the ledger's reason (>=70 is a post hoc subgroup) |

History: P53-41 entry_population first read NOT_STATED (codex) -- **the reader was right about the span the ledger then
cited**. The evidence was corrected at the source (below), the row was re-read blind with the trial's own full text in
the packet, and now agrees. The first reading is kept (`readings/P53-41.v1_without_full_text.json`).

**Comparison rules** (tightened after a fresh-eyes review found `compare.py` accepted any `doc*` file in the folder and
one-word quotes): a quote must be at least 20 characters, in a file the packet LISTS, whose bytes equal the projection
re-derived from its recorded origin; AGREE only for the three declared state pairs; a NOT_STATED on a packet that lacks
a document the ledger cites is not counted as agreement (that rule is what caught P53-41's stale packet).

**The defect P53-41 exposed, fixed at the source.** `build_ledger.py` marked an entry fact RECOVERED whenever the evid
lane had ruled it ESTABLISHED and its span was re-found in the bytes -- which proves the words exist, not that they
state the fact. P53-41's span ("hospitalized patients were randomly assigned ...") never says the patients were on
antibiotics, which POLICY.md forbids inferring from the outcome's name. That branch now requires evid2's own
adjudicated span (`../entry_adjudications.json`), re-found in sha-pinned bytes. All 10 facts that used the branch were
re-adjudicated: 6 of evid's spans state entry as cited; 3 (P53-35/36/37) stopped before the clause that carries the fact
and now cite the full sentence; P53-41 now cites its own full text ("The trial population consisted of hospitalized
patients who were anticipated to take at least three days of any systemic antibiotic."; PMC2658588, free to read but
not open access, held local-only with its sha256). No state changed; 4 facts now rest on evidence that actually states them.

**Step 4 / 2b (POLICY.md amendment A).** 12 trials, 396 hits screened (`step4_screening/`); one candidate (RALES
rationale paper, PMID 8682055) fetched and read: no registration identifier, and its dose-ranging data are the RALES
pilot (a different trial). The ClinicalTrials.gov reverse lookup found registrations citing 3 of the 12 trials (P53-35, P53-39, P53-48), all as
BACKGROUND. The 15 UNRESOLVED facts stay UNRESOLVED with the stopping rule now fully reached.
