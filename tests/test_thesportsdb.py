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
    assert m.fetch_past_events(4328) == []
    assert m.fetch_results_for_keys() == []


def test_fallback_provider_defaults_to_mock(monkeypatch):
    """Without the live-feed flag, the frontend source is deterministic mock."""
    monkeypatch.delenv("SPORTS_ENABLE_LIVE_FEED", raising=False)
    from sports_trends.providers.fallback_provider import FallbackProvider
    p = FallbackProvider()
    assert p.mode == "fallback"
    assert p.fetch_tomorrow_matches()        # non-empty mock slate
    assert p.fetch_live_results()            # mock live games present in dev


def test_live_feed_flag_respects_network_disable(monkeypatch):
    """SPORTS_DISABLE_NETWORK forces mock even when the live feed is enabled."""
    monkeypatch.setenv("SPORTS_ENABLE_LIVE_FEED", "1")
    monkeypatch.setenv("SPORTS_DISABLE_NETWORK", "1")
    from sports_trends.providers.fallback_provider import FallbackProvider
    p = FallbackProvider()
    assert p.mode == "fallback"  # network disabled wins -> deterministic mock
    assert p.fetch_tomorrow_matches()


def test_live_feed_empty_response_falls_back_to_mock(monkeypatch):
    """A rate-limited/empty live feed must not publish a blank slate."""
    monkeypatch.setenv("SPORTS_ENABLE_LIVE_FEED", "1")
    monkeypatch.delenv("SPORTS_DISABLE_NETWORK", raising=False)
    import sports_trends.providers.fallback_provider as m

    monkeypatch.setattr(m.tsd, "fetch_for_keys", lambda: [])
    monkeypatch.setattr(m.tsd, "fetch_results_for_keys", lambda: [])

    p = m.FallbackProvider()
    assert p.mode == "live-feed"
    assert len(p.fetch_today_matches()) >= 1
    assert len(p.fetch_tomorrow_matches()) >= 4
    assert len(p.fetch_finished_results()) >= 1
