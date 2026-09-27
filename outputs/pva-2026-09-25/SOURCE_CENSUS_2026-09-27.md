# Source-preservation census -- every held PubMed record vs PubMed now (pva, independent lane, 27 Sep 2026)

**To: the evidence lane (evid) and the release captain. Report only; nothing in the repository was changed.**

## Question
An external reviewer of the DPP-4 topic found that the held OMNeON abstract (cache/dpp4-mace-t2d/records.json, PMID 28893244)
is abridged. Is it the only one, where did it come from, and does any served "not reported" claim rest on missing text?

## Method
- Commit measured: **main 9eacfe09d411 (V1, live)**.
- Population: every record in every top-level `cache/<slug>/records.json` (38 files; 32 served topics plus 6 unserved caches):
  **3,330 held PubMed records, 3,217 distinct PMIDs**. Excluded and not compared, by name: 61 full-text files
  (`cache/<slug>/ft_*`) and the dated search snapshots (`cache/<slug>/snapshots/*`, the search record, not the held evidence).
- Source: PubMed efetch (XML) on 27 Sep, 22 batches; every raw body kept with its sha256, byte count, URL and UTC time
  (`source_census/fetch_ledger.json`, bodies in `source_census/raw/*.xml.gz`).
- Comparison: each fetched abstract rebuilt with **the harness's own formatter** (`harness/fetch.py::_efetch` at 9eacfe09: each
  AbstractText as `Label: text`, joined by single spaces), then exact-byte, then whitespace/Unicode-normalised, then
  label-stripped word-level diff. Scripts: `source_census.py`, `census_detail.py`, `census_trace.py`.

## Result: 8 of 3,330 held records differ from PubMed in content or labels; 2 are abridged

| class | n | records |
|---|---|---|
| identical bytes | 3,319 | |
| whitespace/Unicode only | 3 | |
| **abridged and edited** (hand-entered condensed text) | **2** | OMNeON 28893244 (dpp4-mace-t2d); SOUL 40162642 (glp1-ra-mace-t2d) |
| section labels missing, every word identical | 3 | pcsk9-mace: 41211925, 25773378, 27846344 |
| PubMed revised the abstract after it was held | 3 | semaglutide-obesity-weight 42610271; spironolactone-hfref-mortality 41955577, 41831311 |

**Both abridged records are pooled in a served primary result**, and the pattern is the same in both: section labels stripped,
per-100-person-year rates cut from the result sentences, and secondary, safety and trial-conduct sentences dropped.

### OMNeON, PMID 28893244 (dpp4-mace-t2d) -- held 172 words, PubMed 318; 151 words removed, 5 added
Sentences missing from the held text (PubMed wording):
- "Subsequently, a business decision was made not to submit a marketing application for omarigliptin in the United States, and
  the CV safety study was terminated. Herein we report an analysis of data from that early-terminated study."
- the definition of the second endpoint: "... and the analysis of first event of hospitalization for heart failure (hHF)."
- "The hHF outcome occurred in 20/2092 patients in the omarigliptin group (0.96%; 0.51/100 patient-years) and 33/2100 patients in
  the placebo group (1.57%; 0.85/100 patient-years), with an HR of 0.60 (95% CI 0.35, 1.05)."
- the HbA1c difference at 142 weeks, the adverse-event sentence, and "Registered 05 October 2012."
Edited in place: "(range 1.1-178.6 weeks)" dropped; "2.96/100 patient-years" and "2.97/100 patient-years" dropped; the conclusion
"did not increase the risk of MACE or hHF and was generally well tolerated" shortened to "did not increase the risk of MACE."

### SOUL, PMID 40162642 (glp1-ra-mace-t2d) -- held 165 words, PubMed 321; 161 removed, 5 added
Missing: the whole BACKGROUND; the entry criterion "with a glycated hemoglobin level of 6.5 to 10.0%"; the confirmatory secondary
outcomes and their result ("did not differ significantly"); follow-up ("mean 47.5±10.9 months, median 49.5 months"); the event
rates "3.1 / 3.7 events per 100 person-years"; "The incidence of serious adverse events was 47.9% ... and 50.3% ...; the incidence
of gastrointestinal disorders was 5.0% and 4.4%, respectively."; the conclusion's "without an increase in the incidence of
serious adverse events". Two sentences are merged into one (randomisation + result).

## What the served pages say because of it (V1, live)
- **dpp4-mace-t2d**: OMNeON is one of the k = 3 in the served primary MACE pool (HR 1.0074, 0.8391-1.2094). The page states, for
  OMNeON's *Hospitalization for heart failure*, `OUTCOME_NOT_IN_SOURCE`, audited `REASON_TRUE` -- "value absent from every held
  source inspected". **That is false of the source**: the abstract reports hHF, HR 0.60 (0.35, 1.05). It is true only of the
  condensed copy. The page's hHF outcome is served with k = 1.
- **glp1-ra-mace-t2d**: SOUL's *Gastrointestinal adverse events* is stated `OUTCOME_NOT_IN_SOURCE` / `NOT_IN_HELD_SOURCES`.
  **False of the source**: 5.0% vs 4.4%. (SOUL's *Adverse events leading to discontinuation*, also stated absent, is NOT shown to
  be wrong: the removed text gives serious adverse events, not discontinuations.)
- Earlier measurement on the branch below: with the true OMNeON abstract the binder refuses omarigliptin, and the served DPP-4
  primary pool goes **k 3 -> 2, HR 1.0074 -> 1.0082**; GLP-1 moves no value.

## Where it came from (git history of each record's bytes)
| record | entered | by | code path |
|---|---|---|---|
| OMNeON 28893244 | **2355a306**, 13 Sep 23:44, "RECOVERY (source-verified): omarigliptin into dpp4-mace-t2d, k=2->3" | author mahmood726-cyber | **none**: the commit changes no code; the text was written into records.json by hand (retrieval ledger `legacy_unrecorded`) |
| SOUL 40162642 | **ef0d0e6b**, 13 Sep 23:59, "RECOVERY: SOUL into glp1 (k=7->8) ..." | same | hand-entered; the commit touches harness/extract.py, not the fetcher |
| PCSK9 x 3 (labels only) | **dd2403f5**, 16 Sep, "Landing 2 (Codex lanes ...)" | same | not harness/fetch.py (which always writes labels); the words are PubMed's, the source formatter is unrecorded |
| semaglutide 42610271 | accfacc5, 12 Sep, fetched through harness/fetch.py | | PubMed revised it later: the held copy says "receptor **antagonist**" where PubMed now says "agonist" |

"Who" beyond the commit author is not recorded: the retrieval ledger marks both condensed records `legacy_unrecorded`, and no
raw fetched body was held for them.

## This was found before, and the fix is not in V1
**origin/ws/HELDTEXT, e5110d95 (19 Sep)** -- "the two condensed hand-entered abstracts replaced by fetched PubMed text with
recorded raw bodies ... omarigliptin leaves the dpp4 pool (k 3 -> 2)" -- is marked **DECISION NEEDED before landing** and is **not
an ancestor of main**. Its own corpus sweep (214 record-uses on 32 reviews) found the same two. This census, over all 3,330
held records, finds **no third** abridged record. The branch's replacement texts equal PubMed today after whitespace/Unicode
normalisation, at the same length (2,167 and 2,283 characters); they are not byte-identical to today's rebuild.

## Decision needed (not this lane's)
The DPP-4 served result moves if the true OMNeON text is held (k 3 -> 2): a served-number change, so it needs a signed notice.
ws/HELDTEXT names two resolutions (accept the binder's refusal, or extend the binder with its own plant) -- Mahmood's call.
Until then, the two "not in source" claims above are false statements on the live site and should at least be disclosed.

## Limits of this census
- 61 full-text files were not compared (no second full-text source was fetched); the 3,330 abstracts were.
- A difference from PubMed *today* is not proof of tampering: 3 records differ because PubMed revised them after they were held.
- The OMNeON and SOUL judgements rest on word-level diffs of the full texts, not on the keyword screen; the keyword screen only
  pointed at which served claims to read.
