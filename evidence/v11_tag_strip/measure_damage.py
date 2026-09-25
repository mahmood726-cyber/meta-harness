"""Tag-stripping damage in held source text, before vs after the V1.1 fix (lane OC).

Universe: every text field the harness can strip that is held in the committed caches -- cache/<slug>/records.json record abstracts,
(also cache/<slug>/ft_<pid>.txt, the held full texts the declared-absent classifier reads),
fulltext_by_pmid full texts, and comparator_fulltext -- for all topic caches present (38) and for the 32 served topics.
Two damage definitions, both reported, because they give different counts and neither should be quoted without its rule:
  TOKEN  (primary, independent): a word or number that the stdlib html.parser keeps as TEXT (it reads '<0.001' as data) is missing
         from the stripped output. The reference is a different implementation from both strippers.
  CHARS  (the main lane's figure): the stripped output has fewer non-space characters than the reference-free strict stripper's.
BEFORE = `<[^>]+>` (the old regex at every source site); AFTER = harness.markup.strip_markup.
usage: python evidence/v11_tag_strip/measure_damage.py <live_slugs.txt> <out.json>"""
import collections
import glob
import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from harness.markup import strip_markup  # noqa: E402

OLD = re.compile(r"<[^>]+>")
TOK = re.compile(r"[A-Za-z]+|\d+(?:\.\d+)?")


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.parts = []

    def handle_data(self, d):
        self.parts.append(d)


def reference_tokens(text):
    p = _Text()
    p.feed(text)
    p.close()
    return TOK.findall(" ".join(p.parts))


def token_damage(stripped, ref):
    have = set(TOK.findall(stripped))
    return [t for t in ref if t not in have]


_TAG_SHAPED = re.compile(r"<[A-Za-z/!?][^<>]*>")


def text_loss(lost, text):
    """Lost tokens that are PROSE: the token occurs in the source OUTSIDE every tag-shaped span. A token that appears only inside
    '<name attr="...">' is markup the reference parser happened to report as data (html.parser is not an XML parser; on some JATS
    files it reads tag attributes as text), not lost prose."""
    outside = set(TOK.findall(_TAG_SHAPED.sub(" ", text)))
    return [t for t in lost if t in outside]


def nonspace(s):
    return len(re.sub(r"\s+", "", s))


def main(live_file, out):
    live = set(open(live_file, encoding="utf-8").read().split())
    agg = collections.defaultdict(lambda: {"fields": 0, "with_lt": 0, "token_before": 0, "token_after": 0, "chars_before": 0,
                                           "chars_after": 0, "topics_before": set(), "topics_after": set()})
    examples = []
    for p in sorted(glob.glob(os.path.join(ROOT, "cache", "*", "records.json"))):
        slug = os.path.basename(os.path.dirname(p))
        d = json.load(open(p, encoding="utf-8"))
        fields = [("abstract", str(r.get("id")), r.get("abstract")) for r in d.get("records") or [] if r.get("abstract")]
        fields += [("fulltext", k, v) for k, v in (d.get("fulltext_by_pmid") or {}).items() if isinstance(v, str)]
        if isinstance(d.get("comparator_fulltext"), str) and d["comparator_fulltext"]:
            fields.append(("comparator_fulltext", "comparator", d["comparator_fulltext"]))
        for fp in sorted(glob.glob(os.path.join(ROOT, "cache", slug, "ft_*.txt"))):      # the held full texts classify_reason reads
            fields.append(("ft_file", os.path.basename(fp), open(fp, encoding="utf-8", errors="replace").read()))
        for kind, fid, t in fields:
            for u in ["all_caches"] + (["served_topics"] if slug in live else []):
                a = agg[(u, kind)]
                a["fields"] += 1
                if "<" not in t:
                    continue
                a["with_lt"] += 1
                ref = reference_tokens(t)
                old_s, new_s = OLD.sub(" ", t), strip_markup(t)
                tb, ta = token_damage(old_s, ref), token_damage(new_s, ref)
                tb = text_loss(tb, t)              # the same PROSE rule before and after
                if tb:
                    a["token_before"] += 1
                    a["topics_before"].add(slug)
                ta_prose = text_loss(ta, t)
                a.setdefault("token_after_markup_only", 0)
                if ta and not ta_prose:
                    a["token_after_markup_only"] += 1
                if ta_prose:
                    a["token_after"] += 1
                    a["topics_after"].add(slug)
                a["chars_before"] += nonspace(old_s) < nonspace(new_s)
                a["chars_after"] += 0          # AFTER is the strict stripper itself; by construction 0 -- the TOKEN rule is the check
                if tb and u == "all_caches" and len(examples) < 12:
                    i = t.find("<")
                    examples.append({"slug": slug, "kind": kind, "id": fid, "lost_tokens": tb[:12], "context": t[max(0, i - 60):i + 160]})
                if ta and u == "all_caches":
                    examples.append({"slug": slug, "kind": kind, "id": fid, "reference_tokens_missing_after": ta[:12],
                                     "of_which_prose": ta_prose[:12], "classification": "PROSE LOST" if ta_prose else "markup-only (reference parser quirk)"})
    res = {"rules": __doc__, "results": {f"{u}|{k}": {**{x: v for x, v in a.items() if not isinstance(v, set)},
                                                      "topics_before": len(a["topics_before"]), "topics_after": len(a["topics_after"])}
                                         for (u, k), a in sorted(agg.items())}, "examples": examples}
    json.dump(res, open(out, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    for k, v in res["results"].items():
        print(f"{k:34s} fields {v['fields']:5d}  with '<' {v['with_lt']:4d}  TOKEN damaged before {v['token_before']:3d} "
              f"({v['topics_before']} topics) after {v['token_after']:3d} (+{v.get('token_after_markup_only', 0)} markup-only)  | CHARS before {v['chars_before']:3d}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
