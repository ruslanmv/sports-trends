from sports_trends.providers import provider_health_report
from sports_trends.providers.fallback_provider import FallbackProvider
from sports_trends.providers.football_provider import FootballProvider


def test_fallback_provider_returns_nonempty_lists():
    p = FallbackProvider()
    assert isinstance(p.fetch_today_matches(), list)
    assert len(p.fetch_tomorrow_matches()) >= 4
    assert all(isinstance(r, dict) for r in p.fetch_tomorrow_matches())
    assert len(p.fetch_live_results()) >= 1


def test_provider_runs_without_api_key_via_fallback():
    p = FootballProvider(api_key="")
    assert p.mode == "fallback"
    rows = p.fetch_tomorrow_matches()
    assert rows and all(r["sport"] == "football" for r in rows)


def test_provider_health_report_shape():
    report = provider_health_report()
    assert {r["sport"] for r in report} >= {"football", "basketball", "tennis", "cricket"}
    assert all(r["mode"] in {"live", "fallback"} for r in report)
