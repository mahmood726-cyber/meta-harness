# Comparator trial count (`theirs_k`): 16 served pages say "not stated"; each comparator abstract states it

**What is served.** On 16 review pages the comparator block reads:

> Legacy comparator extraction, theirs_k: not stated in the comparator abstract/full text.

**Why.** `harness.extract._parse_k` takes the **first** `_K` match only. When that match is a word and not a
count (e.g. "…identify **randomized controlled trials**…"), k is None and the pipeline writes "not stated"
(`harness/pipeline.py`, comparator block). `_K` also matches only "randomi[sz]ed (controlled) trials", "controlled
(clinical) trials" and "RCTs". It never matches "studies", "trials" alone or "CVOTs". Evidence:
`outputs/regex_layer/K_SHADOW.json`.

**Why not just fix the regex.** Compare the first count the abstract states with the source-verified `comparator_k`
held in 4 topic configs:
- pcsk9 12 and semaglutide-obesity-mace 16 agree;
- omega3 says **8** where the verified count is **28**.

A rule over the text is not reliable enough to serve.

**What was done instead: recorded proposals** (`registry/model_proposals/comparator_k.json`, frozen N = 38 from
`4d712dfa`).
- One model call per comparator abstract (gpt-6-astra via codex; recorded, replayable, byte-identical replay).
- The model returns the sentence and the count token **as written**. The verifier (`verify_comparator_k`) parses the
  number itself. Both the quote and the token must appear in the held text. The model supplies no digits of its own.
- **The 4 topics with a verified count are CONTROLS** (`control::<slug>`), counted apart from the 34 data items:
  **4 of 4 agree**, including omega3 = 28.
- On all 16 "not stated" pages the proposal is STATED, with a verbatim quote. For example, dapagliflozin: "We
  identified **six** RCTs…" (6); tranexamic acid: "…from **five** trials" (5); statins: "**Twelve** eligible
  observational studies" (12). The last means that comparator is observational, which is itself worth seeing.

**Plant fired first (#19).** The controls caught a verifier gap: "Twenty-eight" and "Forty-two" were refused as
unparseable, although the model had quoted the right counts. `parse_count` now reads compound count words under 100;
a token that is not a count is still refused.

**What changes a page:** nothing, until Mahmood signs.
- Every data proposal needs an **individual** signature (`NO_RULE_VALUE`: there is no rule value to agree with).
- Packet: `outputs/model_source/comparator_k_proposals.html` (38 signable = 34 data + 4 controls).
- A signed value would enter a topic config as `comparator_k` with its quote as `comparator_k_source`: the existing
  source-verified override path, so the pipeline code needs no change.
