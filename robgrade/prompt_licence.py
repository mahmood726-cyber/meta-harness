"""Which full texts may enter a MODEL PROMPT (D8): CC BY or CC0 only, read from the PMC copy's OWN <permissions>.

reproducible_ai.record_licence.jats_licence answers 'CC' for ANY creativecommons.org licence, NonCommercial and
NoDerivatives included; registry/tracked_fulltext_licences.json rates those NOT_CC (regex use only). On 2026-10-12 a
DEV run sent two such texts (CC BY-NC 32720823, CC BY-NC-ND 28456509) to codex and agy because the lane trusted the
broad answer. This is the narrow test the lane's prompt path uses; a text it does not clear is read by regex only.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPEN_FOR_PROMPT = ("CC_BY", "CC0")
_RESTRICT = re.compile(r"\b(?:by-nc|by-nd|by-nc-nd|by-nc-sa|by-sa)\b|non-?\s?commercial|no\s?-?deriv|share\s?-?alike"
                       r"|\bCC[ -]BY[ -](?:NC|ND|SA)\b", re.I)


def permissions(xml):
    return " ".join(re.findall(r"<permissions>.*?</permissions>", xml, re.S))


def prompt_licence(xml):
    """'CC_BY' | 'CC0' | 'RESTRICTED' (any NC/ND/SA term) | 'NONE', from the JATS <permissions> only."""
    perm = permissions(xml)
    if not perm:
        return "NONE"
    if _RESTRICT.search(perm):
        return "RESTRICTED"
    if re.search(r"creativecommons\.org/licenses/by/", perm) or re.search(r"Creative\s+Commons\s+Attribution\b|\bCC[ -]BY\b", perm):
        return "CC_BY"
    if re.search(r"creativecommons\.org/publicdomain/zero/|\bCC0\b|Creative\s+Commons\s+Zero", perm):
        return "CC0"
    return "NONE"


_TRACKED = None


def tracked_verdict(pmid):
    """The harness's own licence audit verdict for a tracked full text (NOT_CC closes it), else None."""
    global _TRACKED
    if _TRACKED is None:
        p = os.path.join(ROOT, "registry", "tracked_fulltext_licences.json")
        rows = json.load(open(p, encoding="utf-8")).get("rows", []) if os.path.exists(p) else []
        _TRACKED = {str(r.get("pmid")): r.get("verdict") for r in rows}
    return _TRACKED.get(str(pmid))


def open_for_prompt(pmid, xml_path):
    """True only when the stored PMC copy's own permissions are CC BY / CC0 AND the tracked audit does not say NOT_CC."""
    try:
        xml = open(xml_path, encoding="utf-8", errors="replace").read()
    except OSError:
        return False
    return prompt_licence(xml) in OPEN_FOR_PROMPT and tracked_verdict(pmid) != "NOT_CC"
