# Shared acquisition-cascade defects found by the tocilizumab G1 lane (for the Captain lane to route)

Not patched here: the shared cascade (`harness/fetch.py`, `harness/http.py`, `kgap/`, `scripts/k_gap_*`) is owned by the
Captain lane. Each defect below was measured on the tocilizumab topic. The lane-side runner `scripts/g1_toci_cascade.py`
works around each one, with its log in `g1/data/cascade/`.

| id | where | defect | measured effect | evidence |
|---|---|---|---|---|
| C1 | topic build (`harness/fetch.py` `_run_with_recorder`, `config["fulltext"]`) | `topics/tocilizumab-covid19-mortality.json` has no `fulltext` key, so the PMC full-text rung is **NOT_RUN** for the whole topic | RECOVERY's own report (PMID 33933206, PMC8084355, CC BY 4.0) was never fetched; only its abstract was held. Every "no open primary source" verdict downstream rested on a rung that never ran | `cache/tocilizumab-covid19-mortality/` has 9 `ft_*.txt` files and none for 33933206. The lane cascade's R1 returns `OPEN_FULL_TEXT` for it. Plant Q10 |
| C2 | `harness/fetch._pmc_fulltext` | `except Exception: return ""`: a failed fetch is indistinguishable from "not in PMC", and nothing is logged | a throttled or failed rung reads as "no full text" | code, lines 195-215 |
| C3 | `harness/http.get_raw` | HTTP 429 is retried after only 0.5/1/2 s, with no `Retry-After`, then raised, and callers swallow the error (C2) | the PMC idconv service now answers 429 under modest load. The first lane run logged 429 on R1 for 17 of 50 primary-report candidates | `g1/data/cascade/*.json` (first run, `idconv_http: 429`) |
| C4 | `kgap/k_gap.py:77`, `scripts/k_gap_counterfactual.py:124`, `scripts/k_gap_table.py:475`, `scripts/comparator_correctness_sweep.py:392` | the old idconv URL `www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/` now returns **301** to `pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/` | works only while the redirect is followed. The new host rate-limits (C3) | probe, 2026-10-02 |
| C5 | topic build | there is no rung for Europe PMC full text, Unpaywall (trial reports) or ISRCTN | e.g. COVIDSTORM's own report (PMID 35259529) is open in Europe PMC (R1 was throttled); TOCOVID's (33121497) likewise. RECOVERY's ISRCTN record lists its tocilizumab report | `g1/data/cascade/CASCADE.md` |
| C6 | binding of found papers to trials (any cascade) | a paper found by searching a trial's registration is not that trial's report. Europe PMC full-text search and AACT `DERIVED` references return papers that only cite it | ARCHITECTS and COVIDOSE2 returned the same two unrelated papers; RECOVERY's search returned a case report and a mechanism paper. Without a binding rule their numbers would be read as trial rows | `scripts/g1_toci_cascade.binding`, plant Q11 |
