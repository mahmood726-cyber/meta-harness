# Port onto the current exchange package

The handoff stack uses the existing `harness/exchange_v01/` package. Current
callers import the raw boundary from `wire.py`. The public package importer is
a compatibility delegate. `__main__.py` and the legacy importable `main()`
continue to call that same CLI/parser. Existing strict Unicode, duplicate-key,
nonstandard-constant, provenance and validator checks remain in force.

Historical source paths in the frozen runners are intentional. In particular,
016 executes Meta-Harness commit `ea2fac35a212a330dfe27f7b710347e9ef69a12a`, whose
importer is `harness/exchange_v01.py`. Its `PRODUCER_CODE_PATHS` and archived
Git-blob receipt keys must retain that path. The port does not create that file
in the current tree or replace the immutable producer with current code.
017 and 018 retain their distinct historical producer pin. Repository pins and
all three frozen JSON registrations are copied without modification.

Main's manifest has the same closed row format and contiguous case-ID rule as
the source stack. Only its new common row, CROSS-EXCH-015, is appended, with the
original synthetic source and `NOT_RUN` status. The validator and schema floors
increase from 14 to 15. Frozen 016–018 are separate specifications with different
pins and execution roles; they are not new rows in this historical manifest.

No certificate, served review, signature, acknowledgement or production module
is changed. The existing all-releases scope regression is retained, and the
stack's importer-specific closure regression is added alongside it.

## Tests and execution boundaries

The imported tests remain synthetic fixtures. The comparator tests construct
two labelled fixture archives; that does not mean two operating systems ran.
The replay tests use fabricated consumer modules to inject refusal and process
launch failures; they do not replace frozen-checkout execution evidence.

These tests actually invoke Git and must run in Linux CI or a permitted Git
environment. They are retained without replacing Git or filesystem checks:

- All five methods in `PinnedEngineCustodyTests` in
  `tests/test_pinned_engine_custody.py`.
- `RunnerIdentityTests.test_frozen_git_blob_gate_refuses_modified_producer_and_importer`
  in `tests/test_frozen_runner_os_016.py`.
- `ArchivedArtifactParityTests.test_engine_hash_is_tied_to_commit_and_clean_worktree`
  and `test_identical_git_blob_through_external_engine_symlink_refused` in
  `tests/test_compare_cross_os_016.py`.
- The existing `test_pinned_blob_identities_are_what_git_stores` in
  `tests/test_certificate_code_closure.py`.

Actual 016 matrix runs, 017/018 frozen handoffs, engine pooling and downloaded
artifact comparison/replay additionally require the pinned repositories and
runtimes. Their workflows are supplemental gates; they do not replace existing
repository verification. No network, Git invocation, real engine execution or
second-OS attestation is part of the local port.

The restricted Windows environment used for the port also denies access to
directories created with Python's private temporary-directory permissions.
Tests using `tmp_path` or `tempfile.TemporaryDirectory` must be checked in CI;
their filesystem operations and assertions are preserved. The task report
records the runnable local subset and the exact fail-then-pass evidence.

The imported reproduction documents include historical upstream observations.
Those workflow results have not been fetched or independently reverified during
this port. All registration statuses and external-coverage limitations remain
unchanged.
