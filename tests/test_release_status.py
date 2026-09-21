"""PRE-RELEASE is a claim and passes the same discipline as the thing it replaces: declared in the review core (covered by
review_sha256, reproduced by the replay), rendered on every page with every reason, enforced by gate limb 1 in both directions
(declared-but-not-rendered refuses; rendered-but-not-declared refuses), recorded in the fix ledger."""
import glob
import re
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import page, gate  # noqa: E402

REASONS = ("GENERATING_TREE_NOT_RECORDED", "VERIFY_LABEL_DEFECTS", "VERIFIED_IS_A_PRODUCER_ASSERTION", "ADMISSION_PATH_DEMONSTRATED_PERMEABLE",
           "KNOWN_INCORRECT_VALUES_ON_NAMED_PAGES", "HAND_WRITTEN_STATUS_DESCRIBES_A_COMPUTED_RELATION", "BOUNDED_REMEDY_ESTIMATED")


def test_release_status_file_names_the_decision_the_commit_and_the_reasons():
    rs = json.load(open(ROOT / "registry" / "release_status.json", encoding="utf-8"))
    assert rs["status"] == "PRE-RELEASE" and rs["decision"]["by"] == "Mahmood" and rs["pre_release_commit"].startswith("316d2e48")
    assert rs["decision"]["countersignature"]["state"] == "NOT_COUNTERSIGNED"          # relayed, not countersigned -- the true value
    assert "APPROVED" in rs["decision"]["countersignature"]["refused_by_name"]
    assert all("five harness/verify.py defect classes" in c or "verify.py" not in c for c in rs["v1_conditions"])
    assert [x["id"] for x in rs["reasons"]] == list(REASONS)
    assert "NOT_RECORDED" in rs["reasons"][0]["text"] and "not reconstructed" in rs["reasons"][0]["text"]
    assert "e5187ea9cc8e" in rs["reasons"][1]["text"] and "line 58" in rs["reasons"][1]["text"] and "line 73" in rs["reasons"][1]["text"]
    assert "producer assertion" in rs["reasons"][2]["text"]
    assert any("neither lane cuts a release alone" in c for c in rs["v1_conditions"])
    texts = {x["id"]: x["text"] for x in rs["reasons"]}
    assert "RE-LY and ROCKET-AF" in texts["KNOWN_INCORRECT_VALUES_ON_NAMED_PAGES"] and "0.73-1.04 at 97.5%" in texts["KNOWN_INCORRECT_VALUES_ON_NAMED_PAGES"]
    assert "30 of 53" in texts["VERIFY_LABEL_DEFECTS"] and "24 of 92" in texts["VERIFY_LABEL_DEFECTS"] and "PMID 27295427" in texts["VERIFY_LABEL_DEFECTS"]
    assert "121 of 145" in texts["ADMISSION_PATH_DEMONSTRATED_PERMEABLE"] and "0.68 (0.77-0.96)" in texts["ADMISSION_PATH_DEMONSTRATED_PERMEABLE"]
    assert texts["BOUNDED_REMEDY_ESTIMATED"].startswith("ESTIMATE, not a measurement")
    assert "PARITY-RELATION REFUSED" in texts["HAND_WRITTEN_STATUS_DESCRIBES_A_COMPUTED_RELATION"]
    assert rs["statement_currency"]["superseded_by"] is None and len(rs["statement_currency"]["expected_next"]) == 2 and "conclusions and outcome counts may change" in rs["statement_currency"]["expected_next"][0]
    assert rs["scope_boundary"].startswith("This label covers the pages served from this site.") and "rapidmeta-finerenone" in rs["scope_boundary"]
    assert len(rs["re_certifications_by_cause"]) == 4


def test_every_served_review_declares_it_and_every_page_renders_it():
    reviews = sorted(glob.glob(str(ROOT / "docs" / "reviews" / "*" / "review.json")))
    assert len(reviews) == 32
    for rp in reviews:
        r = json.load(open(rp, encoding="utf-8"))
        assert (r.get("release_status") or {}).get("status") == "PRE-RELEASE", rp
        html = open(os.path.join(os.path.dirname(rp), "index.html"), encoding="utf-8").read()
        assert "data-release-status='PRE-RELEASE'" in html and "PRE-RELEASE" in html, rp
        for need in REASONS:
            assert f"data-release-reason='{need}'" in html, (rp, need)
        assert "data-release-scope='boundary'" in html and "carry no label from here" in html, rp
        assert "data-release-currency='None'" in html and "This statement describes:" in html, rp
        assert "data-release-countersignature='NOT_COUNTERSIGNED'" in html and "What this label does not do:" in html, rp
        # at the top of the Overview tab: after the review title, before the next tab begins
        tabs = [m.start() for m in re.finditer(r"<h3 class=\"tabname\">", html)]
        pos = html.index("data-release-status='PRE-RELEASE'")
        assert tabs and tabs[0] < pos and (len(tabs) < 2 or pos < tabs[1]), (rp, pos, tabs[:2])


def test_renderer_is_silent_without_a_status_and_names_every_reason_with_one():
    assert page._prerelease_overview({}) == ""
    rs = json.load(open(ROOT / "registry" / "release_status.json", encoding="utf-8"))
    html = page._prerelease_overview({"release_status": rs})
    assert html.startswith("<div class='absent' data-release-status='PRE-RELEASE'>")
    for need in REASONS:
        assert f"data-release-reason='{need}'" in html
    assert "316d2e484174" not in html and "316d2e487417" in html        # the commit is shown as its first 12 characters


def _limb1_reasons_for(review_dir, html):
    manifest = json.load(open(os.path.join(review_dir, "manifest.json"), encoding="utf-8"))
    rep = json.load(open(os.path.join(review_dir, "REPRODUCTION.json"), encoding="utf-8"))
    return gate.check_limb1(review_dir, manifest, html, rep)


def test_gate_refuses_declared_but_not_rendered_and_rendered_but_not_declared(tmp_path):
    src = ROOT / "docs" / "reviews" / "glp1-ra-mace-t2d"
    html = open(src / "index.html", encoding="utf-8").read()
    # declared, notice stripped from the page
    stripped = html.replace("data-release-status='PRE-RELEASE'", "data-release-status='x'").replace("PRE-RELEASE", "PRE RELEASE")
    reasons = _limb1_reasons_for(str(src), stripped)
    assert any("carries no PRE-RELEASE notice" in x for x in reasons), reasons
    # one reason's rendering removed while the declaration keeps it
    partial = html.replace("data-release-reason='VERIFY_LABEL_DEFECTS'", "data-release-reason='removed'")
    reasons = _limb1_reasons_for(str(src), partial)
    assert any("VERIFY_LABEL_DEFECTS is declared but not rendered" in x for x in reasons), reasons
    # the other direction: a review that declares nothing but a page that renders the notice
    d = tmp_path / "rev"; d.mkdir()
    r = json.load(open(src / "review.json", encoding="utf-8")); r.pop("release_status", None)
    json.dump(r, open(d / "review.json", "w", encoding="utf-8"))
    for name in ("manifest.json", "REPRODUCTION.json"):
        (d / name).write_bytes((src / name).read_bytes())
    reasons = _limb1_reasons_for(str(d), html)
    assert any("renders a PRE-RELEASE notice the review does not declare" in x for x in reasons), reasons


def test_gate_refuses_unevidenced_approval_states_and_foreign_superseded_by(tmp_path):
    src = ROOT / "docs" / "reviews" / "glp1-ra-mace-t2d"
    html = open(src / "index.html", encoding="utf-8").read()
    base = json.load(open(src / "review.json", encoding="utf-8"))
    def with_review(mutate):
        d = tmp_path / ("rev%d" % len(list(tmp_path.iterdir()))); d.mkdir()
        r = json.loads(json.dumps(base)); mutate(r)
        json.dump(r, open(d / "review.json", "w", encoding="utf-8"))
        for name in ("manifest.json", "REPRODUCTION.json"):
            (d / name).write_bytes((src / name).read_bytes())
        return _limb1_reasons_for(str(d), html)
    for bad in ("APPROVED", "AGREED_IN_ADVANCE", "AUTHORISED_IN_PRINCIPLE", "VERBAL"):
        reasons = with_review(lambda r, b=bad: r["release_status"]["decision"]["countersignature"].__setitem__("state", b))
        assert any(f"{bad!r} is refused by name" in x for x in reasons), (bad, reasons)
    reasons = with_review(lambda r: r["release_status"]["decision"]["countersignature"].update({"state": "COUNTERSIGNED"}))   # no by/when/digest
    assert any("COUNTERSIGNED without" in x for x in reasons), reasons
    reasons = with_review(lambda r: r["release_status"]["statement_currency"].__setitem__("superseded_by", "approved"))
    assert any("must be null or a 40-hex commit" in x for x in reasons), reasons
    reasons = with_review(lambda r: r["release_status"]["statement_currency"].__setitem__("superseded_by", "f" * 40))
    assert any("not present in this repository" in x for x in reasons), reasons


def test_fix_ledger_records_the_relabel():
    d = json.load(open(ROOT / "registry" / "fixes.json", encoding="utf-8"))
    e = next(x for x in d["entries"] if x["finding_id"] == "RELEASE-316d2e48-PRERELEASE")
    assert e["scope"] == "CORPUS" and e["kind"] == "finding" and "registry/release_status.json" in e["seal"]["dependencies"]
    assert "316d2e487417a2d8e92ac88e2448488dd7ca3d40" in e["authored_against"]
