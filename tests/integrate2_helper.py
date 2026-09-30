"""Verification helper only: load the PRE-INTEGRATION harness code without checkout or git mutation."""
import importlib.abc
import importlib.util
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASELINE = False
# The unwired baseline is pinned to the last commit before the lane wiring landed. Diffing against HEAD would make the
# baseline equal to the wired code once the wiring is committed, and every with/without comparison would pass vacuously.
PRE_WIRING_COMMIT = 'b0ae05a7cf440048ef07338ab2cf756dccf3241a'

class HeadLoader(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self):
        self.sources = {}
        changed = subprocess.check_output(['git', '--no-optional-locks', 'diff', '--name-only', PRE_WIRING_COMMIT],
                                          cwd=ROOT, text=True).splitlines()
        existed = set(subprocess.check_output(['git', '--no-optional-locks', 'ls-tree', '-r', '--name-only',
                                               PRE_WIRING_COMMIT, 'harness/'], cwd=ROOT, text=True).splitlines())
        for rel in changed:
            if rel.startswith('harness/') and rel.endswith('.py') and rel in existed:
                self.sources[rel[:-3].replace('/', '.')] = subprocess.check_output(
                    ['git', 'show', f'{PRE_WIRING_COMMIT}:' + rel], cwd=ROOT)
    def find_spec(self, fullname, path=None, target=None):
        if fullname in self.sources:
            return importlib.util.spec_from_loader(fullname, self, origin=str(ROOT / (fullname.replace('.', '/') + '.py')))
    def create_module(self, spec):
        return None
    def exec_module(self, module):
        module.__file__ = str(ROOT / (module.__name__.replace('.', '/') + '.py'))
        exec(compile(self.sources[module.__name__], module.__file__, 'exec'), module.__dict__)

def enable_baseline():
    global BASELINE
    BASELINE = True
    sys.meta_path.insert(0, HeadLoader())
