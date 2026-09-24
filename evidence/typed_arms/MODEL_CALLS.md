# Model calls made by evid2 -- disclosed, because the repo's ratchet cannot see them

`evidence/typed_arms/scripts/run_codex.sh` calls `codex exec` directly. It does **not** go through
`reproducible_ai.model_call_live` (the repository's recorded contract), and `tests/test_model_inventory.py` does not
list it -- not because it is exempt, but because that sweep parses tracked `*.py` files only and a shell caller is
invisible to it. This file is the disclosure; the sweep gap is flagged to its owner as a separate task.

Why the contract was not used (engineering decision, delegated to evid2, recorded): the owner's brief for this lane
requires every codex job to run in its own worktree on **workspace-write** with a LANE_CONTEXT.md, reading held
documents as files in that tree. The contract runs **read-only** with the documents inside the prompt. Both were
honoured where they do not conflict: every job dir carries LANE_CONTEXT.md ("nothing outside this tree is context"),
`project_doc_max_bytes=0` is set, the model is pinned (`gpt-6-astra`, reasoning medium), stdin is `/dev/null`.

What is recorded instead, per call (`CALL_LOG.first_pass.jsonl`, and `CALL_LOG.blind.jsonl` for the blind pass):
the exact prompt and its sha256, the model, every command the client ran, every file it named, any path outside its
job dir (none so far), token usage, and whether the artefact exists. Raw event streams are kept off-repo (they echo
document text and local paths); they are not needed to re-check anything, because:

What a model output can change: **nothing served**. An `out.json` is a proposal. It becomes a typed record only
through `scripts/check_typed_arms.py`, which re-finds every quoted span in sha256-pinned held bytes and decides arm
identity, direction and ownership itself (G1-G7). `tests/test_typed_arms_reproduce.py` re-derives every record from the
committed artefacts and the held repo bytes.

What the client may inject that is not ours: the user-level `~/.codex/AGENTS.md`. The predecessor lane's committed
transcripts leaked that content; this lane never commits a transcript.
