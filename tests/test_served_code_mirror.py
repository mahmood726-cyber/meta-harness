"""Every certificate-pinned module must be SERVED at docs/<path> with the pinned blob.

`scripts/release_archive.py` refuses a release whose served tree does not carry the exact bytes
each CERTIFICATE pins. Until now nothing kept `docs/` in step with `harness/`, so the refusal
surfaced hours into a gate run, naming one file at a time. This states the property directly and
cheaply, and the plant proves the check can fail -- a mirror check that can only pass is not a
check.

The plant edits one served file and restores it in a `finally`. If the process is killed between
the two, that file is left one byte longer; `python scripts/sync_served_code.py --write` restores
it exactly.
"""
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sync_served_code", ROOT / "scripts" / "sync_served_code.py")
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)


def test_every_pinned_module_is_served_with_the_pinned_blob():
    pins = sync.pinned_paths()
    assert len(pins) > 50, "the pin set should be the import closure, not a handful of files"
    unserved = []
    for path, blobs in sorted(pins.items()):
        assert len(blobs) == 1, f"certificates disagree on {path}: {sorted(blobs)}"
        want = next(iter(blobs))
        got = sync.blob_of("docs/" + path)
        if got != want:
            unserved.append((path, got or "MISSING", want))
    assert not unserved, f"pinned modules not served: {unserved}"


def test_PLANT_a_served_file_that_differs_from_its_pin_is_caught():
    victim = ROOT / "docs" / "harness" / "p5_admission.py"
    original = victim.read_bytes()
    try:
        victim.write_bytes(original + b"\n# planted drift\n")
        assert sync.main(False) == 1, "the mirror check passed while a served file differed"
    finally:
        victim.write_bytes(original)
    assert sync.main(False) == 0, "the tree was not restored by this test"
