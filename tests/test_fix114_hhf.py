"""The retained acquisition must resolve the abridged-cache hHF extraction debt."""
import json
from pathlib import Path

from scripts.recover_dpp4_hhf import PMID, SLUG, recover

ROOT = Path(__file__).resolve().parents[1]


def test_hhf_cache_is_reproducible_from_retained_source():
    expected = recover()
    data = json.loads((ROOT / "cache" / SLUG / "verified_effects.json").read_text(encoding="utf-8"))
    entries = data.get(PMID, [])
    entries = entries if isinstance(entries, list) else [entries]
    assert expected in entries
    from harness.verified_inputs import load
    loaded = load(SLUG)["verified_effects.json"][PMID]
    matching = next(e for e in loaded if e["outcome"] == expected["outcome"])
    assert matching["kind"] == "extracted_effect"
    assert "span_refusal" not in matching


def test_hhf_recovery_binds_to_held_document():
    from harness.hand_binding import bind_hand_row
    config = json.loads((ROOT / "topics" / f"{SLUG}.json").read_text(encoding="utf-8"))
    row = recover()
    spec = next(s for s in config["harm_outcomes"] if s["name"] == row["outcome"])
    bound = bind_hand_row(spec, dict(row, id=PMID))
    assert bound["hand_binding_state"] == "BOUND", bound.get("endpoint_binding_reason")
    assert bound["target_endpoint_class"] == "EXACT_TARGET"
