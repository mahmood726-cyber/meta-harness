"""PLANT (gate-authority proof, 2026-09-14): a deliberately failing test pushed from a hooks-free clone.
If the deploy is gated on verify, this SHA must NOT be deployed. Reverted in the next commit."""


def test_plant_must_fail():
    assert False, "PLANT: this commit must not be served"
