# LANE-FU-REPORT

## Status

- MEASURED base ref: `ad5e7c66`.
- MEASURED finish artifact: `LANE-FU-REPORT.md`.
- MEASURED no commit made.
- MEASURED final gate: `python -m pytest tests -x -q` passed.

All counts in tables below are MEASURED from local artifacts or commands unless the cell says otherwise.

## What Was Wrong

The funding detector was article-text only. It could classify a funding sentence already present in held abstract/full text, but it did not use local registry sponsor rows as a second source. That made source-backed industry/public sponsors render as funding-unknown when the article abstract was silent or the full text was not held. It also had no canonical funding object with `status`, `sponsor_class`, `sponsors`, `role`, `basis_span`, and `source_id`, so the page could not render held text and registry evidence side by side.

Mechanism fixed:

- `harness/aact.py`: added local AACT sponsor/responsible-party loading.
- `harness/funding.py`: now emits canonical funding objects, detects source-backed roles, flags industry authors without inferring sponsor status, merges held text plus registry sources, and preserves both sources when they disagree.
- `harness/page.py` and `harness/limitations.py`: render sponsor class, sponsors/roles, source evidence, and both disagreement sources in the funding block.
- `scripts/funding_sweep.py`: measures old rendered unknown rows against the lane base and current recovery, writes `docs/funding_sweep.json`.

## Plants

MEASURED plant tests added or strengthened in `tests/test_funding.py`:

- `test_registry_sponsor_second_source_recovers_abstract_silence`: asserts registry-only source becomes `status == "stated_in_registry"`, `sponsor_class == "industry"`, `source_id == "registry:NCT12345678"`, and the registry sponsor name is in `basis_span`.
- `test_registry_vs_abstract_disagreement_keeps_both_sources_renderable`: asserts held-text NIH funding plus registry Janssen sponsor sets `source_disagreement is True`, classifies as `mixed`, and keeps both `abstract:PMID 1` and `registry:NCT12345678`.
- `test_prefix_j_emphasis_unknown_funding_row_is_recovered_from_registry`: reads the base review from `ad5e7c66`, asserts the old row type starts `not stated`, then asserts current recovery for MEASURED source-backed ID `PMID 28824029` is `industry`, `registry:NCT01115855`, and Pfizer/Viatris-backed.
- `test_prefix_rely_unknown_funding_row_is_recovered_from_registry`: reads the base review from `ad5e7c66`, asserts the old row type starts `not stated`, then asserts current recovery for MEASURED source-backed ID `PMID 19717844` is `industry`, `registry:NCT00262600`, and Boehringer Ingelheim-backed.
- `test_scan_depth_distinguishes_fulltext_silence_from_abstract_only`: now asserts synthetic full-text silence becomes `status == "none_stated_in_held_text"` and `sponsor_class == "none_stated_in_held_text"`.
- `test_funding_pointer_to_supplement_is_not_silence`: now asserts a supplement-only pointer becomes `status == "in_source_not_held"`.

MEASURED pre/post plant rows:

```json
{
  "j_emphasis": {
    "id": "PMID 28824029",
    "before_base": {
      "type": "not stated (abstract only \\ufffd full text not retrieved)",
      "source": "abstract only",
      "scanned": "abstract only",
      "span": ""
    },
    "after_current": {
      "status": "stated_in_registry",
      "sponsor_class": "industry",
      "sponsors": ["Pfizer's Upjohn has merged with Mylan to form Viatris Inc."],
      "source_id": "registry:NCT01115855"
    }
  },
  "re_ly": {
    "id": "PMID 19717844",
    "before_base": {
      "type": "not stated (abstract only \\ufffd full text not retrieved)",
      "source": "abstract only",
      "scanned": "abstract only",
      "span": ""
    },
    "after_current": {
      "status": "stated_in_registry",
      "sponsor_class": "industry",
      "sponsors": ["Boehringer Ingelheim", "Population Health Research Institute", "Uppsala University"],
      "source_id": "registry:NCT00262600"
    }
  }
}
```

## Sweep

MEASURED `docs/funding_sweep.json` summary:

- MEASURED pooled review pages: 32.
- MEASURED pooled trial rows: 101.
- MEASURED old rendered funding-unknown rows recovered: 83.
- MEASURED pages with recovered rows: 31.
- MEASURED pages whose funding-count sentence changes: 17.
- MEASURED current sponsor-class distribution: industry 58, mixed 9, public 16, none-stated-in-held-text 18.

The sweep artifact also records all MEASURED pooled rows, per-page sponsor-class distributions, named recovered rows, and the MEASURED page list whose industry sentence changes.

## Rebuilt Pages

All MEASURED numbers in this table use `known/industry_or_tied/unknown/total`.

| Page | MEASURED recovered old unknown rows | MEASURED before | MEASURED after | MEASURED count sentence changed |
|---|---:|---:|---:|---|
| `balanced-crystalloids-vs-saline-mortality` | 2 | 1/0/1/2 | 2/1/0/2 | yes |
| `colchicine-postop-af` | 2 | 0/0/4/4 | 2/0/2/4 | yes |
| `colchicine-recurrent-pericarditis` | 2 | 0/0/2/2 | 2/0/0/2 | yes |
| `colchicine-secondary-cv-prevention` | 3 | 3/0/1/4 | 3/1/1/4 | yes |
| `corticosteroids-cap-mortality` | 3 | 2/1/1/3 | 3/1/0/3 | yes |
| `corticosteroids-covid19-mortality` | 1 | 1/0/0/1 | 1/0/0/1 | no |
| `dapagliflozin-hfpef-hosp` | 1 | 1/1/0/1 | 1/1/0/1 | no |
| `denosumab-vertebral-fracture` | 1 | 0/0/1/1 | 1/1/0/1 | yes |
| `doac-vte-recurrence` | 6 | 4/4/2/6 | 6/6/0/6 | yes |
| `dpp4-mace-t2d` | 3 | 1/1/2/3 | 3/3/0/3 | yes |
| `empagliflozin-hfpef-hosp` | 1 | 1/1/0/1 | 1/1/0/1 | no |
| `esketamine-trd-madrs` | 4 | 0/0/4/4 | 4/4/0/4 | yes |
| `finerenone-ckd-t2d-renal` | 2 | 2/2/0/2 | 2/2/0/2 | no |
| `glp1-ra-mace-t2d` | 8 | 8/8/0/8 | 8/8/0/8 | no |
| `iv-iron-hfref-hosp` | 2 | 0/0/2/2 | 2/1/0/2 | yes |
| `melatonin-primary-insomnia-sol` | 1 | 0/0/1/1 | 1/1/0/1 | yes |
| `metformin-pcos-ovulation` | 0 | 0/0/3/3 | 0/0/3/3 | no |
| `noac-vs-warfarin-af-stroke` | 4 | 3/3/1/4 | 4/4/0/4 | yes |
| `omega3-cardiovascular-events` | 6 | 5/2/2/7 | 6/6/1/7 | yes |
| `pcsk9-mace` | 2 | 2/2/0/2 | 2/2/0/2 | no |
| `probiotics-aad-prevention` | 6 | 2/1/14/16 | 6/3/10/16 | yes |
| `sacubitril-valsartan-hfref` | 1 | 1/1/0/1 | 1/1/0/1 | no |
| `semaglutide-obesity-mace` | 1 | 1/1/0/1 | 1/1/0/1 | no |
| `semaglutide-obesity-weight` | 2 | 1/1/1/2 | 2/2/0/2 | yes |
| `sglt2-ckd-progression` | 3 | 3/3/0/3 | 3/3/0/3 | no |
| `sglt2-hfref-hosp-cvdeath` | 2 | 2/2/0/2 | 2/2/0/2 | no |
| `sglt2-primary-prevention-hf` | 4 | 4/4/0/4 | 4/4/0/4 | no |
| `spironolactone-hfref-mortality` | 2 | 1/1/2/3 | 2/2/1/3 | yes |
| `statins-primary-prevention-elderly` | 2 | 2/1/0/2 | 2/1/0/2 | no |
| `ticagrelor-vs-clopidogrel-acs` | 2 | 0/0/2/2 | 2/2/0/2 | yes |
| `tocilizumab-covid19-mortality` | 3 | 3/2/0/3 | 3/2/0/3 | no |
| `tranexamic-acid-pph` | 1 | 1/1/0/1 | 1/1/0/1 | no |

`metformin-pcos-ovulation` had MEASURED zero recovered old-unknown rows, but its rebuilt bytes changed because the global funding/COI prose and table columns were updated to match the new evidence model.

## Reworded Blocks

MEASURED reworded block scope: all 32 canonical pages and their neutral blind harness pages have the `Funding / conflict-of-interest disclosure` block reworded.

Rewording:

- Before: funding was described as classified from a verbatim statement in the committed source.
- After: funding is described as classified from held text, with registry sponsor as a second source when available; held-text/registry disagreement renders both source spans; industry author affiliations are only flagged as affiliations, never sponsor evidence.
- Table columns changed from `Trial / Funding / Scanned / Verbatim statement` to `Trial / Funding / Sponsors / roles / Scanned / Source evidence`.
- Stored `FUNDING_COI` limitation objects were regenerated for all rebuilt reviews so page blocks and limitation-object blocks match.

No ratchet acknowledgements were written.

## Tests

MEASURED command outputs:

```text
python scripts\funding_sweep.py
83 trials rendered funding-unknown recovered of 101 pooled trials; 17 of 32 pages change
```

```text
python scripts\reproduce_review.py <31 recovered-row pages>
31/31 reproduce (all reproducible)
```

```text
python scripts\reproduce_review.py metformin-pcos-ovulation
1/1 reproduce (all reproducible)
```

```text
python -m pytest tests\test_funding.py tests\test_limitations_legacy_compare.py -q
21 passed in 18.47s
```

```text
python -m pytest tests -x -q
721 passed in 464.00s (0:07:43)
```

Intermediate MEASURED failure/fix: full-suite validation first reported `docs/fix_ledger.json is stale; run python scripts/render_fix_ledger.py`. I ran the documented generator, verified `tests\test_fixstate.py::test_real_store_validates`, and reran the final full suite above.

## Hardcode Disclosure

| Item | Classification | Disclosure |
|---|---|---|
| `FUNDING_SWEEP_BASE` default `ad5e7c66` | CLAIMED static lane baseline | Default is static for this lane, overridable by environment variable. |
| Sponsor class keyword mapping | CLAIMED static rule layer | Uses explicit rule strings plus AACT agency classes; it does not hardcode recovered trial outputs. |
| Sponsor names, NCT IDs, PMID IDs | MEASURED dynamic data | Read from held article text, committed cache records, and local AACT sponsor/responsible-party tables. |
| Page rebuild bytes | MEASURED dynamic output | Generated by `scripts/build_topic.py` from existing cache/protocol paths. |
| Sweep totals and page table | MEASURED dynamic output | Written by `scripts/funding_sweep.py` from base review JSON plus current rescans. |

## Not Done

- CLAIMED no network fetch was performed; recovery used local cache and local AACT snapshot data.
- CLAIMED no pooling, membership, screening, search, or risk-of-bias algorithm changes were made.
- CLAIMED no ratchet acknowledgement files were written.
- CLAIMED no commit, staging, stash, reset, checkout, or cleanup command was run.

## Files Changed Or Added

- Code: `harness/aact.py`, `harness/funding.py`, `harness/page.py`, `harness/limitations.py`, `scripts/funding_sweep.py`.
- Tests: `tests/test_funding.py`.
- Sweep artifact: `docs/funding_sweep.json`.
- Generated review artifacts: all 32 `docs/reviews/*/{review.json,index.html,manifest.json,REPRODUCTION.json}` pages.
- Generated neutral pages: all 32 changed harness-side `docs/m/*/index.html` pages corresponding to rebuilt reviews.
- Generated ledger/indexing side effects: `docs/fix_ledger.json`, `registry/blind_map.json`.
- Report: `LANE-FU-REPORT.md`.
