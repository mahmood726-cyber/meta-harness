"""Plant (6 Oct, forest lane): EMA discovery took only a product's INITIAL EPAR (assessment report + scientific
discussion). A new indication lives in a VARIATION assessment report (tocilizumab's COVID-19 extension:
RoActemra-H-C-955-II-0101, Dec 2021), which was never held. EMA's own documents index lists every assessment /
variation / extension report by medicine name: discovery by product, never a hand list of documents."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import k_gap_regulatory_probe as rp  # noqa: E402

INDEX = [
    {"type": "variation-report", "medicine_name": "RoActemra", "name": "RoActemra-H-C-955-II-0101 : EPAR - Assessment Report - Variation",
     "document_url": "https://www.ema.europa.eu/en/documents/variation-report/roactemra-h-c-955-ii-0101-epar-assessment-report-variation_en.pdf"},
    {"type": "assessment-report", "medicine_name": "RoActemra", "name": "RoActemra : EPAR - Public assessment report",
     "document_url": "https://www.ema.europa.eu/en/documents/assessment-report/roactemra-epar-public-assessment-report_en.pdf"},
    {"type": "product-information", "medicine_name": "RoActemra", "name": "RoActemra : EPAR - Product Information",
     "document_url": "https://www.ema.europa.eu/en/documents/product-information/roactemra-epar-product-information_en.pdf"},
    {"type": "variation-report", "medicine_name": "Tyenne", "name": "Tyenne-H-C-x : EPAR - Assessment Report",
     "document_url": "https://www.ema.europa.eu/en/documents/variation-report/tyenne-x_en.pdf"},
    {"type": "press-release", "medicine_name": "", "name": "RoActemra recommended for COVID-19",
     "document_url": "https://www.ema.europa.eu/en/documents/press-release/x_en.pdf"}]


def test_index_docs_take_every_assessment_variation_report_of_the_product_only():
    got = rp.ema_index_docs(["RoActemra"], INDEX)
    assert got == ["https://www.ema.europa.eu/en/documents/assessment-report/roactemra-epar-public-assessment-report_en.pdf",
                   "https://www.ema.europa.eu/en/documents/variation-report/roactemra-h-c-955-ii-0101-epar-assessment-report-variation_en.pdf"]


def test_index_docs_match_the_medicine_name_exactly_not_by_substring():
    assert rp.ema_index_docs(["Tyenne"], INDEX) == ["https://www.ema.europa.eu/en/documents/variation-report/tyenne-x_en.pdf"]
    assert rp.ema_index_docs(["Roact"], INDEX) == []
