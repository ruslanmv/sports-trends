from ruslan_sports.providers.fallback_provider import FallbackProvider


def test_fallback_provider_returns_lists():
    provider = FallbackProvider()
    assert provider.fetch_today() == []
    assert provider.fetch_tomorrow() == []
    assert provider.fetch_live() == []
