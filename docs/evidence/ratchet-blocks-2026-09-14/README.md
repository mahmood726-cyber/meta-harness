# Ratchet blocks 2026-09-14

**Fix state (orthogonal fields rule): LANDED / NONE / INSTANCE / CURRENT** - generated from TRANCHE-block-level-ratchet

This directory proves the honest-state ratchet defect at `b8925e04`: the lane-start phrase-only `compare()` reported zero violations across 32 review pages, while block-level tracking reports 15 lost absent/banner blocks by SHA-256 and text prefix.
