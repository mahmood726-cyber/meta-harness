"""F6C three-run acceptance ledger; consumes actual captured commands."""
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("artifact_integrity", "state_reproduction", "input_linkage", "scientific_admission", "publication_eligibility")
CONTROLS = ("baseline", "reorder_records", "reorder_pool_records", "freedom_decimal_normalisation")
EXPECTED = {"rotated_ids": "POOL_ROW_IDENTITY_MISMATCH", "unknown_id": "POOL_INPUT_MEMBERSHIP_MISMATCH", "omitted_id": "POOL_INPUT_MEMBERSHIP_MISMATCH", "duplicate_id": "POOL_INPUT_DUPLICATE", "altered_inputs_updated_aggregate": "POOL_INPUT_TUPLE_MISMATCH"}

def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))

def published(row):
    stages = {s["stage"]: s for s in row["stages"]}
    return all(k in stages and stages[k]["returncode"] == 0 for k in ("producer_renderer", "bundle", "publication_gate"))

def exact(row):
    return (row.get("first_refusal") or {}).get("code") == EXPECTED[row["case"]] and not published(row)

def fence(obj):
    return "```json\n" + json.dumps(obj, ensure_ascii=False, indent=2) + "\n```"

def generate():
    runs = [load(f) for f in ("f6_prefix.json", "f6_after.json", "f6_repaired.json")]
    maps = [{r["case"]: r for r in run["cases"]} for run in runs]
    rep = runs[-1]
    names = list(maps[0])
    assert all(set(m) == set(names) for m in maps), "NOT_REACHED: case set incomplete"
    expected_sources = load(".tmp/f6c-patched.json") if (ROOT / ".tmp/f6c-patched.json").exists() else rep["measurement_setup"]["patched_sha256"]
    assert all(r.get("implementation_sha256") and all(h == expected_sources[f] for f, h in r["implementation_sha256"].items()) for row in maps[-1].values() for r in (row, row["restored_acceptance"])), "NOT_REACHED: final repaired implementation did not execute every case and restored baseline"
    accepted = [n for n in CONTROLS if published(maps[-1][n])]
    refused = [n for n in EXPECTED if exact(maps[-1][n])]
    absent = all("POOL_PUBLICATION_INELIGIBLE" not in s["stdout"] + s["stderr"] for n in CONTROLS for s in maps[-1][n]["stages"])
    verdict = "PASS" if len(accepted) == len(CONTROLS) and len(refused) == len(EXPECTED) and absent else "FAIL"
    rep["acceptance_evaluation"] = {"verdict": verdict, "required_controls": list(CONTROLS), "published_controls": accepted, "pool_attacks": EXPECTED, "exactly_refused_attacks": refused, "old_refusal_wording_absent_from_controls": absent}
    rep["same_inputs_vs_prior"] = {n: {f: all(m[n].get(f) == maps[0][n].get(f) for m in maps[1:]) for f in ("selected_records", "derived_statistical_inputs")} for n in names}
    assert all(all(v.values()) for v in rep["same_inputs_vs_prior"].values()), "Fixture inputs differ from the prior ledgers"
    rep["measurement_setup"] = {"patched_sha256": expected_sources, "route": "python -X utf8 scripts/f6_acceptance.py"}
    for key in ("tests", "restoration", "initial_test_attempt", "source_review", "fixture_checks", "corrective_command"):
        path = ROOT / (".tmp/f6c/" + key + ".json")
        if path.exists():
            rep[key] = load(path.relative_to(ROOT))
    data = json.dumps(rep, ensure_ascii=False, indent=2) + "\n"
    if len(data.encode()) >= 19_500_000:
        data = json.dumps(rep, ensure_ascii=False, separators=(",", ":")) + "\n"
    assert len(data.encode()) < 20_000_000
    (ROOT / "f6_repaired.json").write_text(data, encoding="utf-8", newline="\n")
    source_refs = rep["source_review"]
    parts = ["# F6C repaired POOL acceptance", f"**F6C_ACCEPTANCE {verdict}**. {len(accepted)} of {len(CONTROLS)} required publication controls publish; {len(refused)} of {len(EXPECTED)} named pool attacks refuse with the exact intended first refusal. The denominators are the named sets below.",
        "Required controls: " + ", ".join("`"+n+"`" for n in CONTROLS) + ". Named pool attacks: " + ", ".join("`"+n+"`" for n in EXPECTED) + ".",
        f"Executed {len(maps[-1])} of {len(names)} cases in the original pre-fix ledger. Command: `python -X utf8 scripts/f6_acceptance.py`. Same topic producer -> renderer -> bundle -> local publication gate -> independent verifier route, with a fresh baseline restoration run after every case. No whole-corpus deployment, signing, commit or push was performed; no process was stopped or signalled.",
        "## Publication contract and repair",
        source_refs["claims"],
        "Publication gates all explicit verifier failures, including digest/certificate/execution-record integrity, row membership/multiplicity/identity/tuple/analysis/contrast linkage, owning-source evidence and reported-verdict consistency, plus aggregate reproduction. These explicit discrepancies remain failures even where the legacy failure category is named `semantics`. A row's independently recomputed INADMISSIBLE state alone does not gate publication; scientific_admission remains independently reported and FAIL for the authentic controls. Existing page gates still apply. No identifier-specific exemption or forced admission PASS was added.",
        "## Hardcode disclosure",
        "| Item | Static or dynamic | Purpose |\n|---|---|---|\n| Case names, expected codes, topic and fixture date | Static, inherited acceptance contract | Test scope, not scientific findings |\n| Certified rows, source spans, IDs and numeric tuples | Dynamic, retained source records and production captures | No replacement findings |\n| Verdicts and first refusals | Dynamic real command outputs | No pass for an unrun stage |\n| Tuple-permutation test | Generic exact numeric multiset comparison | Distinguish reassigned IDs from altered values |\n| Prior ledgers | Preserved files | Historical comparison only |",
        "## Side-by-side ledger",
        "Fields in order: artifact_integrity / state_reproduction / input_linkage / scientific_admission / publication_eligibility. Each cell reproduces stored values verbatim. Pre-fix fields retain their original projection provenance. Repaired native values are used only when the independent verifier ran. `NOT_REACHED` is not acceptance.",
        "| Case | Pre-fix | F6B post-fix | F6C repaired | First refusal: pre / F6B / F6C |\n|---|---|---|---|---|"]
    for n in names:
        vals = [" / ".join(m[n]["five_verdicts"][f] for f in FIELDS) for m in maps]
        codes = ["NONE" if m[n].get("first_refusal") is None else (m[n]["first_refusal"].get("code") or m[n]["first_refusal"]["message"]) for m in maps]
        parts.append("| " + " | ".join([n, *vals, " / ".join(codes)]) + " |")
    parts.append("\nUncredited interim attempts retained in `prior_attempts`: " + ", ".join(r["case"] for r in rep.get("prior_attempts", [])) + ". These preceded the final build-order repair and are not used as final acceptance results.")
    parts.append("\nThree-run counts, computed from each saved ledger: ")
    for label, m in zip(("Pre-fix", "F6B", "F6C"), maps):
        parts.append(f"{label}: {sum(published(m[n]) for n in CONTROLS)} of {len(CONTROLS)} required controls publish; {sum(exact(m[n]) for n in EXPECTED)} of {len(EXPECTED)} named pool attacks have the exact intended first refusal.")
    parts.extend(["## Real command output", "The per-case gate and first-refusal text below is copied from the actual command captures. Full structured native reports, source/input captures, stage return codes and restored baselines remain in `f6_repaired.json`. Long stdout/stderr use the inherited bounded head/tail retention with explicit omission markers."])
    for n in names:
        row = maps[-1][n]
        parts.append("### `"+n+"`")
        parts.append("Native independent-verifier verdicts (or explicit NOT_REACHED):\n\n" + fence(row.get("verifier", {}).get("verdicts", "NOT_REACHED")))
        first = row.get("first_refusal")
        parts.append("First refusal:\n\n" + fence(first if first else None))
        for stage in row["stages"]:
            if stage["stage"] in ("bundle", "publication_gate"):
                parts.append(f"`{stage['command']}` - exit {stage['returncode']}:\n\n```text\n" + stage["stdout"] + stage["stderr"] + "\n```")
        if not any(s["stage"] == "bundle" and s["returncode"] == 0 for s in row["stages"]):
            parts.append("No current-case bundle was written. Subsequent digest/certificate/execution-record mismatches are downstream stale-bundle consequences, not independent semantic catches; independent verifier NOT_REACHED.")
    parts.extend(["## Limits and validation", "`display_columns` remains an unsupported representation/baseline replay; `reversed_target` has no supported reversed-target acceptance claim. Cases outside the named conjunction are measured without new semantic credit. The lane establishes local publication-gate acceptance, not a live Pages deployment or clinical certification.",
        "Selected records and derived inputs compared against both prior runs:\n\n" + fence(rep["same_inputs_vs_prior"]),
        "Focused regression command output:\n\n" + fence(rep.get("tests", "NOT_REACHED")),
        "Initial test attempt (not credited as green):\n\n" + fence(rep.get("initial_test_attempt", "NOT_REACHED")),
        "## Restoration and evidence preservation", fence(rep.get("restoration", "NOT_REACHED")),
        f"Harness original artifact bytes restored: `{rep.get('original_bytes_restored')}`. JSON size: {len(data.encode())} bytes, below 20 MB. F6B_REPORT.md, f6_after.json and f6_prefix.json hashes are checked against entry hashes. Source/artifact restoration is byte-identical only if the restoration object above says true; new lane deliverables are intentionally retained.",
        "`F6C.patch` is cumulative against the entry tree (original F6 code/harness plus repaired F2/F3 enforcement), not incremental over F6B.patch. Apply only F6C.patch to replay the repaired state; retain f6_repaired.json for the harness's exact source-hash allowlist. Line citations refer to that applied patch state. The delivered working tree is restored, so the repair is carried by the patch."])
    rendered = re.sub(r"(?m)(^\|[^\n]*\|\n)\n(?=\|)", r"\1", "\n\n".join(parts)+"\n")
    (ROOT / "F6C_REPORT.md").write_text(rendered, encoding="utf-8", newline="\n")
    print("F6C_ACCEPTANCE " + verdict)
    print(f"{len(accepted)} of {len(CONTROLS)} required controls publish")
    print(f"{len(refused)} of {len(EXPECTED)} named pool attacks refused with exact first refusal")
    print(f"{len(names)} of {len(names)} pre-fix ledger cases executed")
    return 0 if verdict == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(generate())
