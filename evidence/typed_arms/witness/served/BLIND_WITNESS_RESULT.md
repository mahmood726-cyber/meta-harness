# Blind token-witness pass over the 35 served rows (PREREG addendum C) -- result

**130 of 132** witnessed arm fields carry the same VALUE in the blind pass (served numbers hidden); **124 of 132** cite
the same source occurrence. The only value difference is one row, CARMELINA hypoglycaemia (dpp4-mace-t2d 2-0): the
blind pass -- without the corrective addendum the first pass received -- again chose the registry's `otherEvents`
"Hypoglycaemia" (1022 vs 1003), a non-serious term reported above a frequency threshold; the registry lists serious
hypoglycaemia separately (28 vs 38). The served 1036 vs 1024 is the publication's "1 or more episodes of hypoglycemia".
Pre-registered classification: **BOTH_DEFENSIBLE** (the source prints two readings for the outcome name), not
FIRST_PASS_ANCHORED -- so no row is withdrawn from `v2/OBSERVATIONS_served.json`. The row is flagged for the main lane
as schema question S4: when the registry's only match for an outcome name is a thresholded non-serious AE term, does
registry-first ownership still govern?

Logging: the pass's CALL_LOG had one line corrupted by two slots appending at once (the same race that lost a line in
the held blind pass). It was rebuilt from the 35 raw event streams (35 lines, 35 artefacts, 0 off-tree paths); the
corrupted file is kept off-repo. The runner now writes one summary file per call and rebuilds CALL_LOG by
concatenation into a per-process temporary file, so concurrent slots cannot interleave.
