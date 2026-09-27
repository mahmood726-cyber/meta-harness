# Frozen release archive: meta-harness V1 at 9eacfe09d411

This archive freezes the bytes the whole site served at commit `9eacfe09d41136a615e9fb3331b5b7b3968d124d` (tree `73e1fa8653d5006c56d4b08df6cee35de2df0f6c`): 32 review pages, 314 archived files, and a hash list of all 1250 served files.
- production record: production record 9eacfe09d411: ATTESTED (1251/1251 served files equal)
- acceptance record: INCLUDED (`ACCEPTANCE.json`: the page-verifier lane's hostile audit of THESE served bytes against release checklist 18)

## Get it
- Download `https://mahmood726-cyber.github.io/meta-harness/releases/v1/9eacfe09d411/meta-harness-v1-9eacfe09d411.zip`; its sha256 is in `https://mahmood726-cyber.github.io/meta-harness/releases/v1/9eacfe09d411/SHA256SUMS` and in the repository at `docs/releases/v1/9eacfe09d411/SHA256SUMS`. Take the digest from a second channel if you can.
- `sha256sum meta-harness-v1-9eacfe09d411.zip` (Windows: `certutil -hashfile meta-harness-v1-9eacfe09d411.zip SHA256`), then `python -m zipfile -e meta-harness-v1-9eacfe09d411.zip .` and `cd meta-harness-v1-9eacfe09d411`.

## Replay from this archive alone (no network, Python 3.9+ standard library, no git)
```
python check_sha256sums.py      # every file in this archive matches SHA256SUMS
python audit_all_pages.py       # the archived certificate auditor on every page: must print N of N
python site/scripts/verify_bundle.py --root site --slug glp1-ra-mace-t2d
python plant_control.py         # damages a copy of site/ and must see the verifier NOT pass
```
- `SITE_SHA256SUMS` (`sha256  git-blob  served-path`) covers EVERY served file at the commit, including those not archived: fetch any of them from the site and compare, or run `git rev-parse <commit>:docs/<path>` in any clone.
- `verify_bundle.py --corrupt` is NOT a must-fail control: its verdict stays PASS and it reports the rows that stop being ADMISSIBLE. `--anchor live` without network prints PASS with no live fetch made; read each anchor's `fetched=`.

## What needs a clone, and what the network allows
- Regenerating a page from its inputs needs the repository at the commit (~1.9 GB checkout): `git clone --filter=blob:none https://github.com/mahmood726-cyber/meta-harness.git`, `git checkout 9eacfe09d41136a615e9fb3331b5b7b3968d124d`, then `python scripts/build_topic.py <slug> --now 2026-09-11` (each page's execution record names its command).
- Full network: everything, plus `verify_bundle.py --url https://mahmood726-cyber.github.io/meta-harness/ --slug <slug>` against the live site and `--anchor live`.
- github.com / github.io reachable, raw.githubusercontent.com blocked: download this archive from the Pages URL, clone over git, every offline check, `--url` (it reads github.io, not raw). Not: anything fetched from raw.
- No DNS / no network: only the offline checks above, on an archive carried in by hand whose sha256 you obtained out of band. Not: download, clone, `--url`, `--anchor live`, or establishing what the live site serves today.

## What a PASS here does not establish
- that the live site serves these bytes today (only a fetch, or the production record, says what was served);
- anything a verifier prints under `NOT checked:`; the scientific validity of any pooled estimate;
- anything listed in the release note's 'what this release does not prove' section.
