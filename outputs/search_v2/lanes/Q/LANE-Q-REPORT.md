Q VERDICT: D3i post-fix FIRED; real gate PASS; acronym coverage 99 of 278 (was 11); D1c post-fix FIRED; collisions 0 of 32

Diff stat:

```text
harness/search_completeness.py       |   2 +
registry/search_vocabulary_seal.json | 222 ++++++++++++++++++++++++-----------
scripts/seal_search_vocabulary.py    |  48 ++++++--
tests/test_search_completeness.py    |   4 +-
tests/test_search_v2_guard.py        |  40 +++++++
5 files changed, 234 insertions(+), 82 deletions(-)
```

Post-fix artefacts:

- `lane_q/01-d3i-postfix.txt`: D3i post-fix FIRED; deleting one MEASUREMENT topic now refuses and names `colchicine-postop-af` as NOT_RUN.
- `lane_q/02-real-gate.txt`: real registry PASS; all 21 MEASUREMENT topics are present with NOT_RUN 0 of 21.
- `lane_q/03-d1c-postfix.txt`: D1c post-fix FIRED; `FOURIER` resolves to a benchmark acronym collision and the query is refused as NAME_SEEDED.

Acronym coverage:

- Committed seal via `--records-root C:/meta-harness`: 99 of 278 benchmark positives have a resolvable registered acronym.
- Explicit r2 snapshot check via `record_paths=`: 97 of 278 benchmark positives have a resolvable registered acronym.
- Sealer check: `SEAL OK: 32 of 32 sealed vocabularies match the working tree, 0 of 32 collide`.

Newly resolved unique acronyms in the committed seal (86):

```text
affirm-ahf
amplitude-o
aristotle
arts-dn
ascend
basics
canvas
cape_cod
cocs
codex
colchicine-pci
colcot
coloct
confirm-hf
copps-2
corimuno-toc
corp
corp 2
covacta
covert-mi
covid steroid
credence
dapa-ckd
dapa-hf
declare-timi58
deliver
do-health
effect-hf
ekstrom
elixa
empa-heart
empacta
emphasis-hf
empire hf
end-afld
engageaftimi48
escape
examine
fair-hf
fair-hf2
fidelio-dkd
figaro-dkd
fourier
heart-fid
ironman
leader\u00ae
metcovid
omega
origin
ovidius
paradigm-hf
pearl
pioneer 6
plato
plus
preserved-hf
re-cover i
re-cover ii
recovery
reduce-it
remap-cap
rewind
sacbo
salt
savor- timi 53
select
semalco
simple
smart-med
spaada
staree
step
step 1
step 3
step 6
step hfpef dm
step12
step7
strength
sustain\u2122 6
tecos
tocibras
traces
transform-2
vital
woman
```

Finish-condition tests:

```text
python -m pytest tests/test_search_completeness.py tests/test_search_v2_guard.py tests/test_search_benchmark_isolation.py -q
27 passed in 5.74s
```

Commands run:

```text
Get-Content -Raw -LiteralPath .\LANE_PROMPT.md
Get-Content -Raw -LiteralPath F:\ProjectIndex\INDEX.md
Get-Content -Raw -LiteralPath F:\E156\rewrite-workbook.txt
git status --short
Get-Content -Raw -LiteralPath .\harness\search_completeness.py
Get-Content -Raw -LiteralPath .\scripts\seal_search_vocabulary.py
Get-Content -Raw -LiteralPath .\tests\test_search_completeness.py
Get-Content -Raw -LiteralPath .\tests\test_search_v2_guard.py
Get-Content -Raw -LiteralPath .\tests\test_search_benchmark_isolation.py
Get-Content -Raw -LiteralPath C:\meta-harness\outputs\search_v2\lanes\P\lane_p\plants.txt
Get-Content -Raw -LiteralPath .\registry\search_completeness.json
Get-Content -Raw -LiteralPath .\registry\search_benchmark_split.json
Get-Content -Raw -LiteralPath .\harness\search_v2.py
Get-Content -Raw -LiteralPath .\registry\search_vocabulary_seal.json
rg --files C:\meta-harness\cache -g records.json
Get-Content -Raw -LiteralPath .\registry\search_benchmark.json
rg "benchmark_acronyms|records-root|search_vocabulary" -n .
rg "def _normalise_nct|def _normalise_pmid|acronym" -n harness scripts tests
Get-ChildItem -Path C:\meta-harness\cache -Directory | ForEach-Object { $p = Join-Path $_.FullName 'snapshots\2026-09-15r2-search_v2\records.json'; if (Test-Path -LiteralPath $p) { $p } }
python -m pytest tests/test_search_completeness.py tests/test_search_v2_guard.py tests/test_search_benchmark_isolation.py -q
python -c "from scripts import seal_search_vocabulary as s; import glob; paths=glob.glob(r'C:/meta-harness/cache/*/snapshots/2026-09-15r2-search_v2/records.json'); b=s.benchmark_acronyms(record_paths=paths); print(b['coverage_text']); print('\n'.join(sorted(b['acronyms'])))"
python scripts/seal_search_vocabulary.py --at 41a466fb --records-root C:/meta-harness
python scripts/seal_search_vocabulary.py --check
python -c "import json; p=json.load(open('outputs/search_v2/candidates-2026-09-15r3-all.json', encoding='utf-8')); print(type(p['topics']).__name__, len(p['topics'])); print(list(p['topics'])[:5]); print(p['topics'][list(p['topics'])[0]].keys())"
python -c "from harness import search_completeness as s; print(s.check('.'))"
python -c "import json; cfg=json.load(open('topics/pcsk9-mace.json', encoding='utf-8')); print(cfg)"
Get-Content -Path .\harness\pipeline.py -TotalCount 230
python -c "import json, glob; from scripts import seal_search_vocabulary as s; old=json.load(open('registry/search_vocabulary_seal.json', encoding='utf-8')); print(old['benchmark_acronym_registry']['coverage_text']); print('\n'.join(old['benchmark_acronym_registry']['acronyms']))"
git diff -- harness/search_completeness.py tests/test_search_completeness.py scripts/seal_search_vocabulary.py tests/test_search_v2_guard.py registry/search_vocabulary_seal.json
python -c "import json, subprocess; old=json.loads(subprocess.check_output(['git','show','HEAD:registry/search_vocabulary_seal.json'], text=True, encoding='utf-8')); new=json.load(open('registry/search_vocabulary_seal.json', encoding='utf-8')); added=sorted(set(new['benchmark_acronym_registry']['acronyms'])-set(old['benchmark_acronym_registry']['acronyms'])); print(len(added)); print(json.dumps(added, ensure_ascii=True, indent=2))"
python -c "import glob, json; from scripts import seal_search_vocabulary as s; old=json.loads(__import__('subprocess').check_output(['git','show','HEAD:registry/search_vocabulary_seal.json'], text=True, encoding='utf-8')); paths=glob.glob(r'C:/meta-harness/cache/*/snapshots/2026-09-15r2-search_v2/records.json'); b=s.benchmark_acronyms(record_paths=paths); added=sorted(set(b['acronyms'])-set(old['benchmark_acronym_registry']['acronyms'])); print(b['coverage_text']); print(len(added)); print(json.dumps(added, ensure_ascii=True, indent=2))"
git diff --stat
New-Item -ItemType Directory -Force -Path .\lane_q | Out-Null; attempted python -c D3i capture script (failed before execution because PowerShell stripped Python quotes)
New-Item -ItemType Directory -Force -Path .\lane_q | Out-Null; $code | python -; wrote lane_q\01-d3i-postfix.txt
New-Item -ItemType Directory -Force -Path .\lane_q | Out-Null; python -c "from harness import search_completeness as s; print(s.check('.'))"; wrote lane_q\02-real-gate.txt
New-Item -ItemType Directory -Force -Path .\lane_q | Out-Null; $code | python -; wrote lane_q\03-d1c-postfix.txt
python -m pytest tests/test_search_completeness.py tests/test_search_v2_guard.py tests/test_search_benchmark_isolation.py -q
Get-Content -Raw -LiteralPath .\lane_q\01-d3i-postfix.txt
Get-Content -Raw -LiteralPath .\lane_q\02-real-gate.txt
Get-Content -Raw -LiteralPath .\lane_q\03-d1c-postfix.txt
git status --short
git diff --check -- harness/search_completeness.py scripts/seal_search_vocabulary.py tests/test_search_completeness.py tests/test_search_v2_guard.py registry/search_vocabulary_seal.json
```
