"""Plant (8 Oct, Mahmood's 'yes do all that' on memo 4): the multi-registry adapter must never query WHO ICTRP's portal.
trialsearch.who.int/robots.txt is 'User-agent: * / Disallow: /' and WHO's web and crawling services are for agreed
partners only; the adapter fetched the public HTML search page anyway. ICTRP is reported NOT_RUN_ACCESS, with its open
route named (a person's Search Portal export or WHO's full-dataset request)."""
from __future__ import annotations

from harness import registry_multi as rm


def test_ictrp_is_never_fetched_and_is_reported_not_run(monkeypatch):
    seen = []

    def fake_get(url, timeout=30):
        seen.append(url)
        if "trialsearch.who.int" in url:
            raise AssertionError("the adapter fetched the ICTRP portal")
        return ""
    monkeypatch.setattr(rm, "_get_text", fake_get)
    monkeypatch.setattr(rm.time, "sleep", lambda s: None)
    out = rm.registry_multi_with_status("heart failure", "ferric carboxymaltose")
    assert not any("trialsearch.who.int" in u for u in seen)
    st = out["registries"]["ICTRP"]
    assert st["status"] == rm.NOT_RUN_ACCESS and "robots.txt" in st["note"]
