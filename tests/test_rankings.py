from sports_trends.ranking.rank_top_matches import rank_top_matches


def test_rank_top_matches_orders_interest():
    rows = rank_top_matches([{"id": "low", "interest_score": 1}, {"id": "high", "interest_score": 99}])
    assert rows[0]["id"] == "high"
