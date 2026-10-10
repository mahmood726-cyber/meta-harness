"""Does a comparator print a PER-TRIAL row for our outcome anywhere in its held text? (tranexamic, 10 Oct: a WOMAN
death-due-to-bleeding row in comparator 39461793 would give G1 a shared trial.) Deterministic, no model:

  tables     every JATS <table-wrap> row and every supplement line that names our outcome (g1_tracker.binding_verdict
             on the row label) AND one trial label of the comparator's set AND an 'e/N' cell
  figures    every JATS <fig> caption: a figure whose caption names ANOTHER outcome is recorded with that outcome (its
             per-trial rows are not ours); a figure naming ours would need the dual forest reader (never read here)
  verdict    FOUND (rows listed) / FIGURE_ONLY (a caption names our outcome: route to scripts/g1_forest_reader.py) /
             NOT_FOUND (every held text searched; the texts and their sha256 are listed)

    python scripts/g1_comparator_trial_row_search.py SLUG  -> outputs/k_gap/g1_binding/comparator_trial_rows_<slug>.json
"""
from __future__ import annotations

import glob
import hashlib
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
_N = r"(?:\d{1,3}(?:[    ,]\d{3})+|\d+)"     # '10 036', '27,307' or plain '9985'
_EN = re.compile(r"\b" + _N + r"\s*/\s*" + _N + r"\b")


def _plain(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " | ", s))


def names_outcome(text, po):
    """The text names OUR OUTCOME -- not merely the condition: the binding keyword must carry the outcome's head word
    ('death' for 'Death due to bleeding'). A bare condition keyword ('postpartum haemorrhage') names a hysterectomy row
    too, and is never enough."""
    import g1_tracker as gt
    v = gt.binding_verdict(po["name"], po.get("keywords") or [], text, 2)
    head = (re.findall(r"[a-z]{3,}", po["name"].lower()) or [""])[0]
    return v["verdict"] == "BINDABLE" and any(re.search(r"\b" + re.escape(head) + r"\b", k.lower())
                                              for k in v.get("named_by") or [])


def printed_name(label, jats):
    """A unit label glued to its citation number ('WOMAN-210' = 'WOMAN-2' + ref 10) -> the trial name AS PRINTED: the
    split whose name is followed by its number in the comparator's own text ('WOMAN-2 10', 'WOMAN, 1'). No such split
    -> the label unchanged (never guessed)."""
    plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", jats or ""))
    for k in range(1, len(label)):
        name, ref = label[:k], label[k:]
        if ref.isdigit() and re.search(re.escape(name) + r"\s*,?\s+" + ref + r"\b", plain):
            return name
    return label


def search_texts(jats, supp, po, trials):
    """(rows, figures): per-trial rows for our outcome in the JATS tables / supplement lines, and every figure caption
    with whether it names our outcome."""
    tr = [t for t in trials if t]
    rows, figs = [], []
    for m in re.finditer(r"<table-wrap\b.*?</table-wrap>", jats or "", re.S):
        for row in re.findall(r"<tr\b[^>]*>.*?</tr>", m.group(0), re.S):      # rows with attributes too
            p = _plain(row)
            cells = [c.strip() for c in p.split("|") if c.strip()]
            label = cells[0] if cells else ""
            named = [t for t in tr if re.search(r"\b" + re.escape(t) + r"\b", p)]
            # a POOLED row lists several trials as contributors; a per-trial row names exactly one
            if label and names_outcome(label, po) and len(named) == 1 and len(_EN.findall(p)) >= 2:
                rows.append({"where": "jats table", "trial": named[0], "row": p.strip()[:300]})
    for ln in (supp or "").splitlines():
        named = [t for t in tr if re.search(r"\b" + re.escape(t) + r"\b", ln)]
        if len(named) == 1 and len(_EN.findall(ln)) >= 2 and names_outcome(ln, po):
            rows.append({"where": "supplement", "trial": named[0], "row": ln.strip()[:300]})
    for m in re.finditer(r"<fig\b.*?</fig>", jats or "", re.S):
        cap = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(0))).strip()
        head = re.split(r"(?<=[a-z)])\s+\*|\.\s", cap, maxsplit=1)[0]
        figs.append({"caption": head[:200], "names_our_outcome": names_outcome(head, po)})
    return rows, figs


def search(slug):
    t = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
    po, comp = t["primary_outcome"], str(t["comparator_pmid"])
    d = os.path.join(ROOT, "cache", "comparators", comp)
    jf = sorted(glob.glob(os.path.join(d, "*_kgap_jats.xml")))
    sf = sorted(glob.glob(os.path.join(d, "*_kgap_supplements.txt")))
    jats = open(jf[-1], encoding="utf-8").read() if jf else ""
    supp = open(sf[-1], encoding="utf-8", errors="replace").read() if sf else ""
    g1 = os.path.join(ROOT, "outputs", "k_gap", "g1", slug + ".json")
    labels = [x["label"] for x in json.load(open(g1, encoding="utf-8"))["trials"]] if os.path.exists(g1) else []
    trials = [printed_name(lab, jats) for lab in labels]
    rows, figs = search_texts(jats, supp, po, trials)
    # evidence that could not be searched is never an absence: no held JATS, or no trial inventory to name rows by
    state = ("UNAVAILABLE:NO_HELD_JATS" if not jats else "UNAVAILABLE:NO_TRIAL_INVENTORY" if not trials
             else "FOUND" if rows else "FIGURE_ONLY" if any(f["names_our_outcome"] for f in figs) else "NOT_FOUND")
    sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
    return {"slug": slug, "comparator_pmid": comp, "outcome": po["name"], "trials": trials, "state": state,
            "rows": rows, "figures": figs,
            "searched": [{"path": os.path.relpath(p, ROOT).replace("\\", "/"), "sha256": sha(p)} for p in jf[-1:] + sf[-1:]]}


READER_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["per_trial_rows", "note"],
                 "properties": {"per_trial_rows": {"type": "array", "items": {
                     "type": "object", "additionalProperties": False, "required": ["trial", "quote"],
                     "properties": {"trial": {"type": "string"}, "quote": {"type": "string"}}}},
                     "note": {"type": "string"}}}
READER_INSTR = (
    "Below are ALL the tables and ALL the figure captions of one published meta-analysis (CC BY). The outcome is "
    "'{outcome}'. List every row that reports the result of ONE SINGLE TRIAL (not a pooled row over several trials) "
    "for exactly that outcome -- not for another outcome, even a related one (death within 24 h, life-threatening "
    "bleeding and hysterectomy are other outcomes). For each, give the trial name and a VERBATIM quote of the row "
    "copied from the text. If there is none, return an empty list and say in the note which tables and figures you "
    "checked. Answer only with JSON matching: {schema}")


def shown_text(jats):
    """What a reader is shown: every table (plain) and every figure caption -- the CC BY article's own text only."""
    parts = [_plain(m.group(0)) for m in re.finditer(r"<table-wrap\b.*?</table-wrap>", jats or "", re.S)]
    parts += [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(0))).strip()
              for m in re.finditer(r"<fig\b.*?</fig>", jats or "", re.S)]
    return "\n\n".join(parts)


def gate_reader(answer, shown):
    """A reader's claimed rows count only when each quote is verbatim (whitespace-normalised) in what it was shown."""
    norm = lambda s: re.sub(r"[\s|]+", " ", s or "").strip().lower()
    sh = norm(shown)
    # NO_ROW needs an EXPLICIT empty list: a reply without the field is invalid, never a negative finding
    if not isinstance(answer, dict) or not isinstance(answer.get("per_trial_rows"), list):
        return "INVALID_REPLY"
    rows = answer["per_trial_rows"]
    # a claimed row needs a NON-EMPTY verbatim quote ('' is a substring of everything)
    bad = [r for r in rows if not norm((r or {}).get("quote")) or norm(r.get("quote")) not in sh]
    return "NO_ROW" if not rows else ("QUOTE_NOT_IN_TEXT" if bad else "ROWS_CLAIMED")


def readers(out, run):
    """Two recorded readers of different families over the CC BY tables + captions: codex and agy (Gemini)."""
    from reproducible_ai import model_call_live as mcl
    from reproducible_ai import model_source as ms
    src = out["searched"][0]
    jats = open(os.path.join(ROOT, src["path"]), encoding="utf-8").read()
    shown = shown_text(jats)
    t = json.load(open(os.path.join(ROOT, "topics", out["slug"] + ".json"), encoding="utf-8"))
    p = (READER_INSTR.format(outcome=t["primary_outcome"]["name"], schema=json.dumps(READER_SCHEMA)) +
         f"\n\n<<<TEXT (PMID {out['comparator_pmid']}, tables and figure captions)\n{shown}\nTEXT>>>\n").encode("utf-8")
    rec_dir = os.path.join(ROOT, "registry", "model_calls")
    dig = [{"ref": f"{src['path']} (CC BY JATS; tables + figure captions only)", "sha256": src["sha256"],
            "what": "the comparator's own article text"}]
    caller = {"file": "scripts/g1_comparator_trial_row_search.py", "line": "readers", "lane": "g1/binding",
              "purpose": f"per-trial row search second reader {out['slug']}"}
    led = os.path.join(ROOT, "outputs", "k_gap", "g1_binding", f"comparator_trial_rows_{out['slug']}_readers.json")
    prev = json.load(open(led, encoding="utf-8")) if os.path.exists(led) else {}
    res = dict(prev)
    for who in ("codex", "agy"):
        r0, ps = prev.get(who) or {}, hashlib.sha256(p).hexdigest()
        fp = os.path.join(rec_dir, f"{r0.get('record_id')}.json")
        same = _recorded(rec_dir, ps, who, caller["purpose"]) if not (os.path.exists(fp) and r0.get("prompt_sha256") == ps) \
            else fp
        if same:
            rec = ms.load_record(same)
        elif run:
            rec = (mcl.call(p, schema=READER_SCHEMA, model="gpt-6-astra", effort="high", caller=caller,
                            input_digests=dig, timeout_s=1200) if who == "codex" else
                   mcl.agy_call(p, schema=READER_SCHEMA, caller=caller, input_digests=dig, timeout_s=1200))
            ms.write_record(rec, rec_dir)
        else:
            res[who] = {"state": "NOT_RUN"}
            continue
        a = _answer(ms.replay(rec).decode("utf-8")) if rec.get("state") == "RAN_OK" else None
        res[who] = {"record_id": rec["record_id"], "prompt_sha256": ps, "answer": a,
                    "model_reported": (rec.get("model") or {}).get("id_reported"),
                    "gate": gate_reader(a, shown) if a is not None else "RAN_ERROR"}
        with open(led, "w", encoding="utf-8", newline="\n") as fh:       # after EACH reader: a later failure loses none
            json.dump(res, fh, indent=1, ensure_ascii=False)
    return res


def _answer(text):
    """The reply as JSON: bare, or ONE fenced ```json block and nothing else (agy wraps its JSON in a fence). Any
    other shape is unparseable (None) -- never searched for a JSON-looking substring."""
    t = text.strip()
    m = re.fullmatch(r"```(?:json)?\s*(\{.*\})\s*```", t, re.S)
    try:
        return json.loads(m.group(1) if m else t)
    except ValueError:
        return None


def _recorded(rec_dir, prompt_sha, who, purpose):
    """An already-written record of this exact prompt by this client (a run that failed after writing it): reused,
    never re-called. The earliest by request time."""
    hits = []
    for f in glob.glob(os.path.join(rec_dir, "mc-*.json")):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        cli = json.dumps(d.get("client") or {}).lower()
        if (d.get("prompt") or {}).get("sha256") == prompt_sha and (d.get("caller") or {}).get("purpose") == purpose \
                and d.get("state") == "RAN_OK" and (("agy" in cli) == (who == "agy")):
            hits.append((d.get("request_utc") or "", f))
    return sorted(hits)[0][1] if hits else None


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    for s in [a for a in sys.argv[1:] if not a.startswith("--")]:
        out = search(s)
        if out["searched"]:
            rd = readers(out, run="--readers" in sys.argv)
            out["second_readers"] = {k: v.get("gate", v.get("state")) for k, v in rd.items()}
            out["readers_agree_with_search"] = all(v == "NO_ROW" for v in out["second_readers"].values()) \
                if out["state"] == "NOT_FOUND" else None
        p = os.path.join(ROOT, "outputs", "k_gap", "g1_binding", f"comparator_trial_rows_{s}.json")
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=1, ensure_ascii=False)
        print(s, out["state"], len(out["rows"]), [f["caption"][:70] for f in out["figures"]])
