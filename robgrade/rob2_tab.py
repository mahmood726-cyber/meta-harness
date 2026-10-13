"""RoB 2 tab rendered from the per-trial objects (outputs/robgrade/rob2/<slug>.json), with the NI policy's label
(outputs/robgrade/NI_POLICY.md section 5). A PREVIEW for the signing packet: nothing here writes to docs/.

Every judgement is shown as the algorithm gave it. An NI-driven judgement carries its label, which says only what was
computed: which asked questions were not reported, and the judgement if they had been reported favourably.

    python -m robgrade.rob2_tab SLUG ...   -> outputs/robgrade/tab_preview/<slug>.html
"""
import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from robgrade import rob2_formal as rf  # noqa: E402

WORDS = {"LOW": "Low", "SOME_CONCERNS": "Some concerns", "HIGH": "High", rf.INSUFFICIENT: "Not assessed (no open source)",
         "NOT_ESTABLISHED": "Not established"}


PROBABLY = {"PY": "probably yes", "PN": "probably no"}


def contextual_note(dom):
    """' [contextual: 1.2 probably yes, from '<quote>']' for every contextual answer in the domain (CONTEXTUAL_POLICY C5:
    never silent), else ''. When the answer carries its readers' contexts, EVERY quote is shown with its source
    (codex round 3), so a reader of the page can judge each one."""
    xs = []
    for q, a in sorted((dom.get("answers") or {}).items()):
        closed = a.get("closed_contextual")
        if closed:                                     # A3 (candidate 4): a decision on a branch since closed is shown
            word = PROBABLY.get(closed.get("answer"), closed.get("answer"))
            ctx = closed.get("context") or []
            src = "; ".join(f"'{c.get('quote')}' ({c.get('source_id')})" for c in ctx) if ctx else f"'{closed.get('span')}'"
            xs.append(f"{q} not asked: its branch closed after a contextual answer; it had been decided {word}, from {src}")
            continue
        if a.get("basis") != "contextual":
            continue
        word = PROBABLY.get(a.get("answer"), a.get("answer"))
        ctx = a.get("context") or []
        if ctx:
            xs.append(f"{q} {word}, from " + "; ".join(f"'{c.get('quote')}' ({c.get('source_id')})" for c in ctx))
        else:
            xs.append(f"{q} {word}, from '{a.get('span')}'")
    return f" [contextual: {'; '.join(xs)}]" if xs else ""


def domain_label(dom):
    """'Some concerns (NI-driven: 1.2 not reported; Low if reported favourably)', or the judgement alone; any contextual
    answer is named after it."""
    return _domain_label(dom) + contextual_note(dom)


def _domain_label(dom):
    j = WORDS.get(dom["judgement"], dom["judgement"])
    ni = dom.get("ni")
    if not ni or not ni["ni_driven"]:
        return j
    if ni["decisive_ni_questions"]:
        which = ", ".join(ni["decisive_ni_questions"]) + " not reported"
    else:                                       # only their joint resolution lowers it
        which = ", ".join(ni["ni_questions"]) + " not reported (together)"
    return f"{j} (NI-driven: {which}; {WORDS[ni['if_ni_resolved_favourably']]} if reported favourably)"


def overall_label(ov, domains=None):
    """The overall judgement, its NI-driven label and review flag, and -- never silently (agy round 2) -- the domains
    whose answers include a contextual one."""
    return _overall_label(ov) + _contextual_domains(domains)


def _contextual_domains(domains):
    ds = [d for d, x in sorted((domains or {}).items())
          if any(a.get("basis") == "contextual" or a.get("closed_contextual")
                 for a in (x.get("answers") or {}).values())]
    return f" [contextual answers in: {', '.join(ds)}]" if ds else ""


def _overall_label(ov):
    j = WORDS.get(ov["judgement"], ov["judgement"])
    ni = ov.get("ni")
    flags = " [several domains with some concerns: for a review author's judgement]" \
        if "MULTIPLE_SOME_CONCERNS_FOR_REVIEW" in (ov.get("flags") or []) else ""
    if not ni or not ni["ni_driven"]:
        return j + flags
    return (f"{j} (NI-driven: {', '.join(ni['ni_driven_domains'])}; {WORDS[ni['if_ni_resolved_favourably']]} if the "
            f"missing answers were reported favourably){flags}")


def render(slug, doc):
    rows = []
    for pmid, o in sorted(doc["trials"].items()):
        cells = "".join(f"<td>{html.escape(domain_label(o['domains'][d]))}</td>" for d in rf.DOMAINS)
        rows.append(f"<tr><th>PMID {html.escape(pmid)}</th>{cells}<td>{html.escape(overall_label(o['overall'], o['domains']))}</td></tr>")
    head = "".join(f"<th>{d}</th>" for d in rf.DOMAINS)
    return ("<!doctype html><meta charset='utf-8'><title>RoB 2 preview</title>"
            f"<h1>RoB 2 (preview, not served): {html.escape(slug)}</h1>"
            "<p>Judgements are the RoB 2 algorithm's (Cochrane Handbook ch. 8). <b>NI-driven</b> marks a judgement that "
            "would be less severe if the listed signalling questions, not reported in the open sources read, had been "
            "reported favourably. The judgement itself is unchanged.</p>"
            f"<table border='1'><tr><th>Trial</th>{head}<th>Overall</th></tr>{''.join(rows)}</table>")


def main(argv):
    """--ctx: render the CONTEXTUAL objects (outputs/robgrade/rob2_ctx) into tab_preview_ctx/ -- the display path the
    contextual answers must reach (codex/agy review round 1); otherwise the v3.1 objects into tab_preview/."""
    ctx = "--ctx" in argv
    src = os.path.join(ROOT, "outputs", "robgrade", "rob2_ctx" if ctx else "rob2")
    out = os.path.join(ROOT, "outputs", "robgrade", "tab_preview_ctx" if ctx else "tab_preview")
    os.makedirs(out, exist_ok=True)
    for slug in [a for a in argv if not a.startswith("--")]:
        doc = json.load(open(os.path.join(src, f"{slug}.json"), encoding="utf-8"))
        with open(os.path.join(out, f"{slug}.html"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(render(slug, doc))
        print(slug, len(doc["trials"]))


if __name__ == "__main__":
    main(sys.argv[1:])
