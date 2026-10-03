from app.services.skill_extraction import extract_skills, get_taxonomy_size


def names(skills):
    return {s.canonical for s in skills}


def test_empty_text_returns_empty():
    assert extract_skills("") == []


def test_simple_match():
    assert names(extract_skills("I know Python and SQL.")) == {"Python", "SQL"}


def test_alias_matches_canonical():
    assert names(extract_skills("Experienced with postgres and psql.")) == {"PostgreSQL"}


def test_aws_aliases():
    assert names(extract_skills("Deployed on AWS. Also used Amazon Web Services heavily.")) == {"AWS"}


def test_word_boundary_no_substring_false_positive():
    assert "Java" not in names(extract_skills("I write JavaScript and React."))
    assert "C" not in names(extract_skills("Experienced in C++ and C#."))


def test_cpp_and_csharp_dont_confuse_c():
    assert names(extract_skills("I write C++")) == {"C++"}
    assert names(extract_skills("I write C#")) == {"C#"}


def test_ambiguous_go_lowercase_rejected():
    assert "Go" not in names(extract_skills("I go to the market."))


def test_ambiguous_go_capitalized_accepted():
    assert "Go" in names(extract_skills("Languages: Go, Python, Rust"))


def test_go_golang_alias_always_accepted():
    assert "Go" in names(extract_skills("I write golang services."))


def test_ambiguous_r_rejected_in_prose():
    assert "R" not in names(extract_skills("the r value is 0.5"))


def test_ambiguous_r_accepted_when_capitalized():
    assert "R" in names(extract_skills("Languages: Python, R, SQL"))


def test_no_duplicates_when_aliases_repeat():
    assert names(extract_skills("Python. Also python3 and Python 3. And PYTHON.")) == {"Python"}


def test_multiple_skills():
    got = names(extract_skills("Backend: Python, FastAPI, PostgreSQL, Docker, AWS."))
    assert {"Python", "FastAPI", "PostgreSQL", "Docker", "AWS"} <= got


def test_taxonomy_is_loaded():
    assert get_taxonomy_size() > 40


def test_matched_text_is_recorded():
    skills = extract_skills("Familiar with k8s in production.")
    kubernetes = next(s for s in skills if s.canonical == "Kubernetes")
    assert kubernetes.matched_text.lower() == "k8s"


def test_context_snippet_is_recorded():
    skills = extract_skills("I have used Docker extensively for containerization.")
    docker = next(s for s in skills if s.canonical == "Docker")
    assert "Docker" in docker.context