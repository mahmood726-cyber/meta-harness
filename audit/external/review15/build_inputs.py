from pathlib import Path
import json

out = Path(__file__).resolve().parent
inputs = {
  'schema_version': 1,
  'audit_date': '2026-10-10',
  'repository': 'mahmood726-cyber/meta-harness',
  'ref': '0730234d0b4f',
  'slug': 'semaglutide-obesity-mace',
  'review_sha256': 'b3e40a3d206ff265345fd40a0e0a37136e86912150d7779a0b2ad3311acd4de0',
  'input_origin': 'Manual transcription of the pinned rendered page and source records. NOT a downloaded review.json, complete original HTML, or live registry JSON.',
  'effects': {
    'mace_reported_hr': {'effect': 0.8, 'lower': 0.72, 'upper': 0.90, 'k': 1, 'pmid': '37952131'},
    'mace_counts': {'events_t': 569, 'n_t': 8803, 'events_c': 701, 'n_c': 8801},
    'discontinuation_counts': {'events_t': 1461, 'n_t': 8803, 'events_c': 718, 'n_c': 8801},
    'discontinuation_rendered_3dp': {'rr': 2.034, 'lower': 1.870, 'upper': 2.213}
  },
  'passages': [
    {'label': 'SELECT primary MACE', 'text': 'A primary cardiovascular end-point event occurred in 569 of the 8803 patients (6.5%) in the semaglutide group and in 701 of the 8801 patients (8.0%) in the placebo group (hazard ratio, 0.80; 95% confidence interval, 0.72 to 0.90; P<0.001).', 'expected_sha256': 'e96b4b80d83de47c004d7f974116e8894840bd882e99cac4dc5364c2307dd1a8'},
    {'label': 'SELECT permanent discontinuation due to AEs', 'text': 'Adverse events leading to permanent discontinuation of the trial product occurred in 1461 patients (16.6%) in the semaglutide group and 718 patients (8.2%) in the placebo group (P<0.001).', 'expected_sha256': 'f5b2c8143b3b21bf5550a7c9f7d7ea15f9c5e0c38455dbac9336ac0b344138c8'}
  ],
  'population_positive_terms': [
    'cardiovascular outcomes in obesity without diabetes', 'obesity without diabetes',
    'overweight or obesity and established cardiovascular disease',
    'cardiovascular disease and overweight or obesity',
    'heart disease and stroke in patients with overweight or obesity', 'cardiovascular diseases'
  ],
  'titles': {
    'primary': 'Semaglutide and Cardiovascular Outcomes in Obesity without Diabetes.',
    'companion': 'Semaglutide and Cardiovascular Outcomes by Baseline HbA1c and Change in HbA1c in People With Overweight or Obesity but Without Diabetes in SELECT.'
  },
  'family_fixture': [
    {'nct': 'NCT01720446', 'name': 'SUSTAIN-6', 'family_state': 'UNKNOWN', 'record_state': 'exclude', 'record_rule': 'X2'},
    {'nct': 'NCT03574597', 'name': 'SELECT', 'family_state': 'UNKNOWN', 'record_state': 'include', 'record_rule': 'INCLUDE'},
    {'nct': 'NCT07417618', 'name': 'INTERCEPT', 'family_state': 'UNKNOWN', 'record_state': 'exclude', 'record_rule': 'X1'},
    {'nct': 'NCT07619508', 'name': '', 'family_state': 'UNKNOWN', 'record_state': 'exclude', 'record_rule': 'X1'}
  ],
  'local_adjudication_only': {'NCT03574597': 'ELIGIBLE', 'NCT01720446': 'INELIGIBLE'},
  'rendered_record_ids': '''37952131 42670242 42677221 42339050 42653733 42403733 42536519 42644855 42437874 42163419 42443711 42603234 42403263 42654433 42555627 42580680 42118699 42337824 42427356 42452586 42100257 42470502 42304551 42091772 41883191 42590035 42668799 42304554 42382865 42536323 42588312 42225300 42225305 42353331 42158845 42250076 41969188 42046181 42653816 42207966 42429319 38907684 38157134 42074711 42220875 41808133 41969169 42219272 42033283 42410309 42529614 42549049 42195357 42297751 41889157 41693033 41787495 42483679 41365841 41968220 42608657 42348164 27633186 39345822 NCT07619508 NCT07417618'''.split(),
  'unresolved_report_candidate_count': 37,
  'companion_pmid': '38907684',
  'safety_report_pmid': '39948761'
}
(out / 'inputs.json').write_text(json.dumps(inputs, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
