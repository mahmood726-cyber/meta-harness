# Frozen release archive: glp1-ra-mace-t2d at 1b3b0b8dcf3d

This archive freezes the bytes served for the `glp1-ra-mace-t2d` review at commit `1b3b0b8dcf3df8cf305686e2953ef0d58db5051d` (tree `02b3d5c716a295b1177fe7162e4fd87ba7b7f4f0`). Release status: **PRE-RELEASE**. the review is served under a PRE-RELEASE label (registry/release_status.json); this archive freezes what was served at the commit above and is NOT a version-1 release.

- `release_sha256` 6a04a3dfed6661f3215ba55a694cae89da91c181a45a883e3d3320b6f059277f
- `review_sha256` 7d15dfd97fc744d1c44e8ad50f0f6612c4e9c9a6f6b4de131bca34f450da7d92
- `html_sha256` 5d16b04a7afa53d75bd6bcddae420dcc7c20ff748be7a0f90d98c7ed6c833ce7
- 126 served files under `site/`, each listed in `RELEASE.json` with its sha256, its Git blob id at the commit, its served URL and why it is included. Definition: every path the review's BUNDLE.json advertises as served, every module its CERTIFICATE.json pins, the served review directory, and the verifiers the page names -- all read from the commit above.
- production record: production record 1b3b0b8dcf3d: ATTESTED (1188/1188 served files equal) (copied verbatim as `production_record.json`)

## Get it

- Download: `https://mahmood726-cyber.github.io/meta-harness/releases/glp1-ra-mace-t2d/1b3b0b8dcf3d/glp1-ra-mace-t2d-1b3b0b8dcf3d.zip`; its sha256 is in `https://mahmood726-cyber.github.io/meta-harness/releases/glp1-ra-mace-t2d/1b3b0b8dcf3d/SHA256SUMS` and in the repository at `docs/releases/glp1-ra-mace-t2d/1b3b0b8dcf3d/SHA256SUMS`. Take the digest from a second channel (a clone, a colleague, the page) if you can.
- Check the download: `sha256sum glp1-ra-mace-t2d-1b3b0b8dcf3d.zip` (Windows: `certutil -hashfile glp1-ra-mace-t2d-1b3b0b8dcf3d.zip SHA256`).
- Unpack: `python -m zipfile -e glp1-ra-mace-t2d-1b3b0b8dcf3d.zip .` then `cd glp1-ra-mace-t2d-1b3b0b8dcf3d`.

## Replay: what runs from this archive alone (no network, Python 3.9+ standard library, no git)

```
python check_sha256sums.py          # or: sha256sum -c SHA256SUMS -- every file in this archive
python site/scripts/verify_bundle.py --root site --slug glp1-ra-mace-t2d
python site/scripts/audit_certificate_stdlib.py site/reviews/glp1-ra-mace-t2d/CERTIFICATE.json site
python plant_control.py             # the control: damages a copy of site/ and must see the verifier NOT pass
```

The first must print every file matching. The second must print `verdict PASS`; the third `RESULT REPRODUCED`; the control must print `CONTROL FIRED` (a verifier that cannot fail proves nothing). Each verifier prints `NOT checked:` -- those limits apply to you. Compare the `release_sha256` the auditor prints with the one above and with the one printed on `site/reviews/glp1-ra-mace-t2d/index.html`.

Two traps, both measured in a fresh directory with the network blocked when this archive was made:

- `verify_bundle.py --corrupt <pmid> <limb>` is **not** a must-fail control. It mutates one row in memory and reports which rows stop being ADMISSIBLE (read its `corruption` line); its verdict stays `PASS` and it exits 0. (`site/reviews/glp1-ra-mace-t2d/REPLAY.md` calls it "a control: must refuse"; measured, it does not.)
- `verify_bundle.py --anchor live` with no network printed `verdict PASS` with **0 of 11** live fetches made. The verdict does not say whether the live observation happened: read each `anchor` line's `live: fetched=` field. `fetched=False` everywhere means no external observation was made, whatever the verdict says.

## Replay: what needs a clone

Regenerating the page from its inputs (the review core, certificate and page bytes) needs the repository at the commit, because the build reads the committed cache, protocol and topic configuration, which are not all served. A checkout is ~1.9 GB of files (plus history; a full clone of every blob is far larger). **This lane did not run the steps below for this archive** (the machine that built it had under 2 GB free); they are the commands the execution record names, and `REPLAY.md` records the last measured replay and its tolerances:

```
git clone --filter=blob:none https://github.com/mahmood726-cyber/meta-harness.git && cd meta-harness
git checkout 1b3b0b8dcf3df8cf305686e2953ef0d58db5051d
git status --porcelain                       # must print nothing
python scripts/build_topic.py glp1-ra-mace-t2d --now 2026-09-11
python scripts/build_bundle.py glp1-ra-mace-t2d
git diff --stat -- docs/reviews/glp1-ra-mace-t2d/     # expect only the execution record and the bundle's build fields
```

`docs/reviews/glp1-ra-mace-t2d/REPLAY.md` (in this archive at `site/reviews/glp1-ra-mace-t2d/REPLAY.md`) states per output what reproduces exactly and what within a declared tolerance.

## What an outsider can and cannot do, by network

| machine | can | cannot |
|---|---|---|
| full network | download the archive or clone; everything below; `verify_bundle.py --url https://mahmood726-cyber.github.io/meta-harness/ --slug glp1-ra-mace-t2d` against the live site; `--anchor live` (re-fetch PubMed now) | -- |
| github.com and github.io reachable, `raw.githubusercontent.com` blocked | download the archive from the Pages URL; clone over git (github.com); every offline check; `--url` against the live site (it fetches from github.io, not raw) | anything that fetches from raw.githubusercontent.com; `--anchor live` if NCBI is also blocked |
| no DNS / no network | the offline checks above, on an archive carried in by hand, after checking its sha256 against a digest obtained out of band | download, clone, `--url`, `--anchor live`; establishing that the live site still serves these bytes; regenerating the page (needs the clone) |

## What a PASS here does not establish

- that the live site serves these bytes today (only the production record, or a fetch, says what was served);
- anything the verifiers print under `NOT checked:` -- upstream fidelity of any held representation, completeness of the source set, clinical interpretation, and more;
- that the review is a version-1 release: it is served PRE-RELEASE.
