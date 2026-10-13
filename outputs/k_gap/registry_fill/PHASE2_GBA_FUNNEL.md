# k-gap phase 2: IQWiG / G-BA (AMNOG, section 35a SGB V), run 13 Oct 2026

**Terms, read first:**
- **G-BA** (https://www.g-ba.de/sys/impressum/) protects all content by copyright. Use beyond copyright's limits needs G-BA's or the author's consent; only citing and linking are permitted.
- **IQWiG** (https://www.iqwig.de/sonstiges/impressum/) likewise permits only citing its documents and linking to them.
- The Modul 4 dossiers are the manufacturer's work, published by G-BA.

Licence `GBA_IQWIG_CITE_AND_LINK_ONLY`: **typed only**. No G-BA or IQWiG text goes to a model; `regulatory_evidence` skips the document and `record_licence` would refuse it.

**Route** (`g1_regulatory_source.gba_urls`, no hand list):
1. G-BA's own search words (`suchworte.json`; the search is exact and case-sensitive) are matched to the INN by a typed rule.
2. The procedure pages hold the documents.
3. From each procedure, only the documents holding per-trial results are kept: Modul 4, the IQWiG benefit assessment, and IQWiG addenda.

Each document is held with sha256, URL and retrieval date, text layer only (never OCR).

| topic | AMNOG procedures (by INN) | docs held | missing after earlier phases | named | typed | read | admitted |
|---|---|---|---|---|---|---|---|
| pcsk9-mace | alirocumab, evolocumab | 19 | 9 | 9 | 0 | 0 (typed-only) | 0 |
| ticagrelor-vs-clopidogrel-acs | ticagrelor | 5 | 14 | 3 | 0 | 0 | 0 |
| omega3-cardiovascular-events | icosapent ethyl | 4 | 12 | 1 | 0 | 0 | 0 |
| metformin-pcos-ovulation | metformin (diabetes combination dossiers) | 28 | 30 | 0 | 0 | 0 | 0 |
| melatonin-primary-insomnia-sol | melatonin (paediatric) | 3 | 2 | 0 | 0 | 0 | 0 |
| 9 other gap topics | **none** (pre-2011 drugs and other products are not under AMNOG) | 0 | 73 | -- | -- | -- | -- |
| **total** | | 59 | 140 | 13 | 0 | 0 | **0** |

**Pilot finding (pcsk9): a located candidate that the gates refuse, with three named divergences.**

The alirocumab Modul 4A (doc sha256 98c79696..., text sha256 e67b2573...) holds two relevant tables:
- **Table 4-52:** per study and arm, the number of patients with any adjudicated cardiovascular event, with OR / RR / RD. It covers ODYSSEY FH I, FH II, HIGH FH and COMBO I, which are all gap trials.
- **Table 4-53:** the same events by component. This cannot be summed: patients with several events are counted more than once, as the table itself states.

Against the protocol, Table 4-52 diverges three ways:
- **estimand:** OR / RR / RD, while the protocol estimand is HR;
- **population:** the safety population, while the protocol is ITT (for example FH I alirocumab 322 v 323 randomised);
- **definition:** the composite includes heart-failure hospitalisation, which is outside the topic's MACE components.

The estimand mismatch alone is a typed refusal. **Not admitted. Not proposed as a divergence admission.** The lane copies no numbers from it; the table reference is the pointer.

IQWiG's alirocumab assessment (A15-47) adds context. It states that cardiovascular events were collected in the other included trials but not evaluated by the manufacturer, and calls this highly selective reporting. That is evidence the per-trial MACE counts exist, not a source for them.

**Defect found and fixed here: trial naming too loose** (`trial_names`, all agencies). A lone programme or fragment token named sibling trials: "ODYSSEY" named every ODYSSEY trial, "COMBO" in COMBO I also named COMBO II, and "JAPAN" named any Japanese trial. The gate's named-near-the-quote check uses the same names. A trial is now named by its whole acronym phrase, or by the phrase without its programme prefix when two or more tokens remain. Plant: `test_PLANT_a_programme_token_never_names_a_sibling_trial`. No regulator row was ever admitted, so no served number is affected. The FDA / EMA / NICE "named" counts are recounted under the new naming in PHASE2_SUMMARY.md.
