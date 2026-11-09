"""Synthetic review controls; no clinical results or certificate writes."""
import json

import pytest

import test_certificate_code_closure as certificate_tests
from harness import certificate
from harness.exchange_v01 import _verify_text_locator, validate_manifest
from harness.exchange_v01.wire import validate_manifest_json
from harness.provenance.evidence import REQUIRED, can_pool, sha256, validate_extraction
from test_exchange_v01_validators import MANIFEST, manifest_fixture


@pytest.mark.parametrize("separator", ["\u2028", "\u2029", "\x0b", "\x0c", "\x1c", "\x1d", "\x1e", "\x85", "\r"])
def test_locator_counts_only_lf_and_refuses_shifted_line(separator):
    content = f"a{separator}HR 0.80\nb\n"
    _verify_text_locator(content, "line 1", "HR 0.80")
    with pytest.raises(ValueError, match="passage absent at cited source lines"):
        _verify_text_locator(content, "line 2", "HR 0.80")


@pytest.mark.parametrize("ending", ["\n", "\r\n"])
def test_locator_preserves_line_endings_without_phantom_final_line(ending):
    content = f"a{ending}HR 0.80{ending}"
    _verify_text_locator(content, "line 2", f"HR 0.80{ending}")
    _verify_text_locator(content, "lines 1-2", content)
    with pytest.raises(ValueError, match="outside source line range"):
        _verify_text_locator(content, "line 3", "HR 0.80")


@pytest.mark.parametrize("analysis", [None, [], "ALLOW", True, 1])
def test_9fca5db27_malformed_analysis_refuses(analysis):
    assert can_pool(analysis, {}) is False


@pytest.mark.parametrize("field", ["study_id", "source_uri", "field_name", "population", "outcome", "time_point", "effect_measure"])
@pytest.mark.parametrize("value", ["", " \t", None, False, 0, [], {}])
def test_pr125_source_checked_requires_context(field, value):
    content = b"synthetic source: HR 0.80"
    record = dict.fromkeys(REQUIRED, "synthetic")
    record.update(document_sha256=sha256(content), verbatim_passage="HR 0.80", status="SOURCE_CHECKED")
    assert validate_extraction(record, content) is True
    record[field] = value
    with pytest.raises(ValueError, match="source-checked evidence requires clinical context"):
        validate_extraction(record, content)


@pytest.mark.parametrize("check", [validate_manifest, validate_manifest_json])
def test_empty_manifest_cases_has_named_refusal(check):
    item = manifest_fixture()
    item["cases"] = []
    payload = json.dumps(item).encode("utf-8") if check is validate_manifest_json else item
    with pytest.raises(ValueError, match="^cases missing$"):
        check(payload, MANIFEST.parent)


@pytest.mark.parametrize("check", [
    certificate_tests.test_opt_in_exchange_package_preserves_legacy_signed_certificate_scopes,
    certificate_tests.test_opt_in_benchmark_exchange_does_not_change_signed_certificate_scope,
])
def test_certificate_scope_assertion_detects_injected_exchange_package(monkeypatch, check):
    """Plant a consistent in-memory scope containing the actual package path."""
    original_loads = json.loads

    def inject_package(*args, **kwargs):
        saved = original_loads(*args, **kwargs)
        if isinstance(saved, dict) and "analysis_code_blobs" in saved:
            saved["analysis_code_blobs"]["harness/exchange_v01/__init__.py"] = "a" * 40
            saved["certificate_scope"] = certificate._scope(saved["analysis_code_blobs"])
        return saved

    monkeypatch.setattr(json, "loads", inject_package)
    with pytest.raises(AssertionError):
        check()
