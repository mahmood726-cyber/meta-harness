# k-gap identification queue (13 Oct 2026): 22 missing trials with no PMID and no registration

These trials cannot enter any source phase until they have an identity: a PMID, NCT, DOI or other registry id.

| group | n | trials | next identification route |
|---|---|---|---|
| IDENTIFIED_NOT_INDEXED: the comparator's reference is known (k_gap_table citation chase), but it is not in PubMed | 19 | metformin: Begum 2014, Chuni 2006, Fatima 2018, Heathcote 2013, Karimzadeh 2007, Ko 2001, Refaie 2005. probiotics: Helps 52, Horosheva 23, Iamharit 54, Khanal 55, Pirker 60. ticagrelor: refs 24, 26, 29, 30, 39, 40, 41 | Crossref / DOI lookup from the held reference string; then the phase-3 open-text census by DOI |
| acronym only, no reference resolved | 2 | COVINTOC, PreToVid (tocilizumab) | PubMed / registry search by acronym. COVINTOC: PubMed `COVINTOC OR (tocilizumab AND Soin[au] AND 2021[dp])` returns 33676589 and 34228774, **candidate identities to verify, not adopted**. PreToVid: no PubMed hit (Dutch trial; try the Netherlands Trial Register / medRxiv) |
| two independent metas, no reference resolved | 1 | Sarzaeem [23] (colchicine post-op AF) | the comparator's reference [23] |

## Identity defects found in the comparator labels (not changed by the lane)

- **ODYSSEY JAPAN** is labelled 'NCT02017898', and the registry answers 404. The trial is **NCT02107898** (registry search "ODYSSEY JAPAN alirocumab": brief title names ODYSSEY JAPAN; has posted results).
- **corticosteroids-cap** has a trial labelled "Ampicillin dosage and use ..." (PMID 4404939). The label reads like a reference title, not a trial. It needs an identity check.
