"""Preview contracts; all input and output files are isolated synthetic fixtures."""
import builtins
import html
import io
import json
import os
from html.parser import HTMLParser
from pathlib import Path

import pytest

from robgrade import rob2_formal, rob2_tab
from scripts import grade_formal_build


@pytest.fixture
def preview(tmp_path, monkeypatch):
    from scripts import tab_preview_build as builder

    monkeypatch.setattr(builder, "ROOT", tmp_path)
    tiers = [(label, tmp_path / f"tier-{i}")
             for i, (label, _) in enumerate(grade_formal_build.TIERS)]
    monkeypatch.setattr(grade_formal_build, "TIERS", tiers)
    obj = rob2_formal.assessment("PMID 1", "primary <script>", {})
    obj["domains"]["D1"]["answers"]["1.2"] = {
        "answer": "PY", "basis": "contextual", "span": "quote <script>"}
    second = rob2_formal.assessment("PMID 3", "primary <script>", {
        q: {"answer": answer} for q, answer in {
            "1.1": "Y", "1.2": "Y", "1.3": "N", "2.1": "N", "2.2": "N",
            "2.6": "Y", "3.1": "Y", "4.1": "N", "4.2": "N", "4.3": "N",
            "5.1": "Y", "5.2": "N", "5.3": "N",
        }.items()})
    grade = {"certainty": "provisional", "certainty_from_assessed_domains_only": "low",
             "domains": {"risk_of_bias": {"downgrade": None, "state": "NOT_ASSESSED",
                                         "basis": "basis <script>"}},
             "judgement_flags": ["flag <script>"],
             "certainty_change": {"from": "high", "to": "provisional"}}
    inputs = {
        "docs/reviews/topic/review.json": {"outcomes": [
            {"name": "secondary", "trials": [{"id": "PMID 99"}]},
            {"name": "primary <script>", "primary": True,
             "trials": [{"id": trial_id} for trial_id in (
                 "PMID 1", "PMID 2", "NCT00000001", "PMID 3", "PMID 4", "NCT00000002")]}]},
        "outputs/robgrade/grade/topic.json": grade,
        "tier-0/topic.json": {"outcome": "primary <script>", "trials": {"1": obj}},
        "tier-1/topic.json": {"outcome": "primary <script>", "trials": {"3": second}},
    }
    for name, value in inputs.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")
    (tmp_path / "docs/reviews/not-served").mkdir()
    return builder, tmp_path, obj


def rendered(preview):
    builder, root, _ = preview
    builder.main([])
    return (root / "outputs/robgrade/tab_preview_served/topic.html").read_text(encoding="utf-8")


class PreviewHTML(HTMLParser):
    """Collect decoded table cells and actual tags/attributes, not escaped prose."""

    def __init__(self, page):
        super().__init__(convert_charrefs=True)
        self.tables = []
        self.tags = []
        self.cell = None
        self.feed(page)
        self.close()

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        if tag == "table":
            self.tables.append([])
        elif tag == "tr":
            self.tables[-1].append([])
        elif tag in ("th", "td"):
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("th", "td"):
            self.tables[-1][-1].append("".join(self.cell))
            self.cell = None


def assert_trial_rows(page, root):
    # Read the fixture objects independently of the builder's source selection.
    objects = {}
    for tier, label in [(0, "served contextual (A3)"), (1, "contextual (A3)")]:
        doc = json.loads((root / f"tier-{tier}/topic.json").read_text(encoding="utf-8"))
        for pmid, obj in doc["trials"].items():
            objects[f"PMID {pmid}"] = (label, obj)
    assert objects["PMID 1"][1]["overall"]["judgement"] != objects["PMID 3"][1]["overall"]["judgement"]
    expected = [["Trial", "Source tier", *rob2_formal.DOMAINS, "Overall"]]
    for trial_id in ("PMID 1", "PMID 2", "NCT00000001", "PMID 3", "PMID 4", "NCT00000002"):
        if trial_id in objects:
            tier, obj = objects[trial_id]
            expected.append([trial_id, tier] + [
                rob2_tab.domain_label(obj["domains"][d]) for d in rob2_formal.DOMAINS
            ] + [rob2_tab.overall_label(obj["overall"], obj["domains"])])
        else:
            expected.append([trial_id, "No source object"] +
                            ["No formal RoB 2 assessment yet"] * (len(rob2_formal.DOMAINS) + 1))
    assert PreviewHTML(page).tables[0] == expected


def test_exact_labels_and_sources_for_each_trial_row(preview):
    assert_trial_rows(rendered(preview), preview[1])


def test_row_contract_rejects_swapped_trial_labels(preview, monkeypatch):
    builder, root, _ = preview
    original = builder.table

    def swapped_table(headers, rows):
        copied = [list(row) for row in rows]
        if headers[0] == "Trial":
            # Plant only in a test-local copy: identities and tiers stay intact.
            copied[0][2:], copied[3][2:] = copied[3][2:], copied[0][2:]
        return original(headers, copied)

    with monkeypatch.context() as patch:
        patch.setattr(builder, "table", swapped_table)
        with pytest.raises(AssertionError):
            assert_trial_rows(rendered(preview), root)
    assert_trial_rows(rendered(preview), root)


def test_missing_object_has_explicit_row(preview):
    page = rendered(preview)
    assert "PMID 2</th><td>" in page
    assert "No formal RoB 2 assessment yet" in page
    assert "PMID 99" not in page


def test_source_tier_per_trial(preview):
    assert "PMID 1</th><td>served contextual (A3)</td>" in rendered(preview)


def test_labels_are_existing_renderers_exact_output(preview):
    page = rendered(preview)
    obj = preview[2]
    for domain in obj["domains"].values():
        assert f"<td>{html.escape(rob2_tab.domain_label(domain))}</td>" in page
    assert f"<td>{html.escape(rob2_tab.overall_label(obj['overall'], obj['domains']))}</td>" in page


def test_unsigned_change_and_grade_summary(preview):
    page = rendered(preview)
    for value in ["UNSIGNED -- for the signing packet", "certainty_from_assessed_domains_only",
                  "low", "NOT_ASSESSED", "basis &lt;script&gt;", "flag &lt;script&gt;", "high"]:
        assert value in page


def test_values_are_escaped(preview):
    page = rendered(preview)
    assert "<script>" not in page
    assert "primary &lt;script&gt;" in page
    assert "quote &lt;script&gt;" in page


def test_output_write_allowlist_and_index_covers_served_topics(preview, monkeypatch):
    builder, root, _ = preview
    out = (root / "outputs/robgrade/tab_preview_served").resolve()
    writes = []

    def allowed(path):
        resolved = Path(path).resolve()
        assert resolved.is_relative_to(out), f"Write outside preview output: {resolved}"
        writes.append(resolved)

    before = {p: p.read_bytes() for p in (root / "docs").rglob("*") if p.is_file()}
    for module in (builtins, io):
        original = module.open

        def guarded(path, mode="r", *args, _open=original, **kwargs):
            if not isinstance(path, int) and any(flag in mode for flag in "wax+"):
                allowed(path)
            return _open(path, mode, *args, **kwargs)

        monkeypatch.setattr(module, "open", guarded)
    original_makedirs = os.makedirs
    original_write_text = Path.write_text
    original_mkdir = Path.mkdir

    def guarded_makedirs(path, *args, **kwargs):
        allowed(path)
        return original_makedirs(path, *args, **kwargs)

    def guarded_write_text(path, *args, **kwargs):
        allowed(path)
        return original_write_text(path, *args, **kwargs)

    def guarded_mkdir(path, *args, **kwargs):
        allowed(path)
        return original_mkdir(path, *args, **kwargs)

    monkeypatch.setattr(os, "makedirs", guarded_makedirs)
    monkeypatch.setattr(Path, "write_text", guarded_write_text)
    monkeypatch.setattr(Path, "mkdir", guarded_mkdir)
    builder.main([])
    assert {out / "index.html", out / "topic.html"} <= set(writes)
    assert before == {p: p.read_bytes() for p in (root / "docs").rglob("*") if p.is_file()}
    out = root / "outputs/robgrade/tab_preview_served"
    assert sorted(p.name for p in out.iterdir()) == ["index.html", "topic.html"]
    index = (out / "index.html").read_text(encoding="utf-8")
    for value in ["topic", "<td>6</td>", "<td>2</td>", "served contextual (A3): 1", "provisional",
                  "flag &lt;script&gt;", "PREVIEW -- not served"]:
        assert value in index
    assert "PREVIEW -- not served" in (out / "topic.html").read_text(encoding="utf-8")


def test_every_preview_page_has_no_external_resources(preview):
    rendered(preview)
    out = preview[1] / "outputs/robgrade/tab_preview_served"
    pages = sorted(out.glob("*.html"))
    assert [p.name for p in pages] == ["index.html", "topic.html"]
    for path in pages:
        page = path.read_text(encoding="utf-8")
        for tag, attrs in PreviewHTML(page).tags:
            assert tag not in {"link", "script"}, path.name
            for attribute in ("src", "href"):
                value = (attrs.get(attribute) or "").strip().lower()
                assert not value.startswith(("http:", "https:", "//")), (path.name, value)
        for forbidden in ("<link", "<script", "@import", "url("):
            assert forbidden not in page.lower(), (path.name, forbidden)
