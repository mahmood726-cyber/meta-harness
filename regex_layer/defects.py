"""Located regex defects: plant id -> why the CURRENT pattern fails it. Each runs as a strict xfail in
tests/test_regex_plants.py, so a fix flips it to a pass (and must remove the entry) and a regression cannot hide."""

# plant id -> why the current pattern fails it (a located defect, not a wish)
KNOWN_DEFECTS: dict[str, str] = {
    "_DENOM_EACH-accept-0": "RX-D1 (found 2026-09-24 by this plant): the optional group allows 'patients' OR 'were' "
                            "before 'assigned', never both, so '100 patients were randomly assigned to each' is missed. "
                            "Latent: 0 held abstracts use that phrasing today (scripts/regex_layer measurement). Fix is in "
                            "pinned code (harness/extract.py): batched with R1/R4.",
    "target_endpoint.py:search:714a13cd06-refuse-2":
        "RX-TE1 (found 2026-09-24 by this plant): 'death.{0,30}cardiovascular' spans a conjunction, so the all-cause "
        "death + CV-hospitalization composite ('death from any cause or cardiovascular hospitalization') is read as "
        "naming cardiovascular death. Reachable phrasing: present verbatim in held cache/spironolactone-hfref-mortality "
        "records; effect on a served row not measured. Fix is in pinned code (harness/target_endpoint.py).",
    "target_endpoint.py:search:aa4a355e65-refuse-2":
        "RX-TE2 (found 2026-09-24 by this plant): '\\bvascular death' fires after the hyphen in 'non-vascular death', so "
        "non-vascular death is read as cardiovascular death (the same defect the non-cardiovascular mask fixed for "
        "'non-cardiovascular'). Reachable phrasing: present in held cache/omega3-cardiovascular-events (ft_30415637) and "
        "pcsk9-mace records; effect on a served row not measured. Fix is in pinned code (harness/target_endpoint.py).",
    "target_endpoint.py:search:4a4f5b989a-refuse-2":
        "RX-TE3 (found 2026-09-24 by this plant): '\\bfatal\\b' fires inside 'non-fatal' and '.{0,25}' then reaches a later "
        "'hf', so 'non-fatal stroke or hf hospitalization' adds a heart-failure DEATH component. Latent for this exact "
        "phrasing (held dpp4-mace records carry only the ambiguous 'fatal/non-fatal MI or HF'); not measured. Fix is in "
        "pinned code (harness/target_endpoint.py).",
    "eligibility_chain.py:search:3a8e5df5f4-accept-2":
        "RX-EC1 (found 2026-09-24 by this plant): the **Population** site requires the separator AFTER the closing '**', "
        "so the '**Population:**' style (colon inside the bold) is never read. Reachable in held text: "
        "protocols/denosumab-vertebral-fracture.md and esketamine-trd-madrs.md use it; no criterion is lost today "
        "because neither line carries analysis-set wording. Fix is in pinned code (harness/eligibility_chain.py).",
    "eligibility_chain.py:search:3a8e5df5f4-accept-3":
        "RX-EC2 (found 2026-09-24 by this plant): the separator class [-:] excludes the em dash, so '**Population** — "
        "...' is not read. Reachable: protocols/colchicine-recurrent-pericarditis.md; masked today because the "
        "'intention-to-treat' prose fallback yields the same analysis_set. Fix is in pinned code (harness/eligibility_chain.py).",
    "eligibility_chain.py:search:47eac977e0-accept-2":
        "RX-EC2 (found 2026-09-24 by this plant): same em-dash separator miss on the **Timepoint** line. Reachable and "
        "consequential: protocol_criteria() on protocols/colchicine-recurrent-pericarditis.md returns NO "
        "follow_up_window criterion although the protocol states one (measured 2026-09-24). Fix is in pinned code "
        "(harness/eligibility_chain.py).",
    "compat_check.py:search:854c55479d-refuse-2":
        "RX-EC3 (found 2026-09-24 by this plant): the site's result is used as 'adult-only comparator', but it fires on "
        "any mention of adults, so a comparator covering 'children and adults' is declared adult-only and a pool with "
        "paediatric trials is marked scope-invalid. The phrasing ('...sepsis in children and adults') is in held "
        "cache/comparators/32876694 bytes; whether it reaches comp_text for a pool with paediatric trials is not measured. "
        "Fix is in pinned code (harness/compat_check.py).",
}
