"""Plants for robgrade/prompt_licence: only CC BY / CC0 full texts may enter a model prompt (D8). 2026-10-12: a CC BY-NC
and a CC BY-NC-ND text reached codex and agy because 'any Creative Commons URL' was read as CC."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from robgrade import prompt_licence as pl  # noqa: E402


def _x(inner):
    return f"<article><front><permissions>{inner}</permissions></front></article>"


def test_cc_by_and_cc0_open():
    assert pl.prompt_licence(_x('<license xlink:href="https://creativecommons.org/licenses/by/4.0/"/>')) == "CC_BY"
    assert pl.prompt_licence(_x('<license xlink:href="https://creativecommons.org/publicdomain/zero/1.0/"/>')) == "CC0"
    assert pl.prompt_licence(_x("distributed under the Creative Commons Attribution License (CC BY)")) == "CC_BY"


def test_PLANT_nc_nd_sa_never_open():
    for u in ("by-nc/4.0", "by-nc-nd/4.0", "by-nd/4.0", "by-sa/4.0", "by-nc-sa/3.0"):
        assert pl.prompt_licence(_x(f'<license xlink:href="http://creativecommons.org/licenses/{u}/"/>')) == "RESTRICTED", u
    assert pl.prompt_licence(_x("Creative Commons Attribution-NonCommercial License")) == "RESTRICTED"
    # a CC BY URL beside an NC term (dual statement) is restricted, never the more open reading
    assert pl.prompt_licence(_x('<license xlink:href="https://creativecommons.org/licenses/by/4.0/"/> '
                                "for non-commercial use only")) == "RESTRICTED"


def test_PLANT_words_outside_permissions_do_not_count():
    assert pl.prompt_licence("<article><body>Creative Commons Attribution</body></article>") == "NONE"


def test_PLANT_tracked_not_cc_texts_never_open():
    # the tracked audit rates these NC/ND texts NOT_CC: they never open, whatever a copy's permissions say
    for p in ("21115589", "39529939", "41699149", "36331190"):
        assert pl.tracked_verdict(p) == "NOT_CC"


def test_PLANT_the_two_incident_texts_are_closed_by_their_own_permissions():
    # 32720823 (CC BY-NC) and 28456509 (CC BY-NC-ND), as their PMC permissions state them
    assert pl.prompt_licence(_x('<license xlink:href="http://creativecommons.org/licenses/by-nc/4.0/">'
                                "This is an open access article under the CC BY-NC license</license>")) == "RESTRICTED"
    assert pl.prompt_licence(_x('<license license-type="CC BY-NC-ND" xlink:href="https://creativecommons.org/licenses/'
                                'by-nc-nd/4.0/"/>')) == "RESTRICTED"
