"""Live tab acceptance, headless (Playwright + the local Edge/Chrome, as tests/test_certificate_ui.py uses), against the SERVED
pages: for every review page at 1280x800 and 375x812, click each tab in three scenarios (from the top; from the tab bar after
scrolling to the bottom of the previous tab; while scrolled deep) and require THAT tab's own heading (h3.tabname) to be visible
and fully inside the viewport. A hidden heading is a FAIL, never "top = 0". Also records the area above the tab bar and whether
the page carries the "Verify this page" tab and the one-line verifier summary.

  python tab_acceptance_live.py --site https://mahmood726-cyber.github.io/meta-harness/ --slugs-from <commit> --out tabs.json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

JS = r"""async ([]) => {
  const nav = document.querySelector('nav'); const tabs = [...document.querySelectorAll('nav button')];
  let pass = 0; const fails = [];
  for (const scenario of ['top', 'from-navbar', 'deep']) {
    for (let i = 0; i < tabs.length; i++) {
      const b = tabs[i];
      if (scenario === 'top') window.scrollTo(0, 0);
      else { tabs[(i + tabs.length - 1) % tabs.length].click(); window.scrollTo(0, document.body.scrollHeight);
             if (scenario === 'from-navbar') window.scrollTo(0, nav.getBoundingClientRect().top + window.scrollY); }
      b.click();
      const sec = document.getElementById('tab-' + b.dataset.t);
      const h = sec && sec.querySelector('h3.tabname');
      const vis = !!h && getComputedStyle(h).display !== 'none' && h.getBoundingClientRect().height > 0;
      const top = vis ? h.getBoundingClientRect().top : null;
      if (vis && top >= 0 && top + h.getBoundingClientRect().height <= window.innerHeight) pass++;
      else fails.push(`${scenario}:${b.dataset.t}@${top === null ? 'hidden' : Math.round(top)}`);
    }
  }
  window.scrollTo(0, 0);
  return {iw: window.innerWidth, ih: window.innerHeight, tabs: tabs.length, pass, of: tabs.length * 3,
          above: Math.round(nav.getBoundingClientRect().top), verify_tab: !!document.getElementById('tab-verify'),
          verify_line: !!document.getElementById('verify-line'), fails: fails.slice(0, 6)};
}"""


def slugs_at(commit: str) -> list[str]:
    out = subprocess.run(["git", "-C", "C:/mh-lanes/pva", "ls-tree", "--name-only", commit, "docs/reviews/"],
                         capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout.split()
    return [p.split("/")[-1] for p in out if "." not in p.split("/")[-1]]


def browser_exe() -> str:
    for p in (Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft/Edge/Application/msedge.exe",
              Path(os.environ.get("PROGRAMFILES", "")) / "Microsoft/Edge/Application/msedge.exe",
              Path(os.environ.get("PROGRAMFILES", "")) / "Google/Chrome/Application/chrome.exe"):
        if p.is_file():
            return str(p)
    raise SystemExit("REFUSED: no local Edge/Chrome for the headless browser")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="https://mahmood726-cyber.github.io/meta-harness/")
    ap.add_argument("--slugs-from", help="commit whose docs/reviews/ lists the pages to check")
    ap.add_argument("--slugs", help="comma list instead of --slugs-from (controls)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--sizes", default="1280x800,375x812")
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright
    slugs = a.slugs.split(",") if a.slugs else slugs_at(a.slugs_from)
    if not slugs:
        raise SystemExit(f"REFUSED: no pages listed at {a.slugs_from}")
    sizes = [tuple(int(v) for v in s.split("x")) for s in a.sizes.split(",")]
    runs, t0 = [], time.time()
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path=browser_exe(), headless=True)
        try:
            for w, h in sizes:
                ctx = br.new_context(viewport={"width": w, "height": h})
                page = ctx.new_page()
                for s in slugs:
                    url = f"{a.site.rstrip('/')}/reviews/{s}/?nc={int(time.time() * 1000)}"
                    try:
                        resp = page.goto(url, wait_until="load", timeout=120000)
                        r = page.evaluate(JS, [])
                        r.update(slug=s, w=w, h=h, http=resp.status if resp else None)
                    except Exception as e:  # noqa: BLE001 -- a page that cannot be measured is a FAIL with its reason
                        r = {"slug": s, "w": w, "h": h, "pass": 0, "of": 1, "error": f"{type(e).__name__}: {str(e)[:200]}"}
                    runs.append(r)
                    print(f"{w}x{h} {s[:40]:40} {r.get('pass')}/{r.get('of')} above={r.get('above')} verify_tab={r.get('verify_tab')}", flush=True)
                ctx.close()
        finally:
            br.close()
    bad = [r for r in runs if r.get("pass") != r.get("of") or not r.get("verify_tab") or r.get("http") != 200]
    summary = {"site": a.site, "pages": len(slugs), "runs": len(runs), "checks": sum(r.get("of", 0) for r in runs),
               "passed": sum(r.get("pass", 0) for r in runs), "all_pass": not bad,
               "above_max": {f"{w}x{h}": max((r.get("above") or 0) for r in runs if r.get("w") == w) for w, h in sizes},
               "innerWidth_seen": sorted({r.get("iw") for r in runs if r.get("iw")}), "bad": bad[:20],
               "seconds": round(time.time() - t0)}
    Path(a.out).write_text(json.dumps({"summary": summary, "runs": runs}, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1)[:1500])
    sys.exit(0 if not bad else 1)


if __name__ == "__main__":
    main()
