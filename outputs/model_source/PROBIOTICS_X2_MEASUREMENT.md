# Probiotics X2: measured, not changed (2026-09-24)

Deterministic simulation with the harness's own `harness.screen.screen_record` on the committed probiotics records
(script: `scripts/measure_probiotics_prevention_flag.py`). Setting the topic's existing `prevention` flag (which makes
the population check read the abstract) would move 15 exclusions to INCLUDE and 9 includes to X2 -- the second
because the topic's VETO list ("model", "in vitro", "subgroup analysis", "acute diarrhea", ...) then fires on
incidental abstract words ("Cox model"). A two-sided rule -- positive population terms from the abstract, vetoes
from title/conditions only -- is the likely shape of a fix. It changes a served pool: Mahmood's decision.

```
served decisions Counter({'exclude': 411, 'include': 57})
rule outcome changes with prevention=True: {('X2', 'INCLUDE'): 15, ('INCLUDE', 'X2'): 9, ('X2', 'X3'): 3, ('X3', 'X2'): 1}
records that would become INCLUDE: 15
   ('41707673', 'Effects of a Bacillus subtilis HU58 and Heyndrickxia faecalis SC208 spore-forming probioti')
   ('40727106', 'The role of probiotic supplementation in reducing Helicobacter pylori recurrence after cla')
   ('36742013', 'The efficacy and safety of Saccharomyces boulardii in addition to antofloxacin-based bismu')
   ('36289153', 'Health economic evaluation alongside the Probiotics to Prevent Severe Pneumonia and Endotr')
   ('34444974', 'Bifidobacterium animalis subsp. lactis BB-12 Protects against Antibiotic-Induced Functiona')
   ('32283645', 'Fecal Recovery of Probiotics Administered as a Multi-Strain Formulation during Antibiotic ')
   ('30694338', 'Saccharomyces boulardii CNCM I-745 plus sequential therapy for Helicobacter pylori infecti')
   ('25588782', 'Can probiotic yogurt prevent diarrhoea in children on antibiotics? A double-blind, randomi')
   ('24309198', 'A high-dose preparation of lactobacilli and bifidobacteria in the prevention of antibiotic')
   ('24291194', 'Probiotics reduce symptoms of antibiotic use in a hospital setting: a randomized dose resp')
   ('10634221', 'The effect of probiotics on Clostridium difficile diarrhea.')
   ('19727002', 'Intake of Lactobacillus plantarum reduces certain gastrointestinal symptoms during treatme')
   ('17900321', 'The effect of a multispecies probiotic on the intestinal microbiota and bowel movements in')
   ('17604300', 'Use of probiotic Lactobacillus preparation to prevent diarrhoea associated with antibiotic')
   ('111546', 'Prophylaxis against ampicillin-associated diarrhea with a lactobacillus preparation.')
records that would DROP from include:
   40716758 X2 | wrong population: title/conditions mention 'model'.
   40548185 X2 | wrong population: title/conditions mention 'in vitro'.
   38258024 X2 | wrong population: title/conditions mention 'acute diarrhea'.
   24772726 X2 | wrong population: title/conditions mention 'subgroup analysis'.
   18949181 X2 | wrong population: title/conditions mention 'acute diarrhea'.
   16572062 X2 | wrong population: title/conditions mention 'treatment of antibiotic-associated'.
   11560298 X2 | wrong population: title/conditions mention 'subgroup analysis'.
   7872284 X2 | wrong population: title/conditions mention 'model'.
   21165295 X2 | wrong population: title/conditions mention 'treatment of AAD'.
```
