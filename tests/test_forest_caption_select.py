"""select_figure with the secondary tier's own caption regex: the forest-caption predicate still applies (a PLoS One
CAP meta's only mortality forest plot is captioned 'Meta-analysis for the association between mortality and
corticosteroids' -- matched by neither 'forest' nor the tier's 'meta-analyses of'), and a funnel / flow figure is
never a candidate whichever regex is passed."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
import k_gap_forest_plot as fpl  # noqa: E402
import secondary_meta_build as smb  # noqa: E402

JATS = """<article xmlns:xlink="http://www.w3.org/1999/xlink"><body>
<fig id="g001"><caption><p>Figure 1 Flow of study identification, inclusion, and exclusion.</p></caption><graphic xlink:href="g001"/></fig>
<fig id="g002"><caption><p>Figure 2 Meta-analysis for the association between mortality and corticosteroids.</p></caption><graphic xlink:href="g002"/></fig>
<fig id="g005"><caption><p>Figure 5 Funnel plot of the included trials for pooled mortality.</p></caption><graphic xlink:href="g005"/></fig>
</body></article>"""


def test_the_secondary_tier_selects_a_forest_plot_its_own_regex_misses_and_never_a_funnel(tmp_path, monkeypatch):
    d = tmp_path / "99999999"
    d.mkdir()
    (d / "2026-09-30_kgap_jats.xml").write_text(JATS, encoding="utf-8")
    monkeypatch.setattr(fpl, "COMP", str(tmp_path))
    fig, why = fpl.select_figure("corticosteroids-cap-mortality", "99999999", jats_date="2026-09-30", caption_re=smb.CAPTION)
    assert why == "SELECTED" and fig["fig_id"] == "g002"
