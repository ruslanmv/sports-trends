from sports_trends.seo.generate_meta_descriptions import generate_meta_descriptions


def test_meta_description_placeholder():
    assert generate_meta_descriptions([]) == []
