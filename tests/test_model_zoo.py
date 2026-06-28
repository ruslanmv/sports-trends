from sports_trends.models.model_zoo import SPORT_MODELS, algo_for, build_model, registry_table


def test_each_sport_has_distinct_optimized_model():
    algos = {s: m["algo"] for s, m in SPORT_MODELS.items()}
    assert algos["football"] == "hist_gradient_boosting"
    assert algos["basketball"] == "logistic_regression"
    assert algos["tennis"] == "gradient_boosting"
    assert algos["cricket"] == "random_forest"
    # at least three different algorithms across sports
    assert len(set(algos.values())) >= 3


def test_algo_for_default():
    assert algo_for("unknown-sport") == "logistic_regression"


def test_build_model_is_fittable():
    import numpy as np
    X = np.random.RandomState(0).rand(60, 4)
    y = (X[:, 0] > 0.5).astype(int)
    model = build_model("logistic_regression", calibrate=False)
    model.fit(X, y)
    assert model.predict(X).shape == (60,)


def test_registry_table_shape():
    rows = registry_table()
    assert {r["sport"] for r in rows} == set(SPORT_MODELS)
    assert all("rationale" in r and "model_name" in r for r in rows)
