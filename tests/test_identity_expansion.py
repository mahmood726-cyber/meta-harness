"""Two identity classes (5 Oct), typed and recorded:
  ACRONYM EXPANSION  a comparator label that is an acronym + year ('RALES1999', 'EPHESUS2003') names a trial whose own
                     paper never prints the acronym, but whose TITLE or study-group CollectiveName SPELLS IT OUT
                     ('...Randomized Aldactone Evaluation Study Investigators'; 'Eplerenone Post-Acute Myocardial
                     Infarction Heart Failure Efficacy and Survival Study Investigators'). In order, from word starts,
                     words may be skipped; exactly one candidate or nothing.
  COMMENT ON         a resolved PMID that is only a Letter / Comment ('Isreb (19)' = PMID 31509682, a letter on
                     CREDENCE) is the article it comments on when PubMed links exactly one (CommentOn 30990260)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
import g1_identity_chain as ic  # noqa: E402


def test_a_title_or_study_group_that_spells_the_acronym_out():
    assert ic.spells_out("RALES", "The effect of spironolactone on morbidity and mortality in patients with severe heart "
                                  "failure. Randomized Aldactone Evaluation Study Investigators.")
    assert ic.spells_out("EPHESUS", "Eplerenone Post-Acute Myocardial Infarction Heart Failure Efficacy and Survival "
                                    "Study Investigators")


def test_a_title_that_merely_contains_the_letters_does_not():
    assert not ic.spells_out("RALES", "Aldosterone receptor antagonism: renal and left-ventricular effects in severe disease")
    assert not ic.spells_out("EPHESUS", "Eplerenone in heart failure with preserved ejection fraction")
    assert not ic.spells_out("SCORED", "Sotagliflozin in patients with diabetes and chronic kidney disease")


def test_expansion_resolves_only_a_unique_candidate():
    titles = {"10471456": ("The effect of spironolactone ... Randomized Aldactone Evaluation Study Investigators.", ""),
              "10488324": ("Spironolactone and potassium in heart failure", ""),
              "12668699": ("Eplerenone, a selective aldosterone blocker, in patients with left ventricular dysfunction "
                           "after myocardial infarction.",
                           "Eplerenone Post-Acute Myocardial Infarction Heart Failure Efficacy and Survival Study Investigators")}
    assert ic.expansion_hits("RALES", titles) == ["10471456"]
    assert ic.expansion_hits("EPHESUS", titles) == ["12668699"]
    dup = dict(titles, x=("A second Randomized Aldactone Evaluation Study report", ""))
    assert len(ic.expansion_hits("RALES", dup)) == 2                  # two -> the caller refuses (AMBIGUOUS)


def test_a_letter_resolves_to_the_one_article_it_comments_on():
    rec = {"pubtypes": ["Letter", "Comment"], "comment_on": ["30990260"]}
    assert ic.comment_target(rec) == "30990260"
    assert ic.comment_target({"pubtypes": ["Journal Article", "Randomized Controlled Trial"], "comment_on": ["1"]}) is None
    assert ic.comment_target({"pubtypes": ["Letter"], "comment_on": ["1", "2"]}) is None
