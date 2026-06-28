from sports_trends.seo.generate_json_ld import sport_event_jsonld
from sports_trends.seo.generate_match_pages import generate_match_pages, render_match_page
from sports_trends.seo.generate_meta_descriptions import generate_meta_descriptions
from sports_trends.seo.generate_sitemap import sitemap_urls

MATCH = {
    "match_id": "rma-mci", "sport": "football", "league": "UEFA Champions League",
    "home_team": "Real Madrid", "away_team": "Man City",
    "kickoff": "2026-06-28T21:00:00+02:00",
    "probabilities": {"home_win": 0.56, "draw": 0.22, "away_win": 0.22},
}


def test_meta_description_placeholder():
    assert generate_meta_descriptions([]) == []


def test_meta_description_is_bounded():
    meta = generate_meta_descriptions([MATCH])[0]
    assert meta["match_id"] == "rma-mci"
    assert 0 < len(meta["title"]) <= 70
    assert 0 < len(meta["description"]) <= 160


def test_sport_event_jsonld_shape():
    ld = sport_event_jsonld(MATCH)
    assert ld["@type"] == "SportsEvent"
    assert ld["name"] == "Real Madrid vs Man City"
    assert len(ld["competitor"]) == 2


def test_render_and_write_match_pages(tmp_path):
    page = render_match_page(MATCH)
    assert page.startswith("---")
    assert "layout: sports-match" in page
    written = generate_match_pages([MATCH], out_dir=tmp_path)
    assert (tmp_path / "rma-mci.md").exists() and len(written) == 1


def test_sitemap_includes_static_and_match_urls():
    urls = sitemap_urls([MATCH])
    assert any(u.endswith("/sports/") for u in urls)
    assert any("/match/rma-mci/" in u for u in urls)
