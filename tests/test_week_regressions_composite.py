"""Execute the pipeline's actual disclosure block with an unrelated abstract."""
import ast
from pathlib import Path
import pytest
from harness import extract

ROOT = Path(__file__).resolve().parents[1]


def disclosure(path):
    tree = ast.parse(path.read_text(encoding='utf-8'))
    for parent in ast.walk(tree):
        body = getattr(parent, 'body', None)
        if not isinstance(body, list):
            continue
        for i, node in enumerate(body):
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '_ch_srcs' for t in node.targets):
                block = ast.Module(body=body[i:i + 3], type_ignores=[])
                core = 'The composite of cardiovascular death, nonfatal myocardial infarction, and nonfatal stroke.'
                extra = 'The primary outcome was a composite of cardiovascular death, myocardial infarction, stroke, and unstable angina.'
                env = {'extract': extract, 'spec': {'name': 'MACE'},
                       'trials': [{'id': 'plant-a', 'source': core, 'endpoint_definition_span': core}, {'id': 'plant-b', 'source': core, 'endpoint_definition_span': core}],
                       'rec_by_id': {'plant-a': {'abstract': extra}, 'plant-b': {'abstract': core}}}
                exec(compile(block, str(path), 'exec'), env)
                return env['_ch']
    raise AssertionError('pipeline disclosure block not found')


@pytest.mark.xfail(strict=True, reason='READY-BEHIND-INTEGRATOR: outputs/handover/patches/RG/composite-selection.diff')
def test_selected_endpoint_controls_composite_warning():
    assert not disclosure(ROOT / 'harness/pipeline.py')


def test_composite_patch_holds():
    assert not disclosure(ROOT / 'tests/fixtures/week_regressions/prefix/patched/harness/pipeline.py')
