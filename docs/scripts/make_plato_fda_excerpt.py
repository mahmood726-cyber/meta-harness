"""FDA medical-review table segmentation; no NEJM numbers are substituted."""
from pathlib import Path
import re
try:
    from scripts.make_philo_excerpt import one, held
except ModuleNotFoundError:
    from make_philo_excerpt import one, held

ROOT = Path(__file__).resolve().parents[1]
PDF = 'evidence/acquisition_cascade/held/PLATO-regulatory/022433Orig1s000MedR.pdf'
SHA = '2222a5139d2a2f6cc1432dcf925a152d2fe0fbe77eecb28c1fd84bee98979010'
OUTPUTS = ('evidence/acquisition_cascade/excerpts/PLATO_FDA2011_Table12_major_bleeding.tables.txt',
           'evidence/acquisition_cascade/excerpts/PLATO_FDA2011_Table23_dyspnea.tables.txt')


def render(root=ROOT):
    text = held(root, PDF, SHA)
    # The review's list of tables repeats this caption with a dot leader and a page number ('....... 37'); the
    # caption is anchored to the TABLE's own heading (no dot leader) so the page locator is the table's page.
    b = one(r'(Table 12: Sponsor(?:(?!\.{3})[^\n])+?K-M%(?:(?!\.{3})[^\n])+?)[ \t]*\n(.*?)Source: p\. 182, PLATO study report',
            text, re.S)
    ns = one(r'Ticagrelor 90 mg bd\s+N = (\d+)\s+Clopidogrel 75 mg od\s+N = (\d+)', b[2])
    row = one(r'Total Major\s+(\d+)\s+(\d+\s*\([\d.]+%\)),\s*([\d.]+%)\s+(\d+)\s+(\d+\s*\([\d.]+%\)),\s*([\d.]+%)\s+([\d.]+\s*\([\d.]+,\s*[\d.]+\))', b[2])
    # Table 13 explicitly identifies Table 12's 961/929 as patients, not events.
    table13 = text[b.end():].split('Table 14: Frequency', 1)[0]
    corroboration = one(r'Major Bleed (\d+) \([\d.]+\) (\d+) \([\d.]+\)', table13)
    population = one(r'Table 13: Patients with Adjudicated Major Bleeds[^\n]*\n\(Patients Received at least One Dose of Treatment\)', table13)[0]
    if [int(row[i].split()[0]) for i in (2, 5)] != [int(v) for v in corroboration.groups()]:
        raise ValueError('REFUSED Table12/Table13 patient count disagreement')
    prefix = f'# EXCERPT PLATO FDA Clinical Review; US-government work.\n# held PDF: {PDF} sha256 {SHA}\n'
    prefix += '# population corroboration (verbatim Table13 caption):\n'+'\n'.join('# '+line for line in population.splitlines())+'\n'
    bleeding = (prefix+'# Table 12 PDF page '+re.findall(r'=== PAGE (\d+) ===',text[:b.start()])[-1]+'; patient-unit corroboration: '+corroboration[0]+'\n'
                '=== TABLES (excerpt) ===\nTABLE '+b[1]+'\n'
                f'Outcome | Ticagrelor bleeding events | Ticagrelor patients N={ns[1]} | Ticagrelor KM% one year | Clopidogrel bleeding events | Clopidogrel patients N={ns[2]} | Clopidogrel KM% one year | Hazard ratio (95% CI)\n'
                +'Primary safety\nTotal Major | '+' | '.join(row.groups())+'\n')
    d = one(r'(Table 23: Dyspnea AEs, SAEs, AE leading to discontinuation in all patients and in patients\s+who had baseline asthma or COPD)\s+(.*?)\n\s*vi\) Onset of Dyspnea', text, re.S)
    all_subjects = d[2].split('Subjects with baseline asthma or COPD')[0]
    compact = re.sub(r'\s+', '', all_subjects)
    # The PDF text splits digits/words. Remove whitespace only inside this bounded table.
    denominators = one(r'N(\d+)adverseevent', compact)
    if denominators[1] != ''.join(ns.groups()):
        raise ValueError('REFUSED Table23 denominators differ from explicit Table12 arms')
    cnt = r'(\d+\([\d.]+%\))'
    ae = one(r'(?<!serious)adverseevent'+cnt+cnt+r'([\d.]+)(?=serious)',compact)
    sae = one(r'seriousadverseevent'+cnt+cnt+r'([\d.]+)(?=adverse)',compact)
    stop = one(r'adverseevent,drugstopped'+cnt+cnt+r'([\d.]+)$',compact)
    foot = one(r'\* Preferred Terms:.*?painful respiration\.',d[2],re.S)[0]
    onset = text[d.end():].split('=== PAGE', 1)[0]
    hr = one(r'The analysis of the time to first event showed.*?\[HR [\d.]+ \(95% CI [\d.]+, [\d.]+\)\]\.',onset,re.S)
    page = re.findall(r'=== PAGE (\d+) ===', text[:d.end()])[-1]
    dyspnea = (prefix+'# HR prose (verbatim), PDF page '+page+':\n'
               +'\n'.join('# '+line for line in hr[0].splitlines())+'\n'
               '# HR definition binding: UNRESOLVED; adjacent onset prose does not explicitly identify the seven-term grouped definition. Never pair it with Table23 counts.\n'
               '# footnote (verbatim): '+foot.replace('\n','\n# ')+'\n'
               '=== TABLES (excerpt) ===\nTABLE '+re.sub(r'\s+',' ',d[1])+'\n'
               f'Outcome | Ticagrelor patients N={ns[1]} | Clopidogrel patients N={ns[2]} | RR (rounded; no CI)\n'
               'All subjects; grouped preferred terms\nDyspnea adverse event | '+' | '.join(ae.groups())+'\n'
               'Dyspnea serious adverse event | '+' | '.join(sae.groups())+'\n'
               'Dyspnea adverse event leading to discontinuation (drug stopped) | '+' | '.join(stop.groups())+'\n')
    return {OUTPUTS[0]:bleeding.encode('utf-8'),OUTPUTS[1]:dyspnea.encode('utf-8')}


if __name__ == '__main__':
    for name, content in render().items():
        (ROOT/name).write_bytes(content)
        print(name)
