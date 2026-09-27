# V1.1 discovery -- denosumab-vertebral-fracture: recall of the registered title query

Registered PubMed search (topics/denosumab-vertebral-fracture.json): FREEDOM by uid, plus
`denosumab[Title] AND prevention[Title] AND fractures[Title] AND postmenopausal[Title] AND osteoporosis[Title]`,
which returns **2** records. A broader query -- denosumab x (postmenopausal / osteoporosis / bone mineral density /
osteopenia) x randomized-controlled-trial publication type -- returns **229**.
- The code is `recall_test.py`, run through the harness's own PubMed adapters; raw results are in
  `run/recall_fetch.json` (sha256 recorded), the result is `run/RECALL_RESULT.json`, and the plants are
  `tests/test_discovery_denosumab_recall.py`.
- Nothing here changes a served page or the topic config.

## What the title query cannot find
- **Koh 2016 (PMID 27189284, NCT01457950)** -- the review's named case. It is a Korean placebo-controlled denosumab
  RCT, and its title and abstract are about bone mineral density: the primary endpoint is lumbar-spine BMD at
  6 months. Its abstract **does not mention fractures**, so no abstract screen can see its fracture data. Those have
  to come from its registry record (NCT01457950). On the live page that record sits in the search audit's
  `results_only_ncts`, a label applied before the registry ID was resolved against this publication (the V1.0.1
  linking fix).
- **DIRECT (PMID 24646104)** -- a placebo-controlled phase 3 fracture RCT whose *primary endpoint* is new or worsening
  vertebral fracture (HR 0.343, 95% CI 0.194-0.606). Its title reads "fracture risk reduction ... (DIRECT)" rather
  than "prevention ... fractures", so the five-term title query misses it. It enrolled women AND men; whether it is
  eligible is a separate screening question, but the search must find it.
- The broad-only set has **35** records that are placebo-controlled RCTs mentioning vertebral fractures.
  - Most are FREEDOM secondary or extension reports, or trials in men or of romosozumab (screening handles those).
  - The two above are distinct trials the registered query cannot reach.

## For the discovery strategy
A title-AND query over outcome words ("prevention", "fractures") is structurally blind to trials whose title and
abstract name a surrogate endpoint (BMD) and report fractures elsewhere. Recall for this topic needs:
- a population x intervention x design query, with outcome words never in the title field;
- registry-to-publication linking, so a BMD-titled trial's fracture results are found through its registry record.
