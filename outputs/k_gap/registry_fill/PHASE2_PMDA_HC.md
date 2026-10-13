# k-gap phase 2: PMDA and Health Canada (13 Oct 2026). No route can be run by the lane

## PMDA (Japan)

**Terms**, read 13 Oct 2026 at https://www.pmda.go.jp/english/0013.html:
- **Licence.** Content is under the **Public Data License 1.0 (PDL 1.0)**, with source citation required and edits marked as edits. PDL 1.0 is the Japanese government open-data licence and is designed to be compatible with CC BY 4.0.
- **Retrieval.** "Automated crawling or download applications are also not permitted." Bulk or frequent downloads are prohibited, and downloads must be "the minimum necessary".

**Consequence:**
- **No automated route is built.** A harness script fetching review reports would breach PMDA's terms.
- **Licence ruling needed.** Until Mahmood or the Captain rules on PDL 1.0 for prompts (D8 admits CC BY / CC0; FDA public domain and EMA with acknowledgement were admitted by Mahmood's word), PMDA text is typed-only.

**Pilot documents identified.** These are English review reports from PMDA's own listing (review-services/reviews/approved-information/drugs/0001.html), found by browsing it once, by hand:

| product | report | file | size | gap trials it may hold |
|---|---|---|---|---|
| Praluent (alirocumab) | July 2016 | https://www.pmda.go.jp/files/000224582.pdf | 1.04 MB | ODYSSEY JAPAN (a Japanese trial; posted results exist under NCT02107898) and the other ODYSSEY trials |
| Repatha (evolocumab) | January 2016 | https://www.pmda.go.jp/files/000217925.pdf | 553 KB | DESCARTES, GLAGOV (by date, DESCARTES only) |
| Actemra (tocilizumab) | January 2022 partial change (COVID-19) | https://www.pmda.go.jp/files/000246328.pdf | 945 KB | COVID-19 tocilizumab trials |
| Brilinta (ticagrelor) | none | -- | -- | no English review report listed |

**Needs Mahmood:**
1. permission for these three single downloads (minimum necessary, by hand, not a crawler);
2. a ruling on PDL 1.0 for prompts.

Once downloaded, the harness holds each by file (sha256, URL, retrieval date) for the typed reader.

## Health Canada (Clinical Information portal)

The portal releases clinical data only to registered users who accept its terms. The lane cannot create accounts or accept terms on anyone's behalf, so this route is **blocked on an account**. That is for Mahmood, as already flagged.

## NICE, IQWiG / G-BA

See PHASE2_NICE_FUNNEL.md and PHASE2_GBA_FUNNEL.md.
