"""D8 (13 Oct, ruling 2: "the shared licence guard admits only CC BY / CC0"): harness/copy_licence is the BEFORE-the-call
selection of what a model may read, and it still called every Creative Commons copy 'CC' -- NC / ND / SA included --
in three places: the PMC permissions classifier, the cached index lookup, and the Unpaywall check. Found while
re-reading omega3 21115589 (CC BY-NC) after D8 incident #3: pmc_licence('21115589') returned 'CC'. A typed (regex)
reader is unaffected -- nothing it reads enters a record -- so it keeps reading a restricted copy."""
import json

from harness import copy_licence as cl

NC = ('<permissions><license xlink:href="http://creativecommons.org/licenses/by-nc/2.0/uk/">'
      '<license-p>This is an open-access article distributed under the terms of the Creative Commons '
      'Attribution Non-commercial License</license-p></license></permissions>')
BY = ('<permissions><license xlink:href="https://creativecommons.org/licenses/by/4.0/">'
      '<license-p>CC BY</license-p></license></permissions>')


def test_plant_an_nc_pmc_copy_is_not_cc():
    assert cl.classify_permissions(NC)[0] == "CC_RESTRICTED"
    assert cl.classify_permissions(BY)[0] == "CC"


def test_plant_a_cached_cc_entry_whose_statement_is_nc_is_not_cc(tmp_path):
    idx = tmp_path / "i.json"
    idx.write_text(json.dumps({"1": {"copy_licence": "CC", "copy_statement": "Creative Commons Attribution "
                                                                              "Non-commercial License"},
                               "2": {"copy_licence": "CC", "copy_statement": "CC BY 4.0"}}), encoding="utf-8")
    assert cl.pmc_licence("1", run=False, index_path=str(idx)) == "CC_RESTRICTED"
    assert cl.pmc_licence("2", run=False, index_path=str(idx)) == "CC"


def test_plant_an_unpaywall_nc_nd_or_sa_copy_is_not_open():
    for lic in ("cc-by-nc", "cc-by-nc-nd", "cc-by-nd", "cc-by-sa", "implied-oa", None):
        assert not cl.upw_open({"license": lic}), lic
    for lic in ("cc-by", "cc0", "public-domain"):
        assert cl.upw_open({"license": lic}), lic


def test_a_restricted_copy_never_reaches_a_model_prompt():
    text, ref = cl.locator_text({"title": "T", "abstract": "A"}, "FULL TEXT", "CC_RESTRICTED", "1")
    assert "FULL TEXT" not in text and "not CC" in ref


def test_the_live_omega3_copy_is_restricted():
    assert cl.pmc_licence("21115589", run=False) == "CC_RESTRICTED"


def test_a_typed_reader_still_reads_a_restricted_copy():
    assert cl.typed_may_read("CC_RESTRICTED") and cl.typed_may_read("CC") and not cl.typed_may_read("NOT_OPEN")


def test_plant_a_closed_copy_saying_non_commercial_is_not_creative_commons():
    """agy d8x-cap-r1-agy (P1): 'All rights reserved. Non-commercial use only.' matched the restriction pattern and became
    CC_RESTRICTED -- which typed readers accept -- widening typed access to a CLOSED copy. CC_RESTRICTED needs a
    Creative Commons licence actually named."""
    closed = ("<permissions><copyright-statement>(c) 2020 Publisher. All rights reserved. Non-commercial use only."
              "</copyright-statement></permissions>")
    assert cl.classify_permissions(closed)[0] == "NOT_OPEN"
    assert not cl.typed_may_read(cl.classify_permissions(closed)[0])
    assert cl.classify_permissions(NC)[0] == "CC_RESTRICTED"


def test_plant_a_denied_creative_commons_licence_is_not_one():
    """codex d8x-cap-r2 #1 (P1): 'not distributed under a Creative Commons licence ... non-commercial use only' NAMES
    Creative Commons only to deny it; it is a closed copy, never CC_RESTRICTED (which typed readers accept)."""
    denied = ("<permissions><copyright-statement>(c) 2021 Publisher. This article is not distributed under a Creative "
              "Commons licence. Non-commercial use only.</copyright-statement></permissions>")
    assert cl.classify_permissions(denied)[0] == "NOT_OPEN"
    assert cl.classify_permissions(NC)[0] == "CC_RESTRICTED"
