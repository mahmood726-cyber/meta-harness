from pathlib import Path
import ast

p = Path('tests/test_week_regressions_audit.py')
s = p.read_text(encoding='utf-8')
tree = ast.parse(s)
mapping = {
    'harms': ['test_generic_adverse_events_do_not_prove_specific_harm'],
    'missing': ['test_missing_candidates_merge_family_and_report_identity'],
    'overlap': ['test_comparator_only_text_cannot_establish_current_pool_overlap'],
    'screening': ['test_title_omission_requires_review_not_ineligibility'],
    'adjustment': ['test_adjustment_labels_require_estimator_evidence', 'test_adjustment_plant_fires_on_pinned_parent'],
    'reason': ['test_kidney_and_cv_death_values_do_not_prove_mace_value'],
}
lines = s.splitlines(True)
header = ''.join(lines[:next(n.lineno - 1 for n in tree.body if isinstance(n, ast.FunctionDef))])
chunks = {}
for node in tree.body:
    if isinstance(node, ast.FunctionDef):
        start = min([node.lineno] + [d.lineno for d in node.decorator_list]) - 1
        chunks[node.name] = ''.join(lines[start:node.end_lineno]) + chr(10) * 2
for family, names in mapping.items():
    text = header + 'from test_week_regressions_audit import load_pin, estimator_requirement' + chr(10) * 2
    text += ''.join(chunks[name] for name in names)
    Path('tests/test_week_regressions_' + family + '.py').write_text(text, encoding='utf-8')
p.write_text(header + chunks['load_pin'] + chunks['estimator_requirement'], encoding='utf-8')
p = Path('tests/test_week_regressions_owner_patches.py')
s = p.read_text(encoding='utf-8').replace('import pytest', 'import pytest\nimport importlib')
s = s.replace("    patched = audit.load_pin", "    family = {'harms': 'harms', 'known_missing': 'missing', 'comparator_second_pass': 'overlap', 'screen': 'screening', 'reason_audit': 'reason'}[module]\n    tests = importlib.import_module('test_week_regressions_' + family)\n    patched = audit.load_pin")
s = s.replace('monkeypatch.setattr(audit, module, patched)', 'monkeypatch.setattr(tests, module, patched)').replace('getattr(audit, test)', 'getattr(tests, test)')
p.write_text(s, encoding='utf-8')
