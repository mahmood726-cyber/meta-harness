# FINAL signing list: result-change notices for V1

**Mahmood: 32 to sign, 8 to hold, 1 need your ruling.** Nothing here is signed. A lane
cannot sign these notices, and the delegated bulk acceptance does not cover them.

## Run it on your laptop, in the clone `C:\mh-sign-v1`
In Windows PowerShell, once:
```
git clone --filter=blob:none --no-checkout --branch nr/v1-sign-DRYRUN-1fa77f2c4852 https://github.com/mahmood726-cyber/meta-harness.git C:\mh-sign-v1
cd C:\mh-sign-v1
git sparse-checkout set --no-cone '/*' '!/*/' '/harness/' '/scripts/' '/tests/' '/registry/' '/topics/' '/protocols/' '/docs/result_changes.json' '/docs/reviews/*/review.json' '/docs/reviews/*/index.html' '/cache/spironolactone-hfref-mortality/records.json' '/signatures/'
git checkout nr/v1-sign-DRYRUN-1fa77f2c4852
git switch -c sign/mahmood-v1
python -m pip install -r requirements.txt
```
For each notice:
1. Read it: `python scripts/sign_walk.py --notice ID`
2. If you accept it, run its one-line command exactly as written below. It asks for your own account of what you
   read. It refuses, and writes nothing, if the notice's hash or version anchor has moved.

When you have finished, push once:
```
git add docs/result_changes.json
git commit -m "Countersign V1 result-change notices (Mahmood, laptop clone C:\mh-sign-v1)"
git push -u origin sign/mahmood-v1
```
Then say "pushed". Lane NR checks every signature from the pushed bytes.

## A. Sign (32)

**N04**: colchicine secondary cv prevention, *Gastrointestinal adverse effects*
- Served now: RR 5.38 (1.60 to 18.10), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because no trial-registry record is linked to it (PMID 34876021).
- Hash: `1bb44d92ecc82e639f8ec3f39ba4624cfc9b60556b76e061574deda42a98ec4e`
- Version anchor: judgement `B3-N04`
```
python scripts/countersign_result_change.py sign 'colchicine-secondary-cv-prevention' 'Gastrointestinal adverse effects' --notice-index 16 --expect-digest 1bb44d92ecc82e639f8ec3f39ba4624cfc9b60556b76e061574deda42a98ec4e --by 'Mahmood' --judgement B3-N04 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

