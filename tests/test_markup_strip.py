"""'<' and '>' in scientific text survive markup stripping (lane OC, V1.1).

Plants fire on the pre-fix code: every source-text strip site used `<[^>]+>`, which deletes from a literal 'P<' to the next '>'.
Each site is exercised through its own public helper, so a site left on the old regex fails by name."""
import glob
import json
import os
import re
import sys
from html.parser import HTMLParser

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import absence, cites, hand_binding, reason_audit, registry_multi  # noqa: E402
from harness.markup import strip_markup  # noqa: E402

TUPLE = "Mortality was lower (P<0.001), HR 0.82 (95% CI 0.70 to 0.96; P>0.2)."

SITES = {
    "absence._strip_markup": lambda t: absence._strip_markup(t),
    "reason_audit._plain": lambda t: reason_audit._plain(t),
    "hand_binding._plain": lambda t: hand_binding._plain(t),
    "cites._clean_text": lambda t: cites._clean_text(t),
    "registry_multi._clean_text": lambda t: registry_multi._clean_text(t),
}


@pytest.mark.parametrize("site", sorted(SITES))
def test_the_effect_tuple_between_P_less_than_and_P_greater_than_survives(site):
    out = SITES[site](TUPLE)
    for tok in ("P<0.001", "HR 0.82", "95% CI 0.70 to 0.96", "P>0.2"):
        assert tok in re.sub(r"\s+", " ", out), (site, tok, out)


@pytest.mark.parametrize("site", sorted(SITES))
def test_real_markup_is_still_removed(site):
    out = SITES[site]("<p>The <italic>hazard ratio</italic> was 0.82<sup>1</sup><!-- c --><br/> (P&lt;0.001)</p>")
    assert not re.search(r"</?[A-Za-z]", out) and "italic" not in out and "sup>" not in out     # no tag survives (decoded &lt; may)
    assert "hazard ratio" in out and "0.82" in out


def test_literal_comparisons_that_are_not_tags():
    for t in ("age < 65 and HbA1c <7% (p<.05; <=10; x<-1); OR > 1", "P<0.001, P = 0.02, P>0.05"):
        assert strip_markup(t) == t


def test_absence_state_no_longer_manufactures_an_absence():
    """The decision-level plant: the outcome's effect sits between 'P<' and a later '>'. Pre-fix the stripper deleted it, so the
    absence classifier said SOURCE_NOT_RETRIEVED (an absence claim); now the number is seen and the honest state is
    EXTRACTION_NOT_PERFORMED."""
    fulltext = ("<article><body><p>Stroke was less frequent (P<0.05): 12 of 400 patients vs 20 of 402; stroke hazard ratio 0.60 "
                "(95% CI 0.30 to 0.95).</p><p>Other analyses (P>0.2).</p></body></article>")
    state, _ = absence.classify(["stroke"], "Randomized trial of drug X. Stroke was assessed.", fulltext)
    assert state == "EXTRACTION_NOT_PERFORMED", state


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.parts = []

    def handle_data(self, d):
        self.parts.append(d)


def reference_tokens(text):
    """INDEPENDENT reference: the stdlib HTML parser's text (it treats '<0.001' as data), tokenised."""
    p = _Text()
    p.feed(text)
    p.close()
    return re.findall(r"[A-Za-z]+|\d+(?:\.\d+)?", " ".join(p.parts))


def damaged(stripped, text):
    have = set(re.findall(r"[A-Za-z]+|\d+(?:\.\d+)?", stripped))
    return any(t not in have for t in reference_tokens(text))


def test_no_held_abstract_loses_a_token_the_reference_parser_keeps():
    """The corpus plant: every abstract in the committed caches that contains '<'. Pre-fix 84 of 891 (26 topics) lost prose."""
    n = bad = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "cache", "*", "records.json"))):
        for r in json.load(open(p, encoding="utf-8")).get("records") or []:
            t = r.get("abstract") or ""
            if "<" in t:
                n += 1
                bad += damaged(absence._strip_markup(t), t)
    if n == 0:
        pytest.skip("no committed caches in this checkout -- NOT a pass")
    assert bad == 0, f"{bad} of {n} abstracts containing '<' still lose text"
