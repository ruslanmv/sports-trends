from sports_trends.providers.thesportsdb_provider import LEAGUES, fetch_for_keys


def test_thesportsdb_keys_present():
    assert "epl" in LEAGUES and "nba" in LEAGUES


def test_fetch_is_network_safe(monkeypatch):
    # Force the HTTP layer to fail -> provider must return [] (never raise).
    import sports_trends.providers.thesportsdb_provider as m

    def boom(*a, **k):
        raise RuntimeError("offline")
    import requests
    monkeypatch.setattr(requests, "get", boom)
    assert m.fetch_next_events(4328) == []
