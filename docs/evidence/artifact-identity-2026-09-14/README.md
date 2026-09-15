# Artifact identity — build once, verify that artifact, deploy exactly it, fetch it back (2026-09-14)

**Fix state (orthogonal fields rule): LANDED / INTERNAL / INSTANCE / STALE** - generated from TRANCHE-artifact-identity; verified by Codex lane G (internal_agent); evidence: docs/evidence/independent-verification-2026-09-14/04-artifact-identity.txt; stale dependencies: .github/workflows/verify.yml, harness/architecture_identity.py, scripts/production_record.py

| file | what it is |
|---|---|
| `01-prefix-deploy-re-tars-unverified-artifact.txt` | run 34863913498: `deploy` ran its own checkout and created artifact 10356385911; `verify` produced no artifact — the deployed bytes were never the verified bytes |
| `02-second-path-search.txt` | every deploy/bypass surface with the API read-back: Pages source, workflows (incl. GitHub's dynamic legacy one), dispatch refusal (422), environment policy, legacy builds, deployments, ruleset, collaborators, token permissions |
| `03-latent-paths-closed.txt` | the `gh-pages` environment policy deleted (main only); the dynamic legacy workflow CANNOT be disabled by API — inert while `build_type=workflow`, admin-only bypass |
| `04-postfix-first-chained-deploy.txt` | run 34866009285: verify uploaded manifest + pages artifact 10357390680; deploy (no checkout) checked 238/238 files against the manifest, deployed, fetched 238/238 back equal; record published to branch `production-records`; independent re-fetch from another machine equal |

Verify cold: `https://raw.githubusercontent.com/mahmood726-cyber/meta-harness/production-records/<commit sha>.json` holds
the chain for every deployment since d71959a2; fetch any `files[path].url`, sha256 the body, compare with `verified_sha256`.
The served site also carries its own manifest at `/_production/manifest.json`.
