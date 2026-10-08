"""Plant (8 Oct, forest lane D8 class audit): g1_trial_acquire showed a PMC copy to the model whenever the repo guard
said 'CC' -- any Creative Commons licence, CC BY-NC and CC BY-NC-ND included -- and an Unpaywall copy on any 'cc*'
licence. 7 recorded prompts carried NC / NC-ND full text. D8 (scripts/g1_licence.py): CC BY / CC0 only."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_trial_acquire as ga  # noqa: E402


def test_pmc_copy_needs_cc_by_or_cc0(monkeypatch):
    import g1_licence
    monkeypatch.setattr(ga, "pmc_licence", lambda p: "CC")
    monkeypatch.setattr(g1_licence, "licence", lambda p, offline=False: {"license": "cc by-nc", "open": False})
    assert not ga.pmc_prompt_ok("1")
    monkeypatch.setattr(g1_licence, "licence", lambda p, offline=False: {"license": "cc by", "open": True})
    assert ga.pmc_prompt_ok("1")
    monkeypatch.setattr(ga, "pmc_licence", lambda p: "PMC_AUTHOR_MANUSCRIPT")
    assert not ga.pmc_prompt_ok("1")


def test_unpaywall_copy_needs_cc_by_or_cc0():
    assert ga.upw_prompt_ok("cc-by") and ga.upw_prompt_ok("cc0") and ga.upw_prompt_ok("public-domain")
    for lic in ("cc-by-nc", "cc-by-nc-nd", "cc-by-nd", "cc-by-sa", None, "implied-oa"):
        assert not ga.upw_prompt_ok(lic), lic
