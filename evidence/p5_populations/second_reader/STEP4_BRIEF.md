# BRIEF — screen search hits for a same-trial protocol / design / baseline paper (evid2)

`row.json` has `trial` (one randomized trial's own record: title, authors, journal, year, abstract) and `hits`
(bibliographic records returned by two literature queries). Decide, from row.json ONLY, which hits could be a
protocol, design/rationale, methods or baseline-characteristics paper **of this same trial** (same intervention, same
comparator, same population, overlapping authors, plausible date). A different trial, a review, or an unrelated field
is `NO`. When the record gives too little to tell, `POSSIBLE`; only call `LIKELY` with a concrete reason.

Write `out.json`: `{"key": "...", "screened": <number of hits>, "candidates": [{"pmid": "...", "pmcid": "...",
"verdict": "LIKELY|POSSIBLE", "why": "<one sentence>"}]}` -- list only LIKELY/POSSIBLE hits; an empty list is a valid
answer.
