"""A comparator's trial list labelled 'Helps et al52' / 'Mewton et al. (26)' (surname + reference number) never joined
the same comparator's forest row 'Helps 2015' / 'Mewton N-2019' (surname + year): the leading-token join compared
[helps, et, al52] with [helps, 2015]. The surname core (et al / reference number / year / initials removed, spacing
folded) now joins -- uniquely, and never across two different years."""
import os
import sys
from types import SimpleNamespace as NS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
import secondary_meta_build as smb  # noqa: E402


def _fam(labels):
    return smb.family_of_factory([{"id": l, "label": l, "acronyms": [], "author_year": None} for l in labels])


def test_surname_with_reference_number_joins_surname_with_year():
    f = _fam(["Helps et al52", "Hempel et al53", "Mewton et al. (26)", "de Vrese et al33", "Refaie 2005", "Akrami et al. (12)"])
    assert f(NS(trial_label="Helps 2015")) == "Helps et al52"
    assert f(NS(trial_label="Mewton N-2019")) == "Mewton et al. (26)"
    assert f(NS(trial_label="DeVrese 2011")) == "de Vrese et al33"
    assert f(NS(trial_label="Re faie 2005")) == "Refaie 2005"
    assert f(NS(trial_label="Mehdi Akrami–2012")) is None      # a forename leads: not the same surname core


def test_ambiguous_surnames_and_different_years_never_join():
    f = _fam(["Deftereos et al. (25)", "Deftereos et al. (19)", "Palomba 2004", "Palomba 2005a"])
    assert f(NS(trial_label="Deftereos 2013")) is None
    assert f(NS(trial_label="Palomba 2006")) is None
    assert f(NS(trial_label="Palomba 2004")) == "Palomba 2004"


def test_the_surname_tier_never_overrides_or_dilutes_an_existing_join():
    # balanced-crystalloids 4 Oct: 'Young [10]' / 'Young [17]' joined 'Young 2015' / 'Young 2014' by their PMIDs'
    # author-year; the surname tier hit BOTH and made each ambiguous. melatonin: 'Wade AG [28]' moved 2007 -> 2011.
    ents = [{"id": "Young [10]", "label": "Young [10]", "acronyms": [], "author_year": ("young", "2015")},
            {"id": "Young [17]", "label": "Young [17]", "acronyms": [], "author_year": ("young", "2014")},
            {"id": "Wade AG [22]", "label": "Wade AG [22]", "acronyms": [], "author_year": ("wade", "2011")},
            {"id": "Wade AG [28]", "label": "Wade AG [28]", "acronyms": [], "author_year": ("wade", "2007")}]
    f = smb.family_of_factory(ents)
    assert f(NS(trial_label="Young 2015")) == "Young [10]"
    assert f(NS(trial_label="Young 2014")) == "Young [17]"
    assert f(NS(trial_label="Wade AG, 2007 [26]")) == "Wade AG [28]"
    assert f(NS(trial_label="Wade AG, 2011 [21]")) == "Wade AG [22]"
