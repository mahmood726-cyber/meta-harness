"""Landing 3 ratchet accounting BEFORE any signature: (1) pair every lost block with a same-page replacement block
sharing its heading prefix; print the unpaired ones verbatim (those need reading, or Mahmood); (2) for every
marker decrease, measure whether the page's NEW typed states (extracted harm rows, typed refusals with codes the
marker does not count) account for the decrease. Prints, signs nothing."""
import io, json, re, subprocess, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = "C:/mh-int"; BASE = "4ee334537f952ff5898b27446f3c4f3eac14ba12"
sys.path.insert(0, ROOT)
from harness import honest_ratchet as hr
P = open("F:/claude-temp/claude/C--meta-harness/ba56f4ae-2153-4cbd-9f73-1dab4f1d2c65/scratchpad/ratchet3.txt", encoding="utf-8").read().split("\n")
def show(page): return subprocess.run(["git", "-C", ROOT, "show", f"{BASE}:{page}"], capture_output=True, text=True, encoding="utf-8").stdout
def head(t): return re.split(r"[:—(]| — |\. ", t)[0].strip()[:40]
pages = sorted({p.split(":")[0] for p in P if p.strip()})
unpaired = []; paired = 0; pairs = {}
for page in pages:
    base_html = show(page); new_html = open(f"{ROOT}/{page}", encoding="utf-8").read()
    bb = {b["sha256"]: b for b in hr.blocks(base_html)}; nb = hr.blocks(new_html)
    new_by_head = collections.defaultdict(list)
    for b in nb: new_by_head[head(b["text"])].append(b)
    for line in [p for p in P if p.startswith(page + ": lost")]:
        sha = re.search(r"block ([0-9a-f]{64})", line).group(1)
        lb = bb.get(sha)
        if not lb: unpaired.append((page, sha, "LOST BLOCK NOT FOUND IN BASE PARSE")); continue
        cands = [b for b in new_by_head.get(head(lb["text"]), []) if b["sha256"] not in bb]
        if cands: paired += 1; pairs[(page, sha)] = (lb, cands[0])
        else: unpaired.append((page, sha, lb["text"][:200]))
print(f"lost blocks: {paired + len(unpaired)}; paired by heading on the same page: {paired}; UNPAIRED: {len(unpaired)}")
for page, sha, txt in unpaired: print("  UNPAIRED", page.split('/')[2] if page.count('/') > 2 else page, sha[:12], "|", txt[:160])
json.dump({f"{k[0]}|{k[1]}": {"lost_text": v[0]["text"], "replacement_sha256": v[1]["sha256"], "replacement_text": v[1]["text"], "cls": v[0]["cls"]} for k, v in pairs.items()},
          open("F:/claude-temp/claude/C--meta-harness/ba56f4ae-2153-4cbd-9f73-1dab4f1d2c65/scratchpad/ratchet3_pairs.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("\nMARKER DECREASES — coverage by new typed states on the same page (rendered text counts):")
NEW_STATES = ["REFUSED_ON_EVIDENCE", "SIGNAL_SPURIOUS", "RETRIEVED_REFUSED_WITH_REASON", "RETRIEVED_INCOMPATIBLE_STRUCTURE",
              "ENGINE_CANNOT_CONSUME", "typed refusal", "extracted from", "EXTRACTED", "KNOWN_REPORTED_NOT_YET_EXTRACTED", "DESIGN_UNPROVEN", "UNPROVEN"]
for line in [p for p in P if "base count" in p]:
    page, kind, rest = line.strip().split(": ", 2)
    b, n = map(int, re.findall(r"count (\d+)", rest))
    bt = hr._rendered_text(show(page)); nt = hr._rendered_text(open(f"{ROOT}/{page}", encoding="utf-8").read())
    gains = {s: nt.count(s) - bt.count(s) for s in NEW_STATES}
    gained = sum(v for v in gains.values() if v > 0)
    print(f"  {page.split('/')[2]:45s} {kind:16s} {b:4d} -> {n:4d} (drop {b-n:3d}); new typed-state mentions gained: {gained:4d} {'COVERED' if gained >= b-n else 'NOT COVERED'} {dict((k,v) for k,v in gains.items() if v)}")
