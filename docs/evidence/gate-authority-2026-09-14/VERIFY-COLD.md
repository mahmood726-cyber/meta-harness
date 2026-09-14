# Verify this finding yourself, without us — no credentials needed

The finding: **on 2026-09-13, commit `109053ad` failed its CI verification (`verify` workflow, step "Unit
tests") and GitHub Pages deployed that same commit anyway.** Until 2026-09-14 the site was published by
GitHub's automatic legacy Pages build, which runs on every push regardless of checks; nothing stood between a
failing commit and readers. Everything below is a public API read on a public repository
(`mahmood726-cyber/meta-harness`); the expected values are what the API returned when this file was written
(2026-09-14T16:00Z). If a value differs, the finding has changed and this file is out of date.

## The commit
```
curl -s https://api.github.com/repos/mahmood726-cyber/meta-harness/commits/109053ad175eafcb77c0c23020f8e367008591c4
```
Expect: `"sha": "109053ad175eafcb77c0c23020f8e367008591c4"`, author date `2026-09-13T18:43:42Z`, subject beginning
`extract: match mortality<->death synonym`.

## 1. The verification FAILED on that commit
```
curl -s https://api.github.com/repos/mahmood726-cyber/meta-harness/actions/runs/34775559625
```
Expect: `"name": "verify"`, `"head_sha": "109053ad…"`, `"conclusion": "failure"`, `"created_at": "2026-09-13T18:44:29Z"`.
Which step:
```
curl -s https://api.github.com/repos/mahmood726-cyber/meta-harness/actions/runs/34775559625/jobs
```
Expect: job `verify` → `"conclusion": "failure"`, and in `steps[]` the step named `Unit tests` has `"conclusion": "failure"`.
Web view: https://github.com/mahmood726-cyber/meta-harness/actions/runs/34775559625

## 2. Pages deployed that same commit, one second earlier — and succeeded
```
curl -s https://api.github.com/repos/mahmood726-cyber/meta-harness/actions/runs/34775558931
```
Expect: `"name": "pages build and deployment"`, `"head_sha": "109053ad…"`, `"conclusion": "success"`,
`"created_at": "2026-09-13T18:44:28Z"`. (This is GitHub's own legacy Pages workflow, path `dynamic/pages/pages-build-deployment`.)
Web view: https://github.com/mahmood726-cyber/meta-harness/actions/runs/34775558931

The deployment object and its status:
```
curl -s "https://api.github.com/repos/mahmood726-cyber/meta-harness/deployments?sha=109053ad175eafcb77c0c23020f8e367008591c4&environment=github-pages"
curl -s https://api.github.com/repos/mahmood726-cyber/meta-harness/deployments/6425095939/statuses
```
Expect: deployment `6425095939`, `"environment": "github-pages"`, created `2026-09-13T18:44:57Z`; its statuses end in
`"state": "success"` at `2026-09-13T18:45:09Z` with `"environment_url": "https://mahmood726-cyber.github.io/meta-harness/"`.

So: verify failed at 18:44:29Z; the site was rebuilt from the same SHA and went live at 18:45:09Z.

## 3. What stood between a failing commit and readers at the time
```
curl -s https://api.github.com/repos/mahmood726-cyber/meta-harness/rulesets
```
At the time: `[]` (no rulesets), and branch protection returned 404 "Branch not protected" (captured in
`01-prefix-deploy-unconditional.txt`). Pages source was the legacy branch build (`"build_type": "legacy"`,
`"source": {"branch": "main", "path": "/docs"}`), also in `01-*`.

## 4. What stands there now (read back the same way)
```
curl -s https://api.github.com/repos/mahmood726-cyber/meta-harness/pages          # expect "build_type": "workflow"
curl -s https://api.github.com/repos/mahmood726-cyber/meta-harness/rulesets       # expect id 23314494, "enforcement": "active"
curl -s https://api.github.com/repos/mahmood726-cyber/meta-harness/rulesets/23314494   # required_status_checks context "verify", bypass_actors []
```
The refusals were demonstrated with planted failing commits after the change; each capture in this directory names
the run ids and SHAs, and every one of them is readable at the same API paths with the id substituted.

## Fix state, as of this file
Per the four-state rule (REPORTED / LANDED / VERIFIED / GENERALIZED): the gate-authority fix is **LANDED** and
**demonstrated by its author** on planted commits in separate runs (`03`, `06`, `07`, `11`). It is **not VERIFIED**
in the sense the auditor uses — no party independent of the author has re-run these checks — and it is **not
GENERALIZED** — it has refused nothing that it was not written against. This file exists so that the VERIFIED step
can be taken by someone else.
