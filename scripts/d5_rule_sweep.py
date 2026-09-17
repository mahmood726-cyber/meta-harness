from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_REF = "ad5e7c66"


def _git_json(path: str) -> dict:
    raw = subprocess.check_output(
        ["git", "show", f"{BASE_REF}:{path}"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )
    return json.loads(raw)


def _current_json(path: str) -> dict:
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def _primary_trials(review: dict) -> list[dict]:
    primary = next((o for o in review.get("outcomes", []) if o.get("primary")), None)
    return (primary or {}).get("trials", []) or []


def _trial_id(trial: dict) -> str:
    return str(trial.get("id", "")).replace("PMID ", "")


def _pool_summary(point: dict | None) -> dict | None:
    if not point:
        return None
    return {k: point.get(k) for k in ("k", "scale", "estimate", "ci_low", "ci_high", "ci_refused")}


def _d5(review: dict, pid: str) -> dict:
    return (((review.get("rob2") or {}).get("trials") or {}).get(pid, {}).get("domains") or {}).get(
        "D5_selective_reporting",
        {},
    )


def _normal_level(level: str | None) -> str | None:
    if level in {"not assessed", "not_assessable", "not assessable"}:
        return "not_assessable"
    return level


def main(argv: list[str]) -> int:
    write = "--write" in argv
    slugs = [
        name for name in sorted(os.listdir(os.path.join(ROOT, "docs", "reviews")))
        if os.path.exists(os.path.join(ROOT, "docs", "reviews", name, "review.json"))
    ]
    low_only_pages = []
    changed_trials = []
    before_after_pages = []
    total_pooled = 0
    pages_decided_by_overturned_d5 = []

    for slug in slugs:
        before = _git_json(f"docs/reviews/{slug}/review.json")
        after = _current_json(os.path.join("docs", "reviews", slug, "review.json"))
        before_sens = before.get("rob_sensitivity") or {}
        after_sens = after.get("rob_sensitivity") or {}
        has_low_only_stratum = before_sens.get("low_only") is not None or after_sens.get("low_only") is not None
        if has_low_only_stratum:
            low_only_pages.append(slug)
        page_changed_d5 = []
        for trial in _primary_trials(before):
            pid = _trial_id(trial)
            if not pid:
                continue
            total_pooled += 1
            before_d5 = _d5(before, pid)
            after_d5 = _d5(after, pid)
            if _normal_level(before_d5.get("level")) != _normal_level(after_d5.get("level")):
                changed_trials.append({
                    "slug": slug,
                    "trial": pid,
                    "before": before_d5.get("level"),
                    "after": after_d5.get("level"),
                    "before_basis": before_d5.get("basis"),
                    "after_basis": after_d5.get("basis"),
                })
                page_changed_d5.append(pid)
        if has_low_only_stratum:
            before_after_pages.append({
                "slug": slug,
                "changed_d5_trials": page_changed_d5,
                "before_low_only": _pool_summary(before_sens.get("low_only")),
                "after_low_only": _pool_summary(after_sens.get("low_only")),
                "before_low_only_kind": before_sens.get("low_only_kind"),
                "after_low_only_kind": after_sens.get("low_only_kind"),
            })
        if (
            has_low_only_stratum
            and page_changed_d5
            and _pool_summary(before_sens.get("low_only")) != _pool_summary(after_sens.get("low_only"))
        ):
            pages_decided_by_overturned_d5.append(slug)

    out = {
        "base_ref": BASE_REF,
        "pages_with_low_only_stratum": low_only_pages,
        "n_pages_low_only_stratum_decided_by_overturned_d5": len(pages_decided_by_overturned_d5),
        "N_pages_with_low_only_stratum": len(low_only_pages),
        "pages_low_only_stratum_decided_by_overturned_d5": pages_decided_by_overturned_d5,
        "n_trials_d5_changed": len(changed_trials),
        "N_pooled_trials": total_pooled,
        "trials_d5_changed": changed_trials,
        "before_after_low_only_pools": before_after_pages,
    }
    if write:
        path = os.path.join(ROOT, "docs", "d5_rule_sweep.json")
        with open(path, "w", encoding="utf-8", newline="") as handle:
            json.dump(out, handle, indent=2, ensure_ascii=False)
        print(path)
    print(
        f"{len(pages_decided_by_overturned_d5)} pages whose low-risk stratum was decided by an overturned "
        f"D5 signal of {len(low_only_pages)} pages with a low-only stratum"
    )
    print(f"{len(changed_trials)} trials D5 changed of {total_pooled} pooled trials")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
