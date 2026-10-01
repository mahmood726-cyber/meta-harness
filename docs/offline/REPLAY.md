# Offline replay contract

Use the complete downloaded repository snapshot, including cache, protocols, topics,
held documents, scripts, harness, docs and the wheelhouse. A Pages-only download is not
the complete replay package. Keep an untouched copy for comparison. Do not check out
EXECUTION_RECORD.json's generating commit: DIRTY means its uncommitted inputs are not
restored by that commit. Replay checks the supplied source and input bytes against the
certificate. Missing or changed inputs refuse, rather than being downloaded.

The shipped target is **CPython 3.13 on Windows x86-64**. Python itself must already
be available; NumPy and SciPy are required, not stdlib-only. Exact versions and wheel
SHA-256 hashes (including pytest and its dependencies for the tests) are in
`requirements.lock`; all those wheels are in `wheels/`. Installation uses only these
local wheels. Other Python/platform combinations are not claimed byte-exact.
The executed corpus results and actual imported distribution versions are recorded
in [REPLAY_RESULT.json](REPLAY_RESULT.json), together with the runner and lock digests.

From the repository root, run the setup in any topic's generated REPLAY.md, then:

```text
scratch/replay-venv/Scripts/python scripts/replay_offline.py --report scratch/corpus-replay.json
scratch/replay-venv/Scripts/python scripts/generate_replay.py --check
scratch/replay-venv/Scripts/python -m pytest tests/test_bundle.py tests/test_bundle_verifier.py tests/test_exclusion_relation.py tests/test_execution_record.py tests/test_offline_replay.py -q --basetemp=scratch/pytest-replay
```

The replay denies Python socket networking, recomputes the review core and certificate,
and re-renders the page without overwriting the served artefacts. Runtime imports are
reported with distribution versions. This is numerical regeneration, not a check that
the producer once wrote matching hashes. It does not re-run people or models.
It reuses the recorded registration presentation metadata from review.json (bound by
the regenerated page/certificate), so no Git history or Git executable is required.
It does not independently re-establish prospective registration. Child processes are
also denied, so a missing cache cannot trigger an external acquisition tool.
The legacy regulatory-source `git show HEAD:<document>` lookup is adapted to read
only the current topic's certificate-pinned held-document bytes. Unlisted paths,
path escapes, missing bytes or wrong digests refuse. This reproduces the supplied
snapshot; it does not independently prove its historical Git custody.

## Identity and per-output claims

Each topic guide names its own review, page, release, protocol, lock and held-document
digests. CERTIFICATE.json.analysis_code_blobs records the code closure and declared
absences. The certificate is computed before the execution record; the record is bound
by BUNDLE.json.review_files and its release_sha256 must match the certificate. Records
describe command, interpreter, host, distributions, input/output digests and dirty paths.
An optional production-records attestation establishes served=committed at its recorded
time. Remote branch identity or a current CDN observation is optional external evidence;
neither is needed for offline reproduction, and replay alone proves neither.

| Output | Claim and failure interpretation |
|---|---|
| review.json core | EXACT canonical review_sha256; any difference fails |
| CERTIFICATE.json | EXACT recomputed release_sha256 over all other fields; altered code/input fails |
| index.html | EXACT rendered UTF-8 page digest and manifest agreement; any difference fails |
| primary estimates and intervals | EXACT on the locked certified path; not permission to change method or input |
| independent verifier pool | Its documented numerical tolerance is 1e-9, not byte exactness |
| third-party implementation | Historical HR comparison: absolute delta log(HR) <= 1e-6 and delta tau-squared <= 1e-8; only for the same PM estimator, HKSJ t(k-1) interval and max(1,Q/(k-1)) floor. Summation, root-search and quantile rounding motivate this tolerance; it is not a corpus-wide tolerance for other scales |
| per-row admission | EXACT recomputation of the predicates supported by verify_bundle.py; disagreement prints ROW_VERDICT_DISAGREES |
| BUNDLE.json rebuild | Not a byte-exact output of corpus replay. Rebuilding can change source.content_commit, source.generating_commit, build_utc, execution-record digests and dependent metadata. No blanket two-field exemption is claimed |
| retained EFetch XML anchors | EXACT retained-byte digests; optional live anchors are new observations, never part of replay |

For the independent, stdlib-only verifier, substitute the topic slug:

```text
python scripts/verify_bundle.py --root docs --slug <slug> --json
python scripts/verify_bundle.py --root docs --slug <slug> --corrupt <pooled-source-pmid> effect --json
```

Choose the control PMID from that topic's BUNDLE.json.verification_rows source object;
expect refusal after corruption. Read every `NOT checked:` line. The verifier checks
the evidence bundle, not the production admission gate. Producer `verified` labels are
assertions, not proof of source identity, interval, effect measure or admission.

Full producer rebuilds remain available via `build_topic.py <slug> --now <build_utc>`
then `build_bundle.py <slug>`, but mutate metadata and are not the read-only procedure.
The manifest source block is restamped by the bundle builder; registry/blind_map.json
is a last-topic-built side file. Adding even an unimported harness/*.py changes the
certificate's declared scope. Replay helpers therefore live in scripts/.

## Limits and historical specification

Fresh searches are not replay: these pages use held known-item caches and do not establish
search completeness. Recorded human/AI judgments are hashed inputs, not independently
re-derived judgments. Eligible-but-unpooled evidence, incomplete RoB/GRADE and unbound
harms remain disclosed limits, not completed work. Cached documents and saved acquisitions
prove saved bytes, not publisher authenticity or faithful preservation. Read each topic's
BUNDLE.json.limits and custody/licence states; a digest does not supply a missing document.

The original GLP-1 specification, including its historical measurements, frozen commits,
wrapper history, source-preservation defects and producer-label caveats, is retained
verbatim in [REPLAY-history.md](REPLAY-history.md). **That is historical evidence, not
current replay instructions.** Its stdlib-only heading, remote clone/check steps,
dirty-commit checkout advice and two-field bundle exemption are superseded here.

Report digest failures with the named file and numerical differences with the applicable
tolerance. A dirty source snapshot is not reconstructed from its commit name; successful
byte verification identifies the supplied snapshot, not a historical clean release.

| Static policy | Dynamic evidence |
|---|---|
| Target platform, exactness rules, network denial | Executed corpus replay and observed imports |
| No inferred scientific values | Topic digests, held documents and provenance read from objects |
| Pinned wheel versions/hashes | Wheel bytes verified locally and installed with --require-hashes |
