"""Execute the changed schema contracts on synthetic objects, without network I/O."""
import copy
import json

import pytest

from test_exchange_v01 import ROOT, exchange
from test_exchange_v01_validators import BOUNDARY_WHITESPACE, executed_manifest, manifest_fixture

# This is test tooling only; the runtime validator remains standard-library only.
jsonschema = pytest.importorskip("jsonschema")
SCHEMA_DIR = ROOT / "benchmarks/cross_repo/v0.1"


@pytest.fixture
def exchange_schema():
    spec = json.loads((SCHEMA_DIR / "exchange.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(spec)
    return jsonschema.Draft202012Validator(spec)


@pytest.fixture
def manifest_schema():
    spec = json.loads((SCHEMA_DIR / "manifest.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(spec)
    return jsonschema.Draft202012Validator(spec)


@pytest.mark.parametrize("field", ["study_id", "trial_id"])
@pytest.mark.parametrize("padding", BOUNDARY_WHITESPACE)
@pytest.mark.parametrize("side", ["leading", "trailing"])
def test_schema_refuses_identity_padding(exchange_schema, field, padding, side):
    item = exchange()
    value = item["rows"][0][field]
    item["rows"][0][field] = padding + value if side == "leading" else value + padding
    assert not exchange_schema.is_valid(item)


@pytest.mark.parametrize("locator", ["page 2", "line 0", "line 02", "line 2\n", "lines 1-9999999999"])
def test_schema_refuses_malformed_locators(exchange_schema, locator):
    item = exchange()
    item["rows"][0]["source_span"]["locator"] = locator
    assert not exchange_schema.is_valid(item)


def test_schema_keeps_canonical_ids_and_internal_spaces(exchange_schema):
    item = exchange()
    item["rows"][0].update(study_id="S", trial_id="SYNTHETIC TRIAL 001")
    exchange_schema.validate(item)


@pytest.mark.parametrize("section", ["root", "repository", "case", "coverage", "run_evidence"])
def test_schema_closed_manifest_objects(manifest_schema, section):
    item = executed_manifest()
    target = {"root": item, "repository": item["repositories"]["rapidmeta-kit"],
              "case": item["cases"][0], "coverage": item["coverage"][0],
              "run_evidence": item["cases"][0]["run_evidence"]}[section]
    target["unversioned_override"] = True
    assert not manifest_schema.is_valid(item)


@pytest.mark.parametrize("status", ["PASS", "FAIL"])
def test_schema_requires_execution_record(manifest_schema, status):
    item = manifest_fixture()
    item["cases"][0]["status"] = status
    assert not manifest_schema.is_valid(item)
    manifest_schema.validate(executed_manifest(status))


@pytest.mark.parametrize("status", ["NOT_RUN", "BLOCKED"])
def test_schema_forbids_nonexecuted_evidence(manifest_schema, status):
    item = executed_manifest()
    item["cases"][0]["status"] = status
    assert not manifest_schema.is_valid(item)


@pytest.mark.parametrize("field,value", [
    ("action_run_url", "https://github.com/other-owner/meta-harness/actions/runs/123"),
    ("action_run_url", "https://github.com/mahmood726-cyber/unpinned-repo/actions/runs/123"),
    ("action_run_url", "https://github.com/mahmood726-cyber/meta-harness/actions/runs/0"),
    ("action_run_url", "https://github.com/mahmood726-cyber/meta-harness/actions/runs/123\n"),
    ("commit_sha", "0" * 39), ("commit_sha", "0" * 40 + "\n"),
    ("input_sha256", "0" * 63), ("job_name", ""),
])
def test_schema_requires_well_formed_execution_fields(manifest_schema, field, value):
    item = executed_manifest()
    item["cases"][0]["run_evidence"][field] = value
    assert not manifest_schema.is_valid(item)


def test_schema_requires_case_floor(manifest_schema):
    item = manifest_fixture()
    item["cases"].pop()
    assert not manifest_schema.is_valid(item)


@pytest.mark.parametrize("cid", ["CROSS-R-014", "CROSS-EXCH-000", "CROSS-EXCH-14", "CROSS-EXCH-014\n"])
def test_schema_requires_transport_namespace(manifest_schema, cid):
    item = manifest_fixture()
    item["cases"][-1]["id"] = cid
    assert not manifest_schema.is_valid(item)


def test_schema_allows_contiguous_future_case(manifest_schema):
    item = manifest_fixture()
    future = copy.deepcopy(item["cases"][-1])
    future["id"] = "CROSS-EXCH-015"
    item["cases"].insert(0, future)
    manifest_schema.validate(item)
