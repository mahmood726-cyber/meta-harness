"""Replay failing contracts with the HEAD renderer/graph, without changing files."""
import importlib.util
import subprocess
import sys
import types
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
import harness

for name in ('claimgraph', 'page'):
    module_name = 'harness.' + name
    module = types.ModuleType(module_name)
    module.__package__ = 'harness'
    module.__file__ = str(root / 'harness' / (name + '.py'))
    module.__spec__ = importlib.util.spec_from_loader(module_name, loader=None)
    sys.modules[module_name] = module
    setattr(harness, name, module)
    source = subprocess.check_output(['git', 'show', 'HEAD:harness/' + name + '.py'], cwd=root).decode('utf-8')
    exec(compile(source, module.__file__, 'exec'), module.__dict__)

import pytest
raise SystemExit(pytest.main([
    '-q', '--tb=short',
    'tests/test_fixstate.py::test_real_store_validates',
    'tests/test_gate.py::test_valid_page_passes_non_replay_limbs',
    'tests/test_gate_scorecard.py::test_real_registry_passes',
    'tests/test_integrity.py::test_committed_integrity_is_fresh_for_every_live_topic',
    'tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews',
    'tests/test_override_audit.py::test_override_audit_covers_every_committed_override',
    'tests/test_stage_additions.py::test_manuscript_limb_passes_on_every_live_review',
    'tests/test_stage_additions.py::test_manuscript_limb_REFUSES_a_fabricated_number',
    'tests/test_stage_additions.py::test_error_rate_is_fresh_against_current_pooled_population',
]))
