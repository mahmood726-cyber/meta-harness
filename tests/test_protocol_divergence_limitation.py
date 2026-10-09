"""A DISCLOSED protocol/config divergence is a limitation object with its own visible block, never only a paragraph. Before,
a page whose compliance moved from NOT_ESTABLISHED (nothing compared) to DISCLOSED_DIVERGENCE (a real disagreement found)
LOST its only warning block -- the page got quieter exactly when it found a problem (V13-03Q render, honest ratchet)."""
from harness import limitations, page

DIV = [{"code": "ESTIMAND_DIVERGENCE", "dimension": "estimand", "prose": "RR", "config": "HR"}]


def test_PLANT_a_disclosed_divergence_is_a_visible_limitation_naming_each_divergence():
    html = page.protocol_divergence_disclosed_html(DIV)
    assert "class='absent'" in html and "ESTIMAND_DIVERGENCE" in html and "RR" in html and "HR" in html
    assert "not asserted" in html


def test_the_limitation_is_built_from_the_compliance_object():
    review = {"slug": "t", "outcomes": [], "protocol_config": {"divergences": DIV, "agreed_dimensions": []}}
    objs = limitations.build_limitations(review)
    hit = [o for o in objs if "protocol-config-divergence" in str(o.get("limitation_id") or o.get("id") or "")]
    assert len(hit) == 1 and "ESTIMAND_DIVERGENCE" in hit[0]["rendered_text"]
    review["protocol_config"] = {"divergences": [], "agreed_dimensions": []}
    assert not [o for o in limitations.build_limitations(review)
                if "protocol-config-divergence" in str(o.get("limitation_id") or o.get("id") or "")]


def test_PLANT_the_reproducibility_tab_prints_the_divergence_block():
    import json, os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    r = json.load(open(os.path.join(root, "docs", "reviews", "iv-iron-hfref-hosp", "review.json"), encoding="utf-8"))
    r["protocol_config"] = {"divergences": DIV, "agreed_dimensions": [], "compliance": {"state": "DISCLOSED_DIVERGENCE"}}
    html = page._reproduction(r, False)
    assert "Protocol/config DIVERGENCE disclosed" in html
