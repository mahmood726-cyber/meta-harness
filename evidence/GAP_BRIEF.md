# Gap brief (one row): close a named evidence gap from newly held full text

Read the packet (packet.json) and the lane's ruling (adjudication.json). The packet now
includes the trial's FULL TEXT (a `held_local/...html` source). Use only the packet's texts as evidence.

For THIS row's served outcome, find verbatim spans (character for character from one source's text, name its `ref`,
<= 350 chars) for each gap below, or say `NOT_FOUND` with where you looked:

- analysis_set: the population the served outcome's estimate was analysed in (ITT / mITT / per-protocol / safety / all randomised / available cases), stated for THIS outcome or for the trial's efficacy analyses generally (say which)
- follow_up: the follow-up duration / assessment timepoint for the served outcome
- entry_age: the trial's age criterion at entry (e.g. "aged 18 years or older")
- entry_other: anything in the entry criteria that makes the population fall outside the packet's `question` (quote it), or NONE

Output ONLY: {"key": "...", "analysis_set": {"ref": "...", "span": "...", "scope": "THIS_OUTCOME|EFFICACY_GENERAL"} | "NOT_FOUND",
 "follow_up": {...} | "NOT_FOUND", "entry_age": {...} | "NOT_FOUND", "entry_other": {...} | "NONE", "notes": "..."}
