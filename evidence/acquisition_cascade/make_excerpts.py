"""Committed EXCERPTS of held documents that may be read but not redistributed (free-to-read PMC pages of journal
articles without an open licence). An excerpt is a short verbatim quotation -- a table's caption, its column headings
and ONE row, or one sentence -- each located EXACTLY ONCE in the tag-stripped text of the held page, with the page's
URL, fetch record and sha256 in the header. The full page stays local (gitignored); anyone can re-fetch it and check
the quotation. Excerpts are what the harness binds to, so a clean clone reproduces the same binding.
  python evidence/acquisition_cascade/make_excerpts.py"""
import hashlib, html, json, os, re, sys

D = os.path.dirname(os.path.abspath(__file__))
HELD = os.path.join(D, "held")
OUT = os.path.join(D, "excerpts")
LEDGER = json.load(open(os.path.join(HELD, "HELD.json"), encoding="utf-8"))


def plain(p):
    s = open(p, encoding="utf-8", errors="replace").read()
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"</?[A-Za-z][A-Za-z0-9:.-]*(?:\s[^<>]*)?/?>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


EXCERPTS = {
    "CoDEX_table2_28day_mortality.txt": ("CoDEX/pmc_article.html", [
        ("table2_caption_and_arm_headings",
         "Table 2. Study Outcomes. Outcomes Mean (95% CI) Effect statistic Between-group effect Adjusted a Unadjusted "
         "Dexamethasone (n = 151) Standard care (n = 148)"),
        ("table2_row_28day_all_cause_mortality",
         "28-Day results All-cause mortality No. (%) 85 (56.3) 91 (61.5) HR 0.97 (0.72 to 1.31) .85 0.86 (0.64 to 1.15) .31"),
        ("methods_secondary_outcome", "Secondary outcomes were all-cause mortality at 28 days"),
    ]),
    "COVIDICUS_recruitment_periods.txt": ("COVIDICUS/pmc_article.html", [
        ("period1_placebo_36_vs_37",
         "From April 10 to September 17, 2020, 73 patients were randomized between placebo (37 patients) and "
         "high-dose dexamethasone (36 patients)"),
        ("period2_after_amendment_234_vs_239",
         "Thereafter, 473 patients were randomly allocated between standard dexamethasone (239 patients) or high-dose "
         "dexamethasone (234 patients)"),
        ("comparator_changed_at_amendment",
         "Initially, the standard dexamethasone group received a nondexamethasone placebo. From the amendment "
         "implementation, the standard of care moved to an intravenous administration of dexamethasone-phosphate 6 mg/d"),
        ("whole_trial_60day_hr",
         "There was no difference in 60-day mortality between standard and high-dose dexamethasone groups (HR, 0.96 "
         "[95% CI, 0.69-1.33]; P = .79)"),
        ("period_effect_modelled_not_reported",
         "Period effect (ie, before vs after the protocol amendment for standard dexamethasone) was tested using fixed "
         "covariate in the regression models"),
    ]),
}


def table_rows_of(rel, caption_prefix, want_rows):
    """The cells of one HTML table in a held page, verbatim per cell: header rows, then only the rows whose first cell
    is listed in `want_rows` (a section heading row and the result row), serialised the way harness.hand_binding reads
    tables ('=== TABLES', 'TABLE <caption>', ' | '-joined cells)."""
    s = open(os.path.join(HELD, rel), encoding="utf-8").read()
    i = s.find(caption_prefix)
    if i < 0 or s.count(caption_prefix) < 1:
        sys.exit(f"REFUSED: caption {caption_prefix!r} not in {rel}")
    j = s.find("<table", i)
    tab = s[j:s.find("</table>", j)]
    cell = lambda c: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c))).strip()
    rows = [[cell(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)]
            for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", tab, re.S)]
    header = []
    for r in rows:
        if any(re.search(r"\d\s*\(|\d+\.\d", c) for c in r[1:]) or len([c for c in r if c]) <= 1:
            break
        header.append(r)
    body = [r for r in rows if r and r[0] in want_rows]
    if len(body) != len(want_rows):
        sys.exit(f"REFUSED: rows {want_rows} found {len(body)} times in {rel}")
    return header, body


def main():
    os.makedirs(OUT, exist_ok=True)
    # CoDEX Table 2: the table itself, as cells, for the binder (caption, header rows, the 28-Day section row, the row)
    rel = "CoDEX/pmc_article.html"
    header, body = table_rows_of(rel, "Table 2.", ["28-Day results", "All-cause mortality No. (%)"])
    sha = hashlib.sha256(open(os.path.join(HELD, rel), "rb").read()).hexdigest()
    lines = ["# EXCERPT (table cells, verbatim) of a held document that is not redistributed",
             f"# source_url: {LEDGER[rel]['source']}", f"# held_sha256: {sha}",
             "# Table 2 caption, its header rows, the '28-Day results' section row and the all-cause mortality row only", "",
             "=== TABLES (excerpt) ===", "TABLE Table 2. Study Outcomes."]
    lines += [" | ".join(c for c in r if c) for r in header]
    lines += [" | ".join(r) if r[0] != "28-Day results" else r[0] for r in body]
    open(os.path.join(OUT, "CoDEX_table2.tables.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("wrote CoDEX_table2.tables.txt", len(header), "header rows,", len(body), "body rows")
    for name, (rel, spans) in EXCERPTS.items():
        meta = LEDGER[rel]
        full = os.path.join(HELD, rel)
        sha = hashlib.sha256(open(full, "rb").read()).hexdigest()
        if sha != meta["sha256"]:
            sys.exit(f"REFUSED: {rel} bytes differ from the ledger")
        text = plain(full)
        lines = [f"# EXCERPT of a held document (verbatim quotations only; the document itself is not redistributed)",
                 f"# source_url: {meta['source']}", f"# held_path (local, gitignored): evidence/acquisition_cascade/held/{rel}",
                 f"# held_sha256: {sha}", f"# route: {meta.get('route')}  licence: {meta.get('licence')}",
                 "# each line below: <kind>\\t<verbatim text, located exactly once in the tag-stripped page>", ""]
        for kind, span in spans:
            n = text.count(span)
            if n != 1:
                sys.exit(f"REFUSED: {name}:{kind} occurs {n} times in {rel}")
            lines.append(f"{kind}\t{span}")
        open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
        print("wrote", name, len(spans), "spans")


if __name__ == "__main__":
    main()
