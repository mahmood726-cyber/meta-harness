# Two findings from the evidence lane, tested on the real path: the tag-stripping defect, and the k=10 scenario against the external reviewer

## 1. The `<[^>]+>` defect is real, and it is V1.1 — not a V1 blocker

The lane's minimal reproduction runs exactly as stated:

    re.sub(r"<[^>]+>", " ", "(P<0.001), HR 0.82.<h4>End</h4>")   ->   "(P End "

The `<` in `P<0.001` opens a pretend tag and the hazard ratio is deleted. The same pattern is in
`harness/` at `absence.py:25`, `cites.py:33`, `hand_binding.py:100`/`:194`, `registry_multi.py:61`,
`reason_audit.py:33`, `rob2.py:529`/`:532`, and over generated HTML at `gate.py:313`,
`index.py:1089`, `honest_ratchet.py:71`.

**Exposure on our corpus, measured:** of 892 held text fields containing a `<`, **84 are damaged**,
across 26 topics. Losses reach 474 characters and include whole effect sentences — e.g.
`...exacerbation (RR 0.64; 95% CI: 0.52-0.78; P < 0.0001)...` is removed entirely.

**Does it produce a wrong served statement?** The served pages declare trials machine-absent with
reasons of the form *"no percentage-corroborated arm counts or effect+CI for this outcome found in
the abstract"*. If the deleted text held the effect, that declaration would be false and served.
Both halves of that reason were tested against all **433** declared-absent entries with a
not-found reason:

    effect+CI in the deleted text, absent from the kept text : 0   (control: detector finds an effect+CI in 660 abstracts)
    arm counts in the deleted text, absent from the kept text : 0   (control: detector finds arm counts in 390 abstracts)

Both detectors were shown to fire before being trusted; a detector that finds nothing anywhere
would have made this run void rather than clean.

**Verdict:** a genuine defect that damages held text, with **no demonstrated wrong served number or
false served absence on this corpus**. Under the scope freeze it is V1.1, and V1 names it as a
known limitation with this measurement beside it. The fix the lane proposes is adopted for V1.1:

    <!--.*?-->|<\?.*?\?>|<![A-Za-z\[][^<>]*>|</?[A-Za-z][A-Za-z0-9:_-]*(?:\s[^<>]*)?/?>

*Direction note for my own earlier checks:* this pattern can only DELETE text, so it can produce a
false absence, never a false presence. The "41 of 41 notices present in the rendered page" result
and the served-code counts are therefore unaffected in the unsafe direction.

## 2. The k=10 scenario: our pipeline vs the external reviewer — close, not identical, and the reason is the inputs

The external reviewer's independent script and the evidence lane's `BEFORE_AFTER.json` both compute
the eight-trial baseline plus FLOW and ELIXA. The baseline itself agrees to floating-point noise
(recorded in record 38: 4 of 4 quantities within 5e-12). The k=10 scenario does not:

| quantity | ours (`BEFORE_AFTER.json`) | reviewer (independent) |
|---|---|---|
| k | 10 | 10 |
| HR | 0.8613 | 0.8615325 |
| CI low | 0.8069 | 0.8068470 |
| CI high | 0.9194 | 0.9199244 |
| PI low | 0.7531 | 0.7518126 |
| PI high | 0.9852 | 0.9872650 |
| tau² | 0.0027 | (I² 31.31%) |

The differences are in the third and fourth decimals — far larger than the 1e-13 agreement on the
baseline, so this is **not** a method difference and **not** floating-point. It is an input
difference: the reviewer pooled the *published rounded* FLOW and ELIXA effects, while the lane
bound FLOW from the FDA label (HR 0.82, 212/1767 vs 254/1766) and ELIXA from FDA StatR §3.3.4.3
(HR 1.02, 0.887–1.172, ITT on-study, explicitly not the 4-point MACE+). The lane's own variant at
ELIXA's Table 8 rendering (0.89–1.18) gives 0.8612 (0.807–0.919), which moves toward the reviewer's
CI and away from its PI — consistent with the inputs being the whole story.

**Both routes give the same reading**: HR ≈ 0.861, CI excludes 1, PI entirely below 1, and I²
rising from ≈0.9% to ≈31% — the reviewer's substantive point, that the average effect is stable
while the apparent homogeneity is not, survives on our numbers too.

**Consequence for the release note:** the independent-reproduction claim is stated for the
**served k=8 baseline only**, where agreement is exact. The k=10 scenario is reported as our own
pipeline's output with the input provenance named, and the reviewer's figures are *not* quoted
beside it as agreement. Their numbers remain a cross-check and are never copied into served
content.

**Back to the evidence lane:** please state in the admission which rendering of FLOW and ELIXA is
bound, since the choice is worth ~0.0005 on the CI bound and ~0.002 on the PI bound, and a reader
comparing against the published rounded values will land on different digits.

Artefacts: `F:/claude-temp/tag_defect_exposure.py`, `tag_defect_false_absence.py`.

## 3. A third V1.1 item, found while gating this work: gitblob's per-file fallback

`harness/gitblob.blob_shas()` documents itself as "one batched git call for the set", and it is —
but only when `_is_git_toplevel(repo)` is true. When it is false the code falls back to
`_direct_hash_objects`, which spawns **one `git hash-object` process per file**.

`tests/test_architecture_identity.py::test_topic_config_byte_change_changes_identity` copies the
identity tree **without `.git`** (deliberately — it is testing identity, not git), so the clone is
never a toplevel and the fallback always fires. Measured on this machine:

    files hashed per identity() call : 469   (harness 95 + scripts 194 + configuration 89 + ...)
    identity() calls in the test     : 2
    process spawns                   : 938
    measured cost per spawn          : 0.068 s
    lower bound                      : ~64 s, plus 13-29 s to build the clone

That is why the test timed out at 300 s and again at 600 s while the rest of the suite was
competing for a saturated disk. On Linux CI a spawn costs ~2 ms, so the same code path costs ~2 s
there and the cliff never shows.

**The fallback is not necessary.** `git hash-object --stdin-paths` works outside a repository —
verified here, rc=0, 10 shas returned from a plain temp directory. Using it unconditionally turns
938 spawns into 2 and changes no hash value, since it is the same command over the same bytes.

Not done now: `gitblob.py` is inside the certificate import closure, so editing it invalidates all
32 certificates. It is a performance defect, not a wrong served number, so under the scope freeze
it is **V1.1**. Recorded here so it is not rediscovered as a mystery timeout.

*Method note:* the first hypothesis was antivirus scanning each spawned process. Measuring it gave
0.068 s per spawn — about 6 s for 89 files, nowhere near the observed cost — which killed that
explanation and pointed at the file **count** instead. The reproduction script that settled it is
`F:/claude-temp/repro_gitblob_hang.py`; it hashes the same 89 config files one at a time with a
per-call timeout and shows no call hangs, so "slow" and "hung" could be told apart.
