# M3 amendments (append-only; each dated, each names the registration sha it amends)

## A1 — 2026-10-13: defaults confirmed; external timestamp recorded

- **Amends:** registration commit `6f48931610dabf2ce37c6dff02be83de938f86ab`
  (`registry/m3/PREREGISTRATION.md` sha256 `bb1ad5cf3cf22d7854995b749a2df44a1685ff961f1aad5ce72bae207abd4f2f`).
- **Decision:** Mahmood, Dispatch, 13 Oct, "sign and do as you suggested for all"
  (MORNING_SUMMARY_2026-10-13 sha256 `6bf07e9d1cf314bb594c3ed2dd2eb70cf526913f797d5e930344a9f93c63ffa6`, item 5).
  Recorded SEEN_AND_SIGNED; the captain does not sign for him.
- **Made before suite selection:** no held-out case, answer key or examiner exists yet.

| # | Default as registered | Status |
|---|---|---|
| 1 | Answer key held and signed by Mahmood, prepared with a non-OpenAI model family, never the examiner | Confirmed as proposed |
| 2 | Registration sha deposited by Mahmood (email to self) before launch | **Mechanism changed by Mahmood:** a GitHub release now; a Zenodo-archived release once he enables the integration (below) |
| 3 | Highest codex model and effort available on run day, named exactly in the launch record | Confirmed as proposed |
| 4 | Suite size 102 | Confirmed as proposed |

### External timestamp (default 2)

- Tag `m3-preregistration-2026-10-13`: annotated tag object `8c8e1eaa6f18d033fd15f49014d4f942a708473b`, peeling to
  `6f48931610dabf2ce37c6dff02be83de938f86ab` (`git ls-remote origin` 13 Oct).
- GitHub release https://github.com/mahmood726-cyber/meta-harness/releases/tag/m3-preregistration-2026-10-13,
  server-side `publishedAt` **2026-10-13T08:48:37Z** (`createdAt` 08:48:13Z), read back with `gh release view`.
- **Not cryptographically signed.** No signing key is configured, and the captain lane does not sign with Mahmood's
  personal keys. The independent time record is GitHub's server-side timestamp. He may add his own signature, and the
  Zenodo archive (pending his toggle) gives a DOI-backed deposit.
