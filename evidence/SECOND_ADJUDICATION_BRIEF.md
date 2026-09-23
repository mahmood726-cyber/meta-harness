# Second adjudication brief (independent reviewer)

You are the SECOND, independent adjudicator of one ruling made by another model family. Your job is to REFUTE it
if it is wrong. Read two files: the ruling `evidence/adjudication/<KEY>.json` and the packet
`evidence/packets/<KEY>.json` (every source text we hold for the trial). Use only those texts as evidence.

Judge three things separately:
1. NUMBER: is the ruling right about which number the source states for the served outcome (endpoint, arm,
   population, timepoint, scale, CI level)? If the ruling rejected the served candidate, is the proposed number right?
2. ENTRY: is the entry-population ruling (ESTABLISHED / PARTLY / NOT_ESTABLISHED) right for the packet's `question`?
3. ANYTHING the ruling missed that would change 1 or 2.

Quote verbatim (character for character) from a packet source for every claim; name the source `ref`.

Output ONLY this JSON object:
{"key": "...", "number": {"verdict": "AGREE" | "DISAGREE" | "CANNOT_TELL", "why": "...", "quotes": [{"ref": "...", "span": "..."}]},
 "entry": {"verdict": "AGREE" | "DISAGREE" | "CANNOT_TELL", "your_ruling": "ESTABLISHED|PARTLY|NOT_ESTABLISHED", "why": "...", "quotes": [...]},
 "missed": "..." }
