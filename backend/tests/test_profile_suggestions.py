from app.services.profile_suggestions import suggest_profile_fields


def test_detects_btech_degree():
    text = "Bachelor of Technology in Computer Science"
    r = suggest_profile_fields(text)
    assert r.degree == "B.Tech"


def test_detects_mtech_over_master():
    text = "M.Tech in AI"
    r = suggest_profile_fields(text)
    assert r.degree == "M.Tech"


def test_detects_graduation_year_from_completion_phrase():
    text = "Year of completion: 2027"
    r = suggest_profile_fields(text)
    assert r.graduation_year == 2027


def test_detects_graduation_year_from_range():
    text = "Education: 2023 - 2027"
    r = suggest_profile_fields(text)
    assert r.graduation_year == 2027


def test_detects_institution():
    text = "Sahrdaya College of Engineering and Technology\nComputer Science"
    r = suggest_profile_fields(text)
    assert r.education is not None
    assert "College" in r.education


def test_empty_text_returns_no_suggestions():
    r = suggest_profile_fields("")
    assert r.degree is None
    assert r.graduation_year is None
    assert r.education is None
    assert any("no extractable" in n.lower() for n in r.notes)


def test_no_false_positives_on_random_text():
    text = "I like long walks on the beach and drinking coffee."
    r = suggest_profile_fields(text)
    assert r.degree is None
    assert r.graduation_year is None


def test_year_out_of_range_is_ignored():
    text = "Year of completion: 1850"
    r = suggest_profile_fields(text)
    assert r.graduation_year is None