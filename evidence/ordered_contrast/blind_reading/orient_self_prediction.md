Written 2026-09-25T08:55:25Z, BEFORE the blind reader's labels were seen.
Parser (both implementations identical on all 27) predicted-wrong items, by my own reading:
- C09 "Events occurred in 694 placebo recipients and 608 liraglutide recipients (hazard ratio for liraglutide, 0.87 ...)":
  parser -> placebo (ORDER_OF_MENTION); the words 'hazard ratio for liraglutide' make liraglutide the numerator. MISSING RULE: a ratio 'for X' names X as numerator.
- C05 "... 8.9% of the placebo group and in 6.6% of the semaglutide group; the hazard ratio was 0.74":
  parser -> placebo (ORDER_OF_MENTION). The words alone do not settle it (null is right); the rates (6.6/8.9 = 0.74) say semaglutide/placebo.
  ORDER_OF_MENTION is a convention and is wrong here. MISSING WITNESS: per-arm rates vs the estimate.
Everything else I expect to agree, with C18 ('hazard ratio vs placebo') answered by the parser as the implied experimental arm.
