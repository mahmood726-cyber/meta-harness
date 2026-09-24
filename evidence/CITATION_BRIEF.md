# Citation check brief (one served row)

A served meta-analysis row carries a citation meant to DEFINE the endpoint of its served outcome
(`compat_span`). Judge only that citation, using the item below and the packet's source texts.

- RIGHT_ENDPOINT: the citation defines the served outcome's endpoint (the one whose number is served)
- WRONG_ENDPOINT: the citation defines a different endpoint (e.g. the trial's primary composite when the served
  outcome is a secondary or harm outcome)
- OUTCOME_NAME_ONLY: the citation is just the outcome's name, no definition
- NOTE_NOT_A_SPAN: the citation is an editorial note, not a quotation
- CANNOT_TELL: say why

Output ONLY: {"key": "...", "verdict": "...", "why": "...", "quote": "<verbatim quote from a packet source that
decides it, or null>"}
