"""Plant: a model-call record is redacted of private text BEFORE it is built or written (reproducible_ai/model_source.
redact_private). Codex reads the owner's global instructions (CODEX_HOME holds his login and is not moved), and replies
and transcripts echoed drive-qualified private paths and instruction lines into committed records (5 Oct 2026: 16
records had to be removed from branch history). The pre-commit leak scan stays as the second layer."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from reproducible_ai import model_source as ms  # noqa: E402

OWNER = ["Never quote a private workbook path back to anyone at all, ever."]
PRIVATE = "F:" + "\\" + "Private" + "\\" + "workbook.txt"          # assembled so this file is not itself a leak


def _rec(response=b'{"ok": true}', error=None, state="RAN_OK", evidence=None):
    return ms.build_record(
        prompt_bytes=b"PROMPT", response_bytes=response,
        model={"id_requested": "m", "id_reported": "m", "provider": "p"}, params={}, not_controllable=[],
        client={"name": "codex exec"}, request_utc="2026-10-05T00:00:00Z", response_utc="2026-10-05T00:00:01Z",
        caller={"file": "f", "line": "1", "purpose": "plant"}, input_digests=[{"ref": "r", "sha256": "0" * 64}],
        state=state, error=error, client_evidence=evidence, owner_lines=OWNER)


def test_a_clean_record_is_untouched_and_carries_no_redaction_field():
    r = _rec()
    assert "redaction" not in r and ms.replay(r) == b'{"ok": true}'


def test_a_drive_qualified_path_in_the_response_keeps_only_its_file_name():
    raw = ('{"note": "I read ' + PRIVATE.replace("\\", "\\\\") + ' first"}').encode()
    r = _rec(response=raw)
    out = ms.replay(r).decode()
    assert "Private" not in out and "<outside-workdir>/workbook.txt" in out
    red = r["redaction"]["fields"]["response"]
    assert red["replacements"] == 1 and red["pre_redaction_sha256"] == ms.sha256_bytes(raw)
    assert ms.record_problems(r) == []                                   # still a sound, replayable record


def test_owner_instruction_lines_are_withheld_everywhere():
    r = _rec(response=("echo: " + OWNER[0]).encode(), evidence={"transcript": "saw " + OWNER[0] + " and " + PRIVATE})
    s = json.dumps(r)
    assert OWNER[0] not in ms.replay(r).decode() and OWNER[0] not in s and "Private" not in s
    assert "<owner-instructions withheld" in ms.replay(r).decode()
    assert set(r["redaction"]["fields"]) == {"response", "client_evidence"}


def test_an_error_text_is_redacted_and_the_work_dir_is_kept():
    work = "C:/tmp/mcall-abc123/schema.json"
    r = _rec(response=b"", state="RAN_ERROR", error="failed reading " + PRIVATE + " in " + work)
    assert "Private" not in r["error"] and work in r["error"]


def test_the_written_bytes_hold_no_private_text(tmp_path):
    p = ms.write_record(_rec(response=PRIVATE.encode()), tmp_path)
    assert b"Private" not in p.read_bytes()
