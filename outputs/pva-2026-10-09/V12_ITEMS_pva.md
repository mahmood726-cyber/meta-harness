# V12 items from the pva lane (review-tabs handover) -- for the Captain's packet, NOT applied

Each item below would change a stored review object, a signed record, or a count the page serves, so this lane does not apply it. Root causes are from a recorded codex classification (outputs/pva-2026-10-09/codex_handover/classify, calls.jsonl); every quoted code line and data value passed a span gate against the files (classify/gate.json). The presentation-only items (H11, H12, H13, H17, H18, H19, A1) are fixed, with plants, on branch pva/handover-fixes.

H1 (noac ENGAGE CI) is already decided: D16 'c then b' (8 Oct).

## V12-PVA-01 (H2)

- **What the page says:** dpp4 (and the funding sentence generally): absence counts read 0 / 0 while the funding rows hold one full-text-silent and one abstract-only trial.
- **What would change:** limitations[funding-coi].rendered_text (stored) + the Risk-of-bias sentence; counts 0/0 -> 1/1 on dpp4.
- **Root cause:** `harness/page.py; harness/limitations.py` -- page.py::_riskofbias, lines 2822–2825:
        n_ns_ft = sum(1 for f in fund if f.get("status") == "none_stated_in_held_text"
                      and (f.get("scanned") or "").startswith("full text"))
        n_ns_ab = sum(1 for f in fund if f.get("status") == "none_stated_in_held_text"
                      and not (f.get("scanned") or "").startswith("full text"))
limitations.py::_funding_block, lines 575–578, repeats this status-only predicate. The committed rows instead carry funding_state and legacy type strings.
- **Proposed fix:** In both counters, replace the status-only condition with a shared predicate: def no_statement(f): return f.get('status') == 'none_stated_in_held_text' or f.get('funding_state') == 'NOT_STATED_IN_RETRIEVED_SOURCE' or f.get('type') in {'not stated (full text scanned)', 'not stated (abstract only - full text not retrieved)'}. Retain the full-text test; require an explicit abstract scan for the abstract count rather than treating every non-full-text value as abstract. Regenerate the funding limitation.
- **Plant:** Use the committed dpp4-mace-t2d funding rows. Assert both page._riskofbias(r, False) and limitations._funding_block(r['funding']) contain '1 with no funding statement' and 'and 1 where only the'. Current _funding_block was executed read-only and emits 0 instead. The corrected predicate counts one row in each category.
- **Evidence** (span-gated 5/5): `reviews/dpp4-mace-t2d/review.json`: ""type": "not stated (full text scanned)"" · `reviews/dpp4-mace-t2d/review.json`: ""type": "not stated (abstract only - full text not retrieved)"" · `reviews/dpp4-mace-t2d/review.json`: ""funding_state": "NOT_STATED_IN_RETRIEVED_SOURCE""
- **Decision needed:** apply as proposed / apply differently / leave as is.

## V12-PVA-02 (H3)

- **What the page says:** finerenone, semaglutide-weight: 'Nothing was pooled on this page' where a point estimate is served (CI refused).
- **What would change:** limitations[claim-check-zero].rendered_text + text_sha256 (stored) on 2 reviews.
- **Root cause:** `harness/page.py; harness/limitations.py` -- page.py::_reproduction, lines 2417–2423, incorrectly equates zero checkable claims with no pooling:
        n_chk = cc.get("claims_checked") or 0
        _zero = ("<div class='absent'><strong>No checkable pooled claim (Claims checked: 0).</strong> "
                 "Nothing was pooled on this page, so the canonical-claim contradiction gate has nothing "
                 "to check here — this is a limitation, not a clean result.</div>" if n_chk == 0 else "")
limitations.py::build_limitations, lines 1102–1112, stores the same error:
        if _claim_check_count(review) == 0:
                "N
- **Proposed fix:** In both functions replace the string literal "Nothing was pooled on this page, so the canonical-claim contradiction gate has nothing " with "No checkable canonical claim was available to the contradiction gate; this does not imply that no point estimate was pooled. The gate has nothing ". Preserve the zero-coverage warning and claim refusal.
- **Plant:** Use the committed finerenone-ckd-t2d-renal and semaglutide-obesity-weight reviews: claims_checked=0 with k=2 and estimates 0.8407 and -11.4732. Assert 'Nothing was pooled' is absent from page._reproduction(review, False) and the claim-check-zero object returned by limitations.build_limitations(review). Both assertions fail currently and passed with the proposed in-memory replacements; no files were written.
- **Evidence** (span-gated 5/5): `reviews/finerenone-ckd-t2d-renal/review.json`: ""estimate": 0.8407" · `reviews/semaglutide-obesity-weight/review.json`: ""estimate": -11.4732" · `reviews/finerenone-ckd-t2d-renal/review.json`: ""rendered_text": "<div class='absent'><strong>No checkable pooled claim (Claims checked: 0).</strong> Nothing was pooled on this page, so the canonical-claim co"
- **Decision needed:** apply as proposed / apply differently / leave as is.

## V12-PVA-03 (H4)

- **What the page says:** dpp4: TECOS listed as a known eligible trial NOT in the pool, while it is pooled.
- **What would change:** outcomes[primary].known_missing_sensitivity.rows loses the TECOS row (stored).
- **Root cause:** `harness/known_missing.py` -- _missing_candidates, lines 204–212, admits historical signals without checking current pool membership:
    for x in signals.get("known_eligible_missing") or []:
        key = str(x.get("trial") or "").strip()
        if key and key not in seen:
            seen.add(key)
            out.append({
                "trial": key,
                "why_eligible": x.get("note") or f"known_eligible_missing via {x.get('mechanism')}",
                "note": x.get("note") or "",
            })
_source_value, lines 183–184, then labels the unresolved descriptive alias absent:
    if not rec:
        out["
- **Proposed fix:** Resolve candidate identities before accepting missing signals and exclude IDs already in primary['trials']. For this legacy alias, match the unique label before the explanatory parenthesis ('TECOS') to the current trial label, yielding PMID 26052984; use explicit normalized IDs/report_ids where supplied and refuse ambiguous alias matches. Apply the same membership exclusion to declared_absent_trials. Clear primary.pop('known_missing_sensitivity', None) before rebuilding so an empty candidate set cannot retain a stale panel.
- **Plant:** Use the committed review with signals={'known_eligible_missing':[{'trial':'TECOS (3-point MACE from primary publication)','note':'test'}]}. Assert _missing_candidates returns no TECOS candidate while retaining unrelated absent trials. Executing the current function returned {'trial': 'TECOS (3-point MACE from primary publication)', 'why_eligible': 'test', 'note': 'test'}. Also seed an old panel with only TECOS and verify rebuilding removes it when no missing candidates remain.
- **Evidence** (span-gated 6/6): `reviews/dpp4-mace-t2d/review.json`: ""trial_key": "TECOS (3-point MACE from primary publication)"" · `reviews/dpp4-mace-t2d/review.json`: ""verify_basis": "named trial is not present in the committed topic cache"" · `reviews/dpp4-mace-t2d/review.json`: ""value_status": "NOT_IN_COMMITTED_SOURCE""
- **Decision needed:** apply as proposed / apply differently / leave as is.

## V12-PVA-04 (H5)

- **What the page says:** dpp4: the TECOS notice reads NOT APPLIED (HELD), overtaken by a later signed route.
- **What would change:** docs/result_changes.json: the notice's held block gains a resolution (a SIGNED record's metadata).
- **Root cause:** `harness/page.py; harness/review_tabs.py` -- page.py::result_changes_status, lines 2240–2242, treats stored hold metadata as current without a resolution check:
    hd = n.get("held") or {}
    if hd.get("code"):
        return {"state": "HELD", "text": f"held ({hd.get('code')}): {hd.get('why')}"}
review_tabs.py::changes_tab, lines 498–500, turns that into a categorical current-result assertion:
                out.append("<p class='absent' data-result-change-status='" + _e(st["state"]) + "'><strong>NOT APPLIED -- "
                           + _e(st["text"]) + "</strong> The notice below is kept as signed, for the record; the served "
 
- **Proposed fix:** Preserve the historical hold and add held.resolution with state='OVERTAKEN', a source-backed reason and the matching signed admission/HHF-notice references. In result_changes_status, check that resolution before returning HELD. In changes_tab, render OVERTAKEN as historical hold resolved, without the 'NOT APPLIED' or 'served result does not include it' assertions. Do not infer resolution merely from matching numbers or rewrite the signed block.
- **Plant:** Use the committed primary-MACE notice, its held metadata, the served TECOS row and the signed HHF notice dated 2026-10-06. Add the verified resolution metadata in memory. Assert result_changes_status returns OVERTAKEN and changes_tab does not label that notice HELD or assert its result is excluded. Current result_changes_status was executed read-only and returns HELD; it ignores resolution metadata.
- **Evidence** (span-gated 6/6): `reviews/dpp4-mace-t2d/review.json`: ""code": "SIGNED_CHANGE_HAS_AN_UNSHOWN_CONSEQUENCE"" · `reviews/dpp4-mace-t2d/review.json`: "Held until both are presented together (next packet)." · `reviews/dpp4-mace-t2d/index.html`: "The notice below is kept as signed, for the record; the served result does not include it."
- **Decision needed:** apply as proposed / apply differently / leave as is.

## V12-PVA-05 (H6)

- **What the page says:** doac: comparator note endorses van Es 2014, which the comparator panel retired (open-licence gate).
- **What would change:** review.json comparator_scope_note (copied from the topic config) -- topic config + rebuild.
- **Root cause:** `harness/pipeline.py` -- build_review_core, line 2346: comparator_scope_note = config.get("comparator_scope_note")
Line 2440: **({"comparator_scope_note": comparator_scope_note} if comparator_scope_note else {}),
harness/page.py, _comparator, lines 2136–2137: if r.get("comparator_scope_note"):
            body += f"<p><strong>Comparator resolution.</strong> {_e(r.get('comparator_scope_note'))}</p>"
- **Proposed fix:** Correct the source config before build_review_core: config['comparator_scope_note'] = config['comparator_scope_note'].replace('van Es et al. 2014 (PMID 24963045) is a scope-matched open-access pooled analysis of the six phase-3 acute symptomatic VTE DOAC-vs-VKA trials and reports recurrent VTE including VTE-related death as RR 0.90 (0.77-1.06).', 'The adopted comparator is PMID 29795629. PMID 24963045 was retired after C1_OPEN_LICENCE failed.'). Rebuild the stored note and page; do not merely hide it in HTML.
- **Plant:** Use the committed doac-vte-recurrence review, whose comparator_panel[0]['id'] is '29795629'. After rebuilding, assert 'is a scope-matched open-access pooled analysis' not in review['comparator_scope_note'] and '29795629' in review['comparator_scope_note']. The current stored note fails.
- **Evidence** (span-gated 3/3): `reviews/doac-vte-recurrence/review.json`: "van Es et al. 2014 (PMID 24963045) is a scope-matched open-access pooled analysis" · `reviews/doac-vte-recurrence/review.json`: "Efficacy and safety of direct oral anticoagulants approved for cardiovascular indications: Systematic review and meta-analysis. PMID 29795629" · `reviews/doac-vte-recurrence/review.json`: "C1_OPEN_LICENCE FAIL: no CC BY / CC0 licence (Europe PMC none; Unpaywall bronze)"
- **Decision needed:** apply as proposed / apply differently / leave as is.

## V12-PVA-06 (H7)

- **What the page says:** sacubitril: comparator note says PARADIGM-HF is the only extractable estimate; PARALLEL-HF is extracted too.
- **What would change:** review.json comparator_scope_note -- topic config + rebuild.
- **Root cause:** `harness/pipeline.py` -- build_review_core, lines 2346–2347: comparator_scope_note = config.get("comparator_scope_note")
    if (primary.get("result") or {}).get("design_refusal"):
Line 2440: **({"comparator_scope_note": comparator_scope_note} if comparator_scope_note else {}),
- **Proposed fix:** Replace the stale opening in the source config: config['comparator_scope_note'] = 'PARADIGM-HF and PARALLEL-HF both have extracted primary-outcome estimates. The two-trial pooled row is refused: DIRECTION_CONFLICT_K2. Separately, ' + config['comparator_scope_note'].split('Separately, ', 1)[1]. Rebuild the review and page.
- **Plant:** Use the committed sacubitril-valsartan-hfref primary outcome: two trials, PARALLEL-HF effect 1.0881, result.pool_refused.code == 'DIRECTION_CONFLICT_K2'. Assert the rebuilt note includes 'PARALLEL-HF' and 'DIRECTION_CONFLICT_K2' and excludes 'only EXTRACTABLE'. Current code preserves the contradictory note.
- **Evidence** (span-gated 3/3): `reviews/sacubitril-valsartan-hfref/review.json`: "k=1 CONTRIBUTING, not a complete-evidence claim: PARADIGM-HF supplies the only EXTRACTABLE primary-outcome estimate here" · `reviews/sacubitril-valsartan-hfref/review.json`: "ClinicalTrials.gov results (structured target endpoint): outcome 'Exposure-adjusted Incident Rate (EAIR) of CEC Confirmed Composite Endpoints' HR 1.0881 (95% CI" · `reviews/sacubitril-valsartan-hfref/review.json`: "k=2 pooled row refused because point estimates are on opposite sides of the null"
- **Decision needed:** apply as proposed / apply differently / leave as is.

## V12-PVA-07 (H8)

- **What the page says:** tocilizumab: comparator note says COVACTA gives mortality as a RATE only; the row holds counts 58/294 v 28/144.
- **What would change:** review.json comparator_scope_note -- topic config + rebuild.
- **Root cause:** `harness/pipeline.py` -- build_review_core, line 2346: comparator_scope_note = config.get("comparator_scope_note")
Line 2440: **({"comparator_scope_note": comparator_scope_note} if comparator_scope_note else {}),
harness/page.py, _comparator, line 2137: body += f"<p><strong>Comparator resolution.</strong> {_e(r.get('comparator_scope_note'))}</p>"
- **Proposed fix:** Replace the stale extraction paragraph, including its dependent k≈1 assertion: config['comparator_scope_note'] = config['comparator_scope_note'].split('(3) REACH/EXTRACTION:', 1)[0] + '(3) REACH/EXTRACTION: the current primary outcome includes RECOVERY, COVACTA and TOCIBRAS. COVACTA has committed day-28 mortality counts of 58/294 versus 28/144.'. Rebuild the review and page.
- **Plant:** Use the committed tocilizumab-covid19-mortality review. Assert the rebuilt note contains '58/294' and '28/144', excludes 'COVACTA gives mortality as a RATE only', and excludes 'verifiable-count k is ~1'. The current note fails all these checks.
- **Evidence** (span-gated 2/2): `reviews/tocilizumab-covid19-mortality/review.json`: "COVACTA gives mortality as a RATE only (19.7% vs 19.4%, no per-arm counts)" · `reviews/tocilizumab-covid19-mortality/review.json`: "Tocilizumab (N=294) ... Placebo (N=144) ... Death at day 28 — no. (%) 58 (19.7) 28 (19.4)"
- **Decision needed:** apply as proposed / apply differently / leave as is.

## V12-PVA-08 (H9)

- **What the page says:** tocilizumab, tranexamic, colchicine-pericarditis: '✓ same question' while each review's own note records a broader comparator.
- **What would change:** comparator.scope.scope_valid / note / intervention_level_match (stored) on 3 reviews.
- **Root cause:** `harness/scope.py` -- assess, lines 34–40:
    topic_is_class = _has_class(" ".join(topic_terms)) or _has_any(" ".join(topic_terms), class_terms)
    comparator_is_class = _has_class(comparator_title) or _has_any(comparator_title, class_terms)
    iv_level_match = not (comparator_is_class and not topic_is_class)
    pop = _has_any((comparator_title or "") + " " + (comparator_abstract or ""), inc.get("population_any") or [])
    valid = bool(iv_level_match and pop)
    if valid:
        note = "same-question comparator (matching intervention level and population)"
harness/page.py, _comparator, lines 2112–2113:
     
- **Proposed fix:** Use source-backed eligibility assessments rather than search-term class inference and population keyword overlap. Minimal explicit-input correction in assess: topic_is_class = config['topic_is_class']; iv_level_match = topic_is_class == comparator_is_class; valid = bool(iv_level_match and pop and config.get('comparator_pico_design_match') is True). Set topic_is_class=False for these single-agent topics; record comparator_pico_design_match=False with the documented mismatch reason and return that reason as note. Missing full-scope assessment must not produce 'same-question'.
- **Plant:** assess({'intervention_terms':['tocilizumab','IL-6 receptor antagonists'], 'include':{'population_any':['COVID-19']}, 'topic_is_class':False, 'comparator_pico_design_match':False}, 'IL-6 antagonists for COVID-19') must return scope_valid=False and intervention_level_match=False. Current code returns both True. Also test single-agent TXA/postpartum and colchicine/pericarditis inputs with comparator_pico_design_match=False: scope_valid must be False while intervention_level_match may remain True.
- **Evidence** (span-gated 4/4): `reviews/tocilizumab-covid19-mortality/review.json`: "the committed comparator (PMID 34228774) pools the IL-6-antagonist CLASS (tocilizumab + sarilumab), a broader PICO than this tocilizumab-only topic." · `reviews/colchicine-recurrent-pericarditis/review.json`: "The 2012 Heart meta-analysis (PMID 22442198) is a RELATED, BROADER comparator, not a same-scope one: it pooled more trials including open-label studies and mixe" · `reviews/tranexamic-acid-pph/index.html`: "<strong>✓ same question.</strong> Intervention level: topic is a single agent, comparator is a single agent (match: True); population match: True."
- **Decision needed:** apply as proposed / apply differently / leave as is.

## V12-PVA-09 (H10)

- **What the page says:** pcsk9: 'pooled trials use each trial's OWN primary composite'; FOURIER contributes its secondary composite.
- **What would change:** outcomes[0].result.composite_heterogeneity (stored) on pcsk9.
- **Root cause:** `harness/extract.py` -- composite_heterogeneity(), lines 630 and 667, unconditionally describes heterogeneous composites as primary:
return ("pooled trials use each trial's OWN primary composite; component sets differ across trials"

_build_outcome(), harness/pipeline.py:1934-1936, persists the text:
_ch = extract.composite_heterogeneity(spec.get("name", ""), _ch_srcs)
if _ch:
    out["result"]["composite_heterogeneity"] = _ch
- **Proposed fix:** In both return branches, replace "pooled trials use each trial's OWN primary composite; component sets differ across trials" with "pooled trials contribute selected composite endpoints; component sets differ across trials". The existing endpoint-definition annotations also require reconciliation with the selected endpoints before treating the entire disclosure as validated.
- **Plant:** Call composite_heterogeneity('MACE', [{'endpoint_definition': 'CV_DEATH | MI | STROKE', 'registry_type': 'SECONDARY'}, {'endpoint_definition': 'CHD_DEATH | MI | STROKE | UNSTABLE_ANGINA'}]). Assert the disclosure contains 'selected composite endpoints' and excludes 'OWN primary composite'. Current function was exercised read-only and produces the incorrect primary assertion.
- **Evidence** (span-gated 3/3): `reviews/pcsk9-mace/review.json`: ""registry_type": "SECONDARY"" · `reviews/pcsk9-mace/review.json`: ""source": "ClinicalTrials.gov results (structured target endpoint): outcome 'Time to Cardiovascular Death, Myocardial Infarction, or Stroke' HR 0.8 (95% CI 0.73" · `reviews/pcsk9-mace/review.json`: ""composite_heterogeneity": "pooled trials use each trial's OWN primary composite; component sets differ across trials (endpoint definitions: CHD_DEATH | MI | IS"
- **Decision needed:** apply as proposed / apply differently / leave as is.

## V12-PVA-10 (H14)

- **What the page says:** tocilizumab, tranexamic: search funnel 'unknown -> 0 -> 0' for queries whose yields were never recorded.
- **What would change:** a displayed search count changes from 0 to 'unknown' (served number on the page; review.json unchanged).
- **Root cause:** `harness/page.py` -- _retrieval_html(), lines 243-246, renders funnel counts without consulting source state:
funnel = src.get("funnel") or {}
flow = (f"{_retrieval_value(funnel.get('hits'))} -&gt; "
        f"{_retrieval_value(funnel.get('fetched'))} -&gt; "
        f"{_retrieval_value(funnel.get('retained'))}")

_retrieval_value(), lines 168-169:
def _retrieval_value(x: Any) -> str:
    return "unknown" if x is None else _e(x)
- **Proposed fix:** Immediately after constructing flow, add:
if src.get('state') == 'RAN_UNRECORDED':
    flow = 'unknown -&gt; unknown -&gt; unknown'
This does not mutate the committed funnel or convert genuinely observed RAN_ZERO counts.
- **Plant:** Pass _retrieval_html({'sources': [{'state': 'RAN_UNRECORDED', 'funnel': {'hits': None, 'fetched': 0, 'retained': 0}}]}). Assert the funnel cell contains 'unknown -&gt; unknown -&gt; unknown' and excludes 'unknown -&gt; 0 -&gt; 0'. Read-only checks reproduced three incorrect rows on each named committed page. Add a RAN_ZERO control asserting measured zeros remain visible.
- **Evidence** (span-gated 5/5): `reviews/tocilizumab-covid19-mortality/review.json`: ""state": "RAN_UNRECORDED"" · `reviews/tranexamic-acid-pph/review.json`: ""fetched": 0,
            "retained": 0," · `harness/page.py`: "return ("<strong>RAN_UNRECORDED</strong>: attempted by a pre-ledger fetch; its yield was never recorded, so "
                "neither a count nor a zero can be"
- **Decision needed:** apply as proposed / apply differently / leave as is.

## V12-PVA-11 (H15)

- **What the page says:** empagliflozin: a SIGNED notice says 'a pooled estimate is now served' for a k = 1 single-trial estimate.
- **What would change:** a SUCCESSOR signed notice (the signed bytes cannot change) + docs/result_changes.json.
- **Root cause:** `harness/result_changes.py` -- conclusion_changed(), lines 78–79:
    if before.get("estimate") is None and after.get("estimate") is not None:
        return "a pooled estimate is now served where none was served before: a new claim, not a continuation"
- **Proposed fix:** For new notices, use kind = 'single-trial' if after.get('k') == 1 else 'pooled'; return f'a {kind} estimate is now served where none was served before: a new claim, not a continuation'. Version the wording so historical signed blocks retain their exact bytes; issue a separately countersigned correction/successor rather than silently regenerating historical signatures.
- **Plant:** before={'k':0,'estimate':None}; after={'k':1,'estimate':0.79,'ci_low':0.69,'ci_high':0.9}; scale='HR'. Require new-version conclusion_changed to say 'single-trial estimate'. Current function returns 'pooled estimate' (reproduced). Also require historical signed-block hashes to remain unchanged.
- **Evidence** (span-gated 3/3): `reviews/empagliflozin-hfpef-hosp/index.html`: "Now: k = 1, 0.79 (0.69 to 0.90). <strong>Conclusion changed: a pooled estimate is now served where none was served before: a new claim, not a continuation.</str" · `docs_result_changes.json`: ""rendered_sha256": "9aa0336c4b75225dcc61539026f1d4bce9fa9de405bd30cf4f76c93259c26db3"" · `harness/result_changes.py`: "    if sig["rendered_sha256"] != rendered_sha256(block_html):"
- **Decision needed:** apply as proposed / apply differently / leave as is.

## V12-PVA-12 (H16)

- **What the page says:** metformin (every higher-is-better outcome): claim direction 'harm' for ovulation OR > 1.
- **What would change:** outcomes[*].result.claim.direction (stored; gate-checked against every surface) + an explicit outcome polarity field.
- **Root cause:** `harness/claim.py` -- derive(), lines 101–106:
    direction = "none"
    if est is not None:
        if est < null - _EPS:
            direction = "benefit"
        elif est > null + _EPS:
            direction = "harm"
- **Proposed fix:** Add explicit, source-backed benefit_when ('higher'/'lower') to derive and its callers. Compute delta = (est - null) * (1 if benefit_when == 'higher' else -1); direction = 'benefit' if delta > _EPS else 'harm' if delta < -_EPS else 'none'. For missing polarity, return direction=None rather than assuming lower is beneficial. Update the direction definition accordingly.
- **Plant:** Use the committed metformin primary result (OR 2.0733, CI 0.0922–46.6008) with benefit_when='higher': require direction='benefit', significant=False and crosses_null=True. Current derive returns harm (reproduced). Include higher/lower polarity controls on both ratio and difference scales.
- **Evidence** (span-gated 4/4): `reviews/metformin-pcos-ovulation/review.json`: ""name": "Ovulation with metformin added to clomifene"" · `reviews/metformin-pcos-ovulation/review.json`: ""estimate": 2.0733," · `reviews/metformin-pcos-ovulation/review.json`: ""direction": "harm","
- **Decision needed:** apply as proposed / apply differently / leave as is.

