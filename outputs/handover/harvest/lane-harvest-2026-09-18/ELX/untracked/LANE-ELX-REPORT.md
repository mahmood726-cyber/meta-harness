# LANE ELX report

MEASURED base HEAD: `237e90946f5b257265b0a3b1c986a8907d12eded`.
No commit, reset, checkout, stash, push, or network retrieval performed. This is a local increment, not a release or certification.

MEASURED: 3 of 3 original plants failed before copying inputs or changing implementation. The held-source plant identified ELIXA and FREEDOM-CVO. Contrary to the lane description, the baseline manifest did not yet list FLOW; its PDF was committed, but its trial association arrived with the incoming manifest. After repair, 5 of 5 plants pass, including two added state/admission checks. Original assertions were retained; exact page assertions were added. Evidence: `.tmp/elx/prefix_pytest.txt`, `.tmp/elx/postfix_pytest.txt`.

MEASURED: 32 of 32 pages rebuilt using the existing build function with date 2026-09-11; all caches preflighted and the fetch runner replaced with a refusal during the corpus rebuild. GLP1 was also rebuilt with the requested CLI. Retraction survival: 32 of 32. Targeted suite: 181 passed, 798 deselected on the final targeted run; full verifier results below. `git diff --check`: PASS.

| Item | Static input/constant | Dynamic computation/validation |
|---|---|---|
| State vocabulary | Named codes and display labels | State from held document, extraction, conflict and proposal records |
| Regulatory evidence | Two copied handover JSON inputs, unchanged | HEAD PDF bytes and working bytes hashed; text digest checked; eight ELIXA spans located at recorded offsets |
| Membership demonstration | Proposed extraction from ADJ-GLP1-005 | Production synth.pool on original rows and original rows plus proposed ELIXA; no typed research output |
| Report audit | Base revision | Field-by-field JSON comparison, manifest hashes, marker inventory |

MEASURED source custody: 3 of 4 document digests verified against `git show HEAD:<path>` binary output (Python hashlib, avoiding shell pipeline encoding). The fourth is explicitly off-tree, has no committed path, and is REFUSED as held evidence; no numeric fact is consumed from it. Zero digest mismatches among the three committed documents. The copied manifest is retained verbatim, including that off-tree disclosure.

```json
[
  {
    "source": "FDA_NDA208471_StatR_2016",
    "path": "outputs/handover/glp1_regulatory/held/208471Orig1s000StatR.pdf",
    "expected": "cf2b3ef92247b85e7be7c3b56c3cc4fc0af007b3950acee95eea9c995653db38",
    "actual": "cf2b3ef92247b85e7be7c3b56c3cc4fc0af007b3950acee95eea9c995653db38",
    "state": "MATCH"
  },
  {
    "source": "FDA_NDA208471_MedR_2016",
    "path": null,
    "expected": "80d91f3cdaea588b845de18d3ef9b254936ec8768305bd91e554d9de3f39acc3",
    "actual": null,
    "state": "REFUSED_NO_COMMITTED_DOCUMENT"
  },
  {
    "source": "FDA_NDA209053_EMDAC_briefing_2023",
    "path": "outputs/handover/glp1_regulatory/held/fda_media_172242_ITCA650.pdf",
    "expected": "719362393b2029c2d4a081ab1bc69647034b2168efe686808d419f16177f0103",
    "actual": "719362393b2029c2d4a081ab1bc69647034b2168efe686808d419f16177f0103",
    "state": "MATCH"
  },
  {
    "source": "FDA_NDA209637_s025_label_2025",
    "path": "outputs/handover/glp1_regulatory/held/209637s025lbl.pdf",
    "expected": "547606a71cf2cee768b1f98848be7ed53c06ea640bc6968f485c0fa3da455c42",
    "actual": "547606a71cf2cee768b1f98848be7ed53c06ea640bc6968f485c0fa3da455c42",
    "state": "MATCH"
  }
]
```

| Trial | Before | After | Deriving evidence |
|---|---|---|---|
| FLOW | NOT_IN_COMMITTED_SOURCE | EXTRACTED_NOT_ADMISSIBLE | `outputs/handover/glp1_regulatory/held/209637s025lbl.pdf`; `547606a71cf2cee768b1f98848be7ed53c06ea640bc6968f485c0fa3da455c42`; 1 displayed spans; ADJ-GLP1-003 PROPOSED, not countersigned |
| FREEDOM-CVO | NOT_IN_COMMITTED_SOURCE | EXTRACTED_NOT_ADMISSIBLE | `outputs/handover/glp1_regulatory/held/fda_media_172242_ITCA650.pdf`; `719362393b2029c2d4a081ab1bc69647034b2168efe686808d419f16177f0103`; 1 displayed spans; ADJ-GLP1-001 PROPOSED, not countersigned |
| ELIXA | NOT_IN_COMMITTED_SOURCE | EXTRACTED_SOURCE_CONFLICT | `outputs/handover/glp1_regulatory/held/208471Orig1s000StatR.pdf`; `cf2b3ef92247b85e7be7c3b56c3cc4fc0af007b3950acee95eea9c995653db38`; 8 displayed spans; ADJ-GLP1-005 PROPOSED, not countersigned |

ELIXA: all eight supplied spans are preserved verbatim (including line breaks) and shown with PDF page numbers: definition/text/Table 8 page 24; executive summary page 7; Table 6 page 22; 4-point text page 35; unrounded 4-point text page 8. Endpoint identity uses the 3-component definition, not the interval fingerprint. Raw text digests are checked before universal-newline normalization used by the handover character offsets.

FLOW: Table 10 is verbatim-located on PDF page 25; reported counts 212/1767 versus 254/1766 are displayed. ADJ-GLP1-003 remains PROPOSED. FREEDOM-CVO: the held FDA briefing supports an extraction record, not an absence-of-source state. Its older pipe-separated table span is displayed explicitly as a transcription, not falsely marked verbatim-located. No proposed row is admitted to the primary pool.

MEASURED primary result object: unchanged in full, including k=8 and estimate 0.856. The manuscript tab text is unchanged from base. No demonstration numeral was added to the headline paragraph. Demonstration numbers live in the audit panel.

| Production pooling metric | Primary | Primary + proposed ELIXA |
|---|---:|---:|
| k | 8 | 9 |
| estimate | 0.8559934175939847 | 0.8630296800888738 |
| ci_low | 0.8086248326603205 | 0.8017603465739591 |
| ci_high | 0.9061368157018077 | 0.928981124967119 |
| tau2 | 4.4479725147539284e-05 | 0.0036135823281711055 |
| Q | 7.060721196954362 | 12.50666490235264 |
| i2 | 0.8599857615190106 | 36.03410611493146 |
| pi_low | 0.8068929729560542 | 0.7376595536079333 |
| pi_high | 0.9080816855795524 | 1.0097072898620336 |

DEMONSTRATION: HETEROGENEITY_MEMBERSHIP_SENSITIVE, under the PROPOSED adjudication—not a result. Paule-Mandel tau², HKSJ t with k-1 df, log scale, same production function as primary. I² is percent. INFERRED from these computations: the near-zero primary heterogeneity is membership-sensitive and the proposed prediction interval crosses the null.

Implementation ownership: existing invalidation.py owns state codes/reasons; claimgraph.py now owns regulatory_fact and digest/span validation; page.py renders evidence and demonstration; synth.py computes both demonstration pools. This base has no harness/envelope.py and had no regulatory_fact function. Existing known_missing.py already assembles this panel, so it was extended as the actual owner; no new production module/framework was added.

MEASURED page movement: 1 of 32 canonical review_sha256 values changed (GLP1); 32 of 32 html_sha256 values changed. In the other 31 review files, exactly three field values changed, all under reproduction/certificate: synth.py blob hash, analysis_code_sha256, release_sha256. Their clinical/review cores are unchanged; rendered certificate hashes explain their HTML changes. Dictionary key-order-only changes in serialized JSON do not alter canonical review hashes. Full before/after field diffs follow. GLP1 additionally changes held evidence, missing states, dependent limitation/gate text and its audit panel; the primary pool and manuscript are unchanged. The index reflects revised invalidation reason counts; the GLP1 neutral page reflects the audit panel; blind_map.json points to the last GLP1 CLI build.

| Page | review_sha256 before → after | html_sha256 before → after |
|---|---|---|
| balanced-crystalloids-vs-saline-mortality | `0aaed1d0eb59e7893f7ea1fd148569c97ca24f46a6d16b63f1666f330d106426` → `0aaed1d0eb59e7893f7ea1fd148569c97ca24f46a6d16b63f1666f330d106426` | `d4e947e81e3ad9cfe7c56cd8acf515974722377f62c645988329d94e36a3469e` → `e931680bcc1f89478e48aa7e01a0c2d054613caa4a48e3cd292dc985eb4a4229` |
| colchicine-postop-af | `6d2f3c808b0d6e9c0c7e1e998130a9ca66d13719e21895c616112680cdc8ba7d` → `6d2f3c808b0d6e9c0c7e1e998130a9ca66d13719e21895c616112680cdc8ba7d` | `b6b95235b3029f1dde4b95b6ac70f2fc7a550e033ee0226594f133d3e5f863ed` → `995170f3b0dbde1ca4e7c796a6d0cd9a577ee27df7b0f2b71884db88f12e1b35` |
| colchicine-recurrent-pericarditis | `85c18ac1dd0672146c4e77f28346f9569673947882ba837ec7d785bab7d9b72d` → `85c18ac1dd0672146c4e77f28346f9569673947882ba837ec7d785bab7d9b72d` | `a1a1f55b0ae87089d8c0c44ef0aa90601674cf584b9951f2a3921c349a3ec740` → `0ff3c93f256da31dd5c68d37543c1e5c3a368b4a3df42a9cbf75387d9504b933` |
| colchicine-secondary-cv-prevention | `7a6f8eb56cc435ba1f6ad11a489d662a7e71e86066077e0d359adbd44ac4c74f` → `7a6f8eb56cc435ba1f6ad11a489d662a7e71e86066077e0d359adbd44ac4c74f` | `c4c98addb52e1f3a58dd84d6f0410a50d3f8593f263e4e0917d4db33b1f48970` → `3f1f9754af70753e1a79fcc76ccc2e26fdddea970ce3a0d8f43f0e1f82898a0e` |
| corticosteroids-cap-mortality | `03e9b2b1a1e7f1b2c7aeb83d86d67a78893d90335cd184933f25f51f37e8c63f` → `03e9b2b1a1e7f1b2c7aeb83d86d67a78893d90335cd184933f25f51f37e8c63f` | `0b95d2e1fc71bb2fbfe9d8a5a134e492eda13ca1c207b105ccedb669e0ada306` → `2f18b61e1ea027e5404538c6cfb6f5d92af557a9d35319facd10f91fddfdbdf3` |
| corticosteroids-covid19-mortality | `808ce59607f55828abb8698fb4f59547cf9fb099c2495bc6264c9a4146c7248e` → `808ce59607f55828abb8698fb4f59547cf9fb099c2495bc6264c9a4146c7248e` | `707716c45a628cf699827cb81cdcf7228d478c8a04191c47d2ec0bef5c26819e` → `fb635d77b35924ec50a824f4cf520417649c955dcfac6824af9281a85899fa65` |
| dapagliflozin-hfpef-hosp | `4f2385c6daeff06712d3d2512a518a86061e60e0fc0bad160f3764e3cf3f90ff` → `4f2385c6daeff06712d3d2512a518a86061e60e0fc0bad160f3764e3cf3f90ff` | `5a56319b931341c8451034b28999834b6c2fed20b1b682e36b820a4351297313` → `7695d855710006944a22361712d7cd68fd029c5ff9d10aec042b1edd90db10b1` |
| denosumab-vertebral-fracture | `b9268f9ade0d17de0d808d57236d3f876e95b5efa84f3416c621c504ba04f592` → `b9268f9ade0d17de0d808d57236d3f876e95b5efa84f3416c621c504ba04f592` | `a8aa3cebd19caeb34be65424e78c3b67c6928ad4c6578e7a38db2b6eba975799` → `cbcef4b891848b59ce19e802e409651c22f7cd9a16a3d2b9522fe8e7a3c5cbfa` |
| doac-vte-recurrence | `4de6d31eb9e95168f357b2ba06d0fc7a83f5cc03583a8ce51aed1f856790701a` → `4de6d31eb9e95168f357b2ba06d0fc7a83f5cc03583a8ce51aed1f856790701a` | `cc0974e73a449e19810368c9541bbe05d4ee1563fc39696dbbad055a6da0e82d` → `bc315b6b64081c53e2ef1ca208edf9ae51c4cf38a184c60ee3777203cb00512b` |
| dpp4-mace-t2d | `d8c52fa18d2dc06e1b1cd68f2628689785969ee01a6ff2ca3c401f4b6e41ab70` → `d8c52fa18d2dc06e1b1cd68f2628689785969ee01a6ff2ca3c401f4b6e41ab70` | `7b9c4122207eb540d562c1bd679aaf1de662f5096fcee52f617bea9e41d4a136` → `798ca0a019020b12875c089d6492e711f336e5f0c902f5f6ad78805d497ba987` |
| empagliflozin-hfpef-hosp | `2f24c905416e8e6adf13241a0027d60a77a6db5c16e53d79b72083957acb388b` → `2f24c905416e8e6adf13241a0027d60a77a6db5c16e53d79b72083957acb388b` | `60754993ab682f7785bbd4cd94a49da72abfd5706216745961175f483e5dd8db` → `479c7179addbf6c18032b55caeb67d369537d0a0bdb4b935748cc229ef151a99` |
| esketamine-trd-madrs | `3f8e48acfe109814a1f3bb23909c45125d4c56ca0e18a4ac356897c393b384c9` → `3f8e48acfe109814a1f3bb23909c45125d4c56ca0e18a4ac356897c393b384c9` | `0e39237e3abb24dcf5a733b8c946ee0098fa3377957267b3d1579061b8892df5` → `8a0ee39881925f0374f59bc3b05dbb05be4fbe2eee3836484f6484af75bdefb5` |
| finerenone-ckd-t2d-renal | `51dd05507f17bff490f4590386e1a50e161efd1f20ae0be12cc32758d526f937` → `51dd05507f17bff490f4590386e1a50e161efd1f20ae0be12cc32758d526f937` | `d4103e09280b20b4fc1f690e6623c3583b77f4ec446e492d5ad1c364fd2e9d0f` → `f5c40b936daf62c288532d1ad4a9e94261b4ebd1fbc1e46da6daf8dac019ea50` |
| glp1-ra-mace-t2d | `98726cc125e9fcc749601459bce442a9b581ef4cce81c60cf891fa6d643917f7` → `82dcaa63d775564a94577ff9dc150f09e09504903002157534d032bae2e94c8a` | `fede8d293caffb87dfc915f1540baad49ce59c0f67b03ec688cfd0555bbc6725` → `41aa39b3dc744f91d46bfd43ffc74571eb6dc97832ea3ce9d0216e3a982471a2` |
| iv-iron-hfref-hosp | `57765213e53cd302e967f18500e96b9f3b0b5f67cad16c9fefaa459d254fa0e3` → `57765213e53cd302e967f18500e96b9f3b0b5f67cad16c9fefaa459d254fa0e3` | `23f8ab80aa0a7057083a3ee3c070ca7b07915f8cb5a8a3c967fed2881b631b10` → `87934683a9a2667a830a119ee4cbda85d5aeb3f059ee873c4f7ed08b37b65433` |
| melatonin-primary-insomnia-sol | `d12d22bde7323098e856f4d444bf518fa2186b69f17de26f503ea8254cd47809` → `d12d22bde7323098e856f4d444bf518fa2186b69f17de26f503ea8254cd47809` | `405f596be9b95798cb2e29d3209491075614b8829549e3e087e570ff91c3d380` → `5dde3a733476d3b9e9c1c1414ec786f2f7e8a8f0491551389b196e625e033006` |
| metformin-pcos-ovulation | `892696356460e12563c0503a07f2d9f5d5aba44c7757661a383456c10a6c3b39` → `892696356460e12563c0503a07f2d9f5d5aba44c7757661a383456c10a6c3b39` | `6299ac45fdfd0b895f4a04e306ae3f52540c7abff314b18f965861bbf390d987` → `0e67dbabeca7f87576bdd76096f09809837124255a9ef666c9503c05e2274547` |
| noac-vs-warfarin-af-stroke | `91da662722bdb1f494cfe525adaf5ce7b0f27e7fc99e7370ea84d973e98da806` → `91da662722bdb1f494cfe525adaf5ce7b0f27e7fc99e7370ea84d973e98da806` | `049daa176b7eef7fe37a14bb48b9f7d08d7c1e869f56a34b794e42b5f9b4eb99` → `19d5b062b99224bdf7fab7c8859d820a7fa4b6c58672794671427220c1be0e3c` |
| omega3-cardiovascular-events | `954eb7b368fde760fb78a74044f05edcef6a1abb1f3b68f072b5d73ec5bfadcb` → `954eb7b368fde760fb78a74044f05edcef6a1abb1f3b68f072b5d73ec5bfadcb` | `d78334a7b66abbeb77e2aff0bc776b473e2d1abc30be469d1a7428be76c85654` → `2e36d3c7fe0b1dd23c1b2561f10b492c1b88f199de121938085a55ace30b2f9a` |
| pcsk9-mace | `e24c35bdbab85138918f26b26e5c1e20c2112fb0ad5749c72d452e651ea2f5a9` → `e24c35bdbab85138918f26b26e5c1e20c2112fb0ad5749c72d452e651ea2f5a9` | `5dfc513eb1a4f305dbed61c42f757adf88b6430729891316f1e718f8498dbd10` → `1ff4e69c9b5c2ec764a914351fa3123c6ce583ad423072a6402135251345dc28` |
| probiotics-aad-prevention | `9932877c8d3c3b6813bb9a21068e7176f0bdace65d3fd09403689f5a10eac904` → `9932877c8d3c3b6813bb9a21068e7176f0bdace65d3fd09403689f5a10eac904` | `48663f2df53794bef8a0ea4a49f498b0f5b6336977efc485eb8be2788ad00354` → `2105dacb1e79ff0ae9292ef9f70557e26ba66ad3caf51540debc4d464d9a475b` |
| sacubitril-valsartan-hfref | `04b07291943df879080bdfd052eaa56560a659a9cba5a849d614ebc95b79a9e1` → `04b07291943df879080bdfd052eaa56560a659a9cba5a849d614ebc95b79a9e1` | `416d34d4a7a3eb5e5c511272bffc30255e06c28d0ad2f25574fa21b5087f71d3` → `f6ab2188230cffa4021a97088acf82c86fd12dc3c4c55aee8d5390e5d3be64be` |
| semaglutide-obesity-mace | `3b2fa682fb561b631f5ffe3b8f011419551cb08a2af324e0cc3773b661c39573` → `3b2fa682fb561b631f5ffe3b8f011419551cb08a2af324e0cc3773b661c39573` | `94360454004db55d07785adc763cda8ebd8ce9a85c2267af4969c6f05804c78e` → `3fbae3d369236d4fe61ba062476b983147c6dae4600ebb92c5c2cb294bef424c` |
| semaglutide-obesity-weight | `2a54c7d191e172be545c701c2d1d8891f71529648280582822eee62f0cc9bc18` → `2a54c7d191e172be545c701c2d1d8891f71529648280582822eee62f0cc9bc18` | `643602d360617584975b73177ed379daab7dd011fd92ce42cf4cff369d269d1d` → `d0a1e3c3be96b4762bc4e144bbe3a154f69732bfb10455a7738cd424a516851d` |
| sglt2-ckd-progression | `2e8806d864a2828ff93306d6bc9a329bf5c4e3b527ab8d9894bc569dd98a61ce` → `2e8806d864a2828ff93306d6bc9a329bf5c4e3b527ab8d9894bc569dd98a61ce` | `65d81b574374e3ffe8b794796426237a2983b7b7b16470bd2e8cb5061659f19d` → `2f725c7a79c98d7ec8247161635b71520c029ef51a5d6f6bce729f8c5120c6e2` |
| sglt2-hfref-hosp-cvdeath | `bbee69a85a3b601474d28332cf436e9d0d021c276b38e739fe081cba70399551` → `bbee69a85a3b601474d28332cf436e9d0d021c276b38e739fe081cba70399551` | `015b07590c7af61408c8666f93bc3e67d0ced7143ebf45bf3a3472c99b67b7a7` → `acb8511e48a2e4d11ef51c72456ac0c85dcd0e3b0cc4babba41c47514346f1a8` |
| sglt2-primary-prevention-hf | `e7fc12147d90a61b79e39b696cc780b62d633b2fcd06b79332b826c90c08f096` → `e7fc12147d90a61b79e39b696cc780b62d633b2fcd06b79332b826c90c08f096` | `c6ec77eaca569506bbb90c6eff02478be742f3adcad5819f7997b349e13f78d0` → `e5953c4cb940f7ee0387c67f47bab5c4642f753f62a50be3407cf5f7d25fb47f` |
| spironolactone-hfref-mortality | `c9fde106b731b623e2be04b1f7af2258b029b0618c75d3fbeb8fbea4135d8ffe` → `c9fde106b731b623e2be04b1f7af2258b029b0618c75d3fbeb8fbea4135d8ffe` | `cf9a076d5818c0d75c62288664f282dd8468ca9b2d9e22353239b78e662e5e59` → `f63f4ea848f30d5c76e12fdef9090ca760dfa673e0f400ff32e5b69d5d5b0837` |
| statins-primary-prevention-elderly | `019f28727ea36026b97c3d77a1f93df21c146637a06902bfbf836e7cd3edc720` → `019f28727ea36026b97c3d77a1f93df21c146637a06902bfbf836e7cd3edc720` | `dd46163874564d1a1b11f2adbe2aac76ef570f6b7801d891f5327e3a9d78a769` → `18e876737f2853a587a5d2043d5a7181b4c6f7fb084bc802cb46987b30806421` |
| ticagrelor-vs-clopidogrel-acs | `759ecb61f51056be428d32ad1bc86868c333b88df1f32288d1388c17060f5492` → `759ecb61f51056be428d32ad1bc86868c333b88df1f32288d1388c17060f5492` | `6eec92054aff2039ccc57d06a273e7285116f5e61ce0b65089ee4db3671fbeb0` → `172adeff25ccad4f18ebc2a1a34a07e7fab05706bbea6faf1744fe7f594f9711` |
| tocilizumab-covid19-mortality | `bc9c2fc12ed92a37f397360318e516699dcf40d408184975a0bcdfb79b8e9071` → `bc9c2fc12ed92a37f397360318e516699dcf40d408184975a0bcdfb79b8e9071` | `476dfa8aec8eeedf068f155f44119d4054a7ecc30f3ca752f4a9a3ccd86a7e78` → `aca11255de5aa56d5270a729851f4f9a984967590507519bcdd91e6afcaf1d13` |
| tranexamic-acid-pph | `1e61ef3c48229b4306a6caa352667870fcb39b1b2c239d28a106e5b371099088` → `1e61ef3c48229b4306a6caa352667870fcb39b1b2c239d28a106e5b371099088` | `5cf38080a31d373f32f9a17bdad56e43ad722464af7ccfd55cb717ff190dfe91` → `a01228c1cdfcaaafc3465f97162e8e31214eff1ada29a2a63e627e77c882ec55` |

MEASURED ratchet: zero marker-count decreases across the 32 review pages. No marker-count acknowledgement is proposed. Three exact-text warning-block replacements require unsigned acknowledgements. They retain STALE and replace the false missing-source explanation with held extraction/adjudication debt (index aggregates these reasons). These are proposals only; docs/ratchet_acknowledgements.json was not changed.

- PROPOSED/UNSIGNED `docs/index.html`, banner `ddddfbfbeadd588f687cd542f07a445cc1f0ba4f5247c3f15121e6b47dff193a` → `abcfbe123135440c19579628f031084e751b1081f2171dce052a1ac341097943`. Reason: held-source state correction; completeness remains stale, no primary numerical change.
- PROPOSED/UNSIGNED `docs/reviews/glp1-ra-mace-t2d/index.html`, absent `4a79ea58597a2d2c097c5b8851faad56e49ad9c0e04244bf9fdac2a824afc094` → `907a0a87c6810684ddfac45e23f6d3e424d5576970e1b682c17e86eaa0e668c5`. Reason: held-source state correction; completeness remains stale, no primary numerical change.
- PROPOSED/UNSIGNED `docs/reviews/glp1-ra-mace-t2d/index.html`, historical-floor absent `74ef9f624c5845659feef24079fb873482531098515959d4a9a1c20473b27570` → `907a0a87c6810684ddfac45e23f6d3e424d5576970e1b682c17e86eaa0e668c5`. Reason: the prior acknowledgement points to an obsolete replacement; the current warning preserves STALE and the search failure, while replacing missing-source wording with held extraction/adjudication debt. This historical floor is checked in addition to base 237e9094.

CLAIMED by handover, not established here: Mahmood acceptance/countersignature; prospective exact-outcome provenance resolution; admission to a conventional strand. This increment does NOT establish countersignatures, FACT binding of the eight pooled rows, CENTRAL search coverage, source completeness, or a release/Overmind PASS. Off-tree medical-review custody and FREEDOM transcription verification remain limitations.

Full verifier ledger:
```text
MEASURED: python scripts/verify_all.py started with RATCHET_BASE=237e9094.
Run stopped through its own exec session at the 20-minute cap (approximately
21:48:58 to 22:08:56 local time). Its capture wrapper did not return the buffered
ledger before interruption. No full-verifier PASS is claimed.

Limb ledger (UNKNOWN means no final verdict was captured):
unit tests (full suite): UNKNOWN; independent final targeted run 181 passed, 798 deselected.
offline reproduction (all live pages): UNKNOWN; 32/32 rebuild completed separately.
publication gate on every live review: UNKNOWN from verifier.
index currency: UNKNOWN from verifier.
served-artefact leak scan: UNKNOWN from verifier.
held-out leak detector: UNKNOWN from verifier.
search completeness: UNKNOWN from verifier.
fix-state discipline: UNKNOWN from verifier.
honest-state ratchet: REFUSED in independent explicit-base audit; three warning-block replacements need acknowledgement; zero review marker-count decreases.
gate scorecard: UNKNOWN from verifier.
gate gaps table: UNKNOWN from verifier.

This optional verifier has no aggregate result: 1 of 11 limb verdicts independently
established (REFUSED), 10 of 11 not reported as passes. No retry of the full verifier.

```

Full-field diffs for every non-GLP1 review object (JSON values, not line diffs):
```json
[
  {
    "slug": "balanced-crystalloids-vs-saline-mortality",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "1fc4bb496a9ec2aeb2c5a2afab157a6bac7e02b0db3c64fc13f526f071a2ba67",
        "after": "d659c158f3f3764380a38b9d55f83ad0bd7b2f9e60495d354e301b4d423fcbf3"
      }
    ]
  },
  {
    "slug": "colchicine-postop-af",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "528d06ea91506c3f4a0df60036afd289b8ba199550a2523a34259adce384f12a",
        "after": "fd1e00aa368471f047fbeb0bb70b64acdb0ecc7f6da03d800d29f941708ada2e"
      }
    ]
  },
  {
    "slug": "colchicine-recurrent-pericarditis",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "a4419f25558867c078f28ccc7e6060bd94ff4cf0c59257e9ab4457ec1e4fc95a",
        "after": "9370778ee461ec3cfa67c40260ce24a9909300663c0a71da9cf20c5cd46f8acb"
      }
    ]
  },
  {
    "slug": "colchicine-secondary-cv-prevention",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "54bc3b30d259f9d46aeabd58157c8dccf202f33868b8100de497b86692a40c67",
        "after": "3cbe6f4351185de171f534ae5e332fa5a642f3786978637a91860be297b76090"
      }
    ]
  },
  {
    "slug": "corticosteroids-cap-mortality",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "6635e3e6ca5ab0802860a514012c3547584816f68ce50262c5983a4d5603be8c",
        "after": "7b2fc0269fd2102c54eeca946d694c06ecc264c6e61b27f3f980d15b6062128f"
      }
    ]
  },
  {
    "slug": "corticosteroids-covid19-mortality",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "dd843eb8a28f8fafc8b469029270a758c79159a5929953b9f18216d6d2e2b408",
        "after": "380870f29409097b350c9086714d4632e054be2c469c58c5e9eab6be01c0d464"
      }
    ]
  },
  {
    "slug": "dapagliflozin-hfpef-hosp",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "e70ec8cb8181760610162b042352310301993e6764b208de807f243504fd87b8",
        "after": "4f35b9626827c894c5b14f265c6b3f44a15550868be57ed337caa3dc67dfeade"
      }
    ]
  },
  {
    "slug": "denosumab-vertebral-fracture",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "6779cda163c4e4de4cfbb17617cb41034efcf8a4c751bc1cad7692bb0efc0ff3",
        "after": "dd1549fab976f094ef330494d65e33c680fc08b96a96172290e1ba1d32815de5"
      }
    ]
  },
  {
    "slug": "doac-vte-recurrence",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "7c5fdb4b7c3f22b3773e318c3db3f40719cafda9272af178754949d607869eea",
        "after": "41f398ca55a3254f69673b521d10eff45302a82aefb7580787b3593f48fb9d13"
      }
    ]
  },
  {
    "slug": "dpp4-mace-t2d",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "19c28388bac82f629d9fe13caef50d1e8b365061a83bd3483f7a72bce5d8ff6f",
        "after": "a953362b2a4423e1725e8a8ff2f2d6fe00bbbb6414f1fcb5febcba0066d33a12"
      }
    ]
  },
  {
    "slug": "empagliflozin-hfpef-hosp",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "abfe303de01c151242bb926ad1faf8b2a4cc592a0f6ea84f626d3903740cf233",
        "after": "6c95b229d51e6e70c91a85dcb79e4e7d6d8db648db555b9ea6dcd812312d907c"
      }
    ]
  },
  {
    "slug": "esketamine-trd-madrs",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "badff899fa3cc12b0529fc78921b27d950965511a3ded96735f69286e9a855d4",
        "after": "7a4f31c915a13291140fe86507cfd0b36c66c71ac7544b0d366175a63ea4ab0d"
      }
    ]
  },
  {
    "slug": "finerenone-ckd-t2d-renal",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "522295c4e131abac403fe8520ce13b63c528a31ae1676257762bff93a7b21f54",
        "after": "b644289451642089352231b72f83912aba803cd5486b7cb657686f969edeec5a"
      }
    ]
  },
  {
    "slug": "iv-iron-hfref-hosp",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "18f7716d71b1030ef22be5daf9c6a88d7177c1f911b65a20c44fcdc211cc7d5b",
        "after": "1eb9458928d45a1d127b41f1bccf0dd89182891625762b68614f3d12e00458fe"
      }
    ]
  },
  {
    "slug": "melatonin-primary-insomnia-sol",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "2bcb2a0f0ee1d4ea4194bd5dec9b001062ff3935ef27336e251ff8dc76b69ea3",
        "after": "fb7bf8754bebbe87f2f68bacc32134f072cfe7834b6ce0e3eb5bdf8ae269b4a7"
      }
    ]
  },
  {
    "slug": "metformin-pcos-ovulation",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "90ac6e7c5a22dd884baff4d81b401786731eb1f523a6ad78e7da05112b726869",
        "after": "48d8d501af6239f9f70c5fa139ac9411c88b35a0bfb252ddc103a500c31866d6"
      }
    ]
  },
  {
    "slug": "noac-vs-warfarin-af-stroke",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "838a39d427d7f1048813605bed6877ca02f74b4ce074e855474c20d32a6379dc",
        "after": "69e7526d24040e0080806b1f26dd9d3a11e1bebe35bdbea4a1cca1ac8bdc22f4"
      }
    ]
  },
  {
    "slug": "omega3-cardiovascular-events",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "a5c5db5aa1651718bf54e2f5f761dde7a089fac3e7126a5adee17e7a53d58f6c",
        "after": "062764879c53af407834128ab319e11a657b035260a5029f33c47696ba963987"
      }
    ]
  },
  {
    "slug": "pcsk9-mace",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "27008f3cecea4bad96563ce5deaa46dc474238796020fdf71d9c3ba6e078d144",
        "after": "aa2d1c9dd964fc2e0427bfc04a2114ba95761dc383ece5fbf3e7128bba6d7726"
      }
    ]
  },
  {
    "slug": "probiotics-aad-prevention",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "74f14fb77425c98ff6784fb57f6dcfe8f1d1b04dddeeaab36585a4295020e162",
        "after": "903f9962308d5f1c9a8ee8bf057191db7c783b77ce4acf2ce0a25abdece87903"
      }
    ]
  },
  {
    "slug": "sacubitril-valsartan-hfref",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "27e200e25ddb54fb68bd58bcbeaa47d0b260f583e21ebce573160dea44a5f868",
        "after": "1c13832093489407efc5f46ec7d64ad86335a0364f3b45743407917c20f0bc50"
      }
    ]
  },
  {
    "slug": "semaglutide-obesity-mace",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "e9b73319d6e144ab0739dadd90b3a8ec9096adb9e70fff10bd597128ee3592c3",
        "after": "8bac516b8b31ee5bcd280c2b390ae3524cead3bbb5c979f13f0a2831f9225e9f"
      }
    ]
  },
  {
    "slug": "semaglutide-obesity-weight",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "5fe65e25486fbac51161e4804d19bba32f2a2685f7a61e756faa9cb467713030",
        "after": "1be0d139daa62053d2351494c7bd0471b872efe6444d193d3037b0b52841b492"
      }
    ]
  },
  {
    "slug": "sglt2-ckd-progression",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "cf6a3558b44b9527f069ef74efc8acab815b10ddfcd4ef0aeaf98f7c4dd00a05",
        "after": "5730cdb5bb80ab2b15f63b3e81b1abbd37a4cd9dcefee637de5422bce4e5fbd5"
      }
    ]
  },
  {
    "slug": "sglt2-hfref-hosp-cvdeath",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "766715ba86c3a08fdb10e6805c0349d3401da17eaad45e5fce6dd32f5427a76f",
        "after": "872ad26ea3daba31bbc793843a75835e5356c5deb4014a93679f870cf60bed61"
      }
    ]
  },
  {
    "slug": "sglt2-primary-prevention-hf",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "b4b8d2abd3ce2c7b18f158dd61be5bb544e618e50d521af21aa5e8f743fea529",
        "after": "e4d3d8fd53818708b48efadacbb814ffa26c49254fa2c8eae9f7b77bb5aa2cd1"
      }
    ]
  },
  {
    "slug": "spironolactone-hfref-mortality",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "d234d70245f495533720568fb27ea02868a025ca9bd82e3e1df4f7752c74751c",
        "after": "0d37a40bb956a486f543e584e1935ae2ef7d700f3623e06dd00ff8bed033bace"
      }
    ]
  },
  {
    "slug": "statins-primary-prevention-elderly",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "a7a250d816b1fbadd7e4b52ea14a2f306581df209bc911dda66f3ca3674cd24b",
        "after": "b5083b4bc1da24a90986e206badf300f9102e248d415d5bc4827d00891e67bd5"
      }
    ]
  },
  {
    "slug": "ticagrelor-vs-clopidogrel-acs",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "65c91750d3a26100f0bfbf2a9d41f23b553cb27dce715b2e338c9e33607c0d52",
        "after": "e70ef4114d545a1a1b74b034f285f4646e184a7e6c42d8f3f3b6a780ba576ba4"
      }
    ]
  },
  {
    "slug": "tocilizumab-covid19-mortality",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "a767b6ba0d7385ce304a1020b77e4ee7423b6c23b5ed2756cf261cc1bf272049",
        "after": "91f235c05260e49d113a356b2031fb6e905d1ae41d0e7ed6e21d0bf558b41616"
      }
    ]
  },
  {
    "slug": "tranexamic-acid-pph",
    "changes": [
      {
        "path": "/reproduction/certificate/analysis_code_blobs/harness/synth.py",
        "before": "504c2bf2b895c7241962907a25ce0acfa0d63cb7",
        "after": "29246ea5b0917c639b1dd9e5d61d5c57d37aa6a5"
      },
      {
        "path": "/reproduction/certificate/analysis_code_sha256",
        "before": "81fbc6b07395c9785a58d9a746ae6d18097d73c658a26151fc2902b6b88f9ae2",
        "after": "fadc4657be3559f39b2310869b333d3c489db48444b91d8ffd81ec4142ef4a63"
      },
      {
        "path": "/reproduction/certificate/release_sha256",
        "before": "e145c9cd7f774084546b78016c2093b60f3727f0a4711a37167f425f5a9c3c21",
        "after": "71c766bc3e5ee524723ad22532edced6f37b2fc195f2177320acc102a4b1230f"
      }
    ]
  }
]
```
