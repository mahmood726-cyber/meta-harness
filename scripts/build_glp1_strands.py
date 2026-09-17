"""Generate GLP1's additive verified-effect source objects, offline."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.glp1_sources import entries, SLUG

if __name__ == '__main__':
    rows = entries()
    (ROOT / 'cache' / SLUG / 'verified_effects.json').write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='')
    print(f'{len(rows)} of {len(rows)} entries verified against held documents')
