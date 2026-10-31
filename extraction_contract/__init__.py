"""P3 -- the trial-level extraction contract (opt-in, versioned).

Before a page, a G1 record or a manuscript may say it "matches the published meta-analysis", every trial-level value
it pools must be:
  (a) TYPED      -- a declared field with a declared type and range (fields.py), and coherent with its siblings
                    (events <= total, the CI brackets the point, a ratio is positive);
  (b) SOURCED    -- carried by the exact source passage it was read from: a verbatim quote at character offsets in a
                    document pinned by sha256, with the value literally present in the quote (passage.py);
  (c) DUAL-READ  -- for OUTCOME fields: read independently by two model families (Claude = anthropic, Codex = openai),
                    neither shown the other's answer, and either AGREED or ADJUDICATED against a verified passage --
                    decided by the source bytes, never by a vote (dual.py).
gate.py turns that into one verdict -- ALLOW_MATCH_CLAIM or REFUSE -- and the CLI exits 0 only for ALLOW.

Why it is a package and not harness/<x>.py: any new harness/*.py changes every page certificate's scope
(harness/certificate.py _scope), forcing a re-certification of every served page. Nothing in the certificate closure
imports this package, so adopting P3 is a per-topic, per-lane choice that changes no served byte.

Opt in: run `python -m extraction_contract check <bundle.json> --docs-root <dir> --records <records-dir>` and cite its report. Omitting records is a noncertifying REFUSE.
Version: CONTRACT_VERSION. A bundle naming a different MAJOR version is refused (fail closed), never coerced.
"""
CONTRACT_VERSION = "p3/1.0.0"
CONTRACT_MAJOR = "p3/1"
