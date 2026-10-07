"""PLANT (6 Oct licence incident: mc-60163e27 + 10 locate records embedded non-CC-BY full text): a recorded locate
prompt carries full text only under a CC BY / CC0 licence; abstracts / AACT / regulatory text always; unknown = closed."""
import json
import os
import sys
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))

import g1_licence as gl  # noqa: E402


def test_gate_keeps_only_licensed_full_text(tmp_path):
    c = {"1": {"license": "cc by", "open": True}, "2": {"license": "cc by-nc", "open": False},
         "3": {"license": None, "open": False}}
    p = tmp_path / "lic.json"
    p.write_text(json.dumps(c), encoding="utf-8")
    texts = [("PMC_OA", "full"), ("UNPAYWALL", "full2"), ("ABSTRACT", "abs"), ("AACT", "posted")]
    with patch.object(gl, "CACHE", str(p)), patch.object(gl, "repo_open", lambda *a, **k: True):
        assert [k for k, _ in gl.gate("1", texts)[0]] == ["PMC_OA", "UNPAYWALL", "ABSTRACT", "AACT"]
        assert [k for k, _ in gl.gate("2", texts)[0]] == ["ABSTRACT", "AACT"]
        assert [k for k, _ in gl.gate("3", texts)[0]] == ["ABSTRACT", "AACT"]
        assert [k for k, _ in gl.gate("4", texts, offline=True)[0]] == ["ABSTRACT", "AACT"]   # unknown = closed


def test_locate_prompt_never_embeds_unlicensed_full_text(tmp_path):
    import g1_binding_locate as loc
    c = {"34420373": {"license": "cc by-nc-nd", "open": False}}
    p = tmp_path / "lic.json"
    p.write_text(json.dumps(c), encoding="utf-8")
    t = {"slug": "colchicine-secondary-cv-prevention", "label": "Mewton et al. (26)", "pmids": ["34420373"]}
    fake = [("PMC_OA", "SECRET FULL TEXT BODY"), ("UNPAYWALL", "SECRET UNPAYWALL BODY")]
    with patch.object(gl, "CACHE", str(p)), patch.object(loc.dg, "held_texts", lambda *a, **k: list(fake)):
        it = loc.item(t, "34420373")
    assert b"SECRET" not in it["prompt"] and set(it["sources"]) <= {"ABSTRACT"}
    assert it["licence_dropped"] and it["licence_dropped"][0]["why"].startswith("LICENCE_NOT_CC_BY_OR_CC0")


def test_cc_by_alone_is_not_enough_when_the_repo_guard_says_the_copy_is_not_open(tmp_path):
    p = tmp_path / "lic.json"
    p.write_text(json.dumps({"1": {"license": "cc by", "open": True}}), encoding="utf-8")
    with patch.object(gl, "CACHE", str(p)), patch.object(gl, "repo_open", lambda *a, **k: False):
        assert [k for k, _ in gl.gate("1", [("PMC_OA", "x"), ("ABSTRACT", "a")])[0]] == ["ABSTRACT"]


def test_the_locate_record_declares_its_source_in_the_guards_form():
    from reproducible_ai import record_licence as rl
    srcs = rl.ref_licences("held open text PMID 34876021 (PMC_OA+ABSTRACT)", {"34876021": "CC"}, {})
    assert srcs == [("PMID 34876021 PMC_OA", "CC")]
