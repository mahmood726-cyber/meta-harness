# Topic 21 independent audit — statins for primary prevention in older adults
Audit date: 10 October 2026.
Pinned repository: mahmood726-cyber/meta-harness @ 0730234d0b4f.
Recorded review SHA-256:
5aefb00dba8541a6221ec1a4e985b6a7fe25dad9295009bdd1489a0df4a78b5b

## Main result
The two current inputs give pooled HR 0.680288, rounding to the served HR 0.68.
Both supplied passage hashes match. The registered k=2 HKSJ interval is withheld
on the inspected manuscript; the independently calculated interval in results.json
is diagnostic, not a claim that this interval is served.

Adding the reported PROSPER primary-prevention subgroup gives diagnostic HR
0.745723 (HKSJ 95% CI 0.436571–1.273796; I2 73.917%). This is NOT an admitted
replacement result or a complete corrected systematic review. Endpoint definitions,
subgroup policy, source admissibility and other eligible evidence still require review.

## Main findings
1. The JUPITER >=70 cut-point was chosen after trial completion, not prespecified.
   The source's prespecified outcomes do not make the age-cut-point analysis prespecified.
2. PROSPER's 'at risk of vascular disease' title is not evidence that its no-prior-disease
   subgroup has established disease. The title blacklist is implemented policy, but does
   not correctly express the review's subgroup-capable primary-prevention PICO.
3. Protocol/configuration RR and rendered HR describe different estimands.
4. Comparator documentation names different sources; full change history was not recovered.
5. Original JUPITER Table 3 offers a muscle-symptom extraction route, not yet admitted here.

## Reproduce the independent checks
From this directory:
    python -m pip install -r requirements.txt
    python audit_topic21.py

The script reads inputs.json and rewrites results.json. It needs no network itself.
Runtime package versions are recorded in results.json. Ten self-checks passed
when run here; checks using manual metadata fixtures are explicitly labelled.
They are NOT tests of the repository's production gates.

## Acquisition and verification boundaries
- GitHub connector: pinned certificate, selected HTML lines, topic configuration,
  records cache, verified-effects cache, and first 230 lines of G1 object.
- Primary-source checks: JUPITER original abstract and original HTML manuscript;
  STAREE indexed original abstract/publisher abstract and trial-investigator disclosure;
  PROSPER original article text, including its Table 3, exposed on an author-uploaded copy.
- Direct live GitHub Pages attestation and complete review JSON acquisition failed.
- Some long minified HTML sections were truncated by connectors.
- No canonical review/HTML/certificate digest was independently regenerated.
- No complete repository replay, production screener, G1, or risk-of-bias machinery ran.
- The small numerical implementation is independent, not imported meta-harness code.
- Exact source data were manually transcribed; the only passage hashes recalculated
  are the two strings supplied in the audit pack.
- Registry sample verification for the three NCT-only records relied on held cache
  entries, not independently acquired complete live registry JSON.
- No PDF screenshot/visual table inspection succeeded; PROSPER table assessment
  used parsed original article text, and JUPITER tables were inspected as HTML text.
- Source copyright/licence admission under the harness's D8 policy was not executed.
- No journal PDFs, source full texts, private data or font files are redistributed.
- No repository or website was modified.

## Files
audit_topic21.py: executable independent numerical and transcription checks
inputs.json: transcribed effect inputs, user-supplied passages, identity and sources
results.json: actual output from the executed script
findings.json: findings with severity and scope
SOURCE_NOTES.md: primary sources and repository paths
requirements.txt: runtime dependencies
SHA256SUMS.txt: digests of this audit bundle's own files only
