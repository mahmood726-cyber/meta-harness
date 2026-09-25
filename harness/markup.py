"""Strip MARKUP from source text without eating the science (lane OC, V1.1).

The defect: every source-text site stripped tags with `<[^>]+>`, which treats ANY '<' as the start of a tag. Scientific text is full
of literal '<' and '>' -- "(P<0.001), HR 0.82 (95% CI 0.70 to 0.96; P>0.2)" -- and the regex deleted everything from 'P<' to the
next '>', here the whole effect tuple. Measured on the committed caches: 84 of the 891 abstracts that contain '<' (26 topics) lost
prose; full texts and comparator full texts lost more (evidence/v11_tag_strip/).

A '<' opens markup ONLY when what follows is markup syntax:
  <name ...> / </name>   -- a letter after '<' (or '/' then a letter), attributes containing no '<' or '>'
  <!-- ... -->, <![CDATA[ ... ]]>, <? ... ?>, <!DOCTYPE ...>
'<' followed by a digit, a space, '.', '=' or '-' is TEXT ("P<0.001", "age < 65", "p<.05", "<=", "<-") and is kept, as is every '>'
that does not close a recognised tag. Entities are not decoded here: '&lt;' is already text and stays text; callers that decode do
so after stripping, as before.
"""
from __future__ import annotations

import re

MARKUP = re.compile(r"<!--.*?-->|<!\[CDATA\[.*?\]\]>|<\?.*?\?>|<![A-Za-z][^<>]*>|</?[A-Za-z][A-Za-z0-9:._-]*(?:\s[^<>]*)?/?>", re.S)


def strip_markup(text: str | None, repl: str = " ") -> str:
    """Remove markup tokens only; every other character of the source survives."""
    return MARKUP.sub(repl, text or "")
