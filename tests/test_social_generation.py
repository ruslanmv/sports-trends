from sports_trends.social.generate_og_images import generate_og_images, render_og_svg
from sports_trends.social.generate_share_text import generate_share_text

MATCH = {"match_id": "rma-mci", "league": "UEFA Champions League",
         "home_team": "Real Madrid", "away_team": "Man City",
         "prediction_label": "AI: Real Madrid favoured"}


def test_share_text_has_intents():
    s = generate_share_text([MATCH])[0]
    assert "Real Madrid" in s["text"]
    assert s["x"].startswith("https://twitter.com/intent/tweet")
    assert s["whatsapp"].startswith("https://wa.me/")


def test_og_svg_renders_and_writes(tmp_path):
    svg = render_og_svg(MATCH)
    assert "<svg" in svg and "Real Madrid" in svg
    written = generate_og_images([MATCH], out_dir=tmp_path)
    assert (tmp_path / "rma-mci.svg").exists() and len(written) == 1
