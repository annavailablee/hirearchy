"""
Unit tests for the pure compatibility algorithm.
No DB, no HTTP — just the function.
"""

from app.services.compatibility import (
    JobMatchInput,
    SkillRef,
    UserMatchInput,
    UserSkill,
    compute_match,
)


def skill(name, category="language", context=None):
    return UserSkill(canonical=name, category=category, context=context)


def ref(name, category="language"):
    return SkillRef(canonical=name, category=category)


def category(result, name):
    return next(c for c in result.breakdown if c.name == name)


# ---------- Skills ----------

def test_perfect_required_skills():
    job = JobMatchInput(required_skills=(ref("Python"), ref("SQL")))
    user = UserMatchInput(skills=(skill("Python"), skill("SQL")))
    result = compute_match(job, user)
    # 40 required + 10 preferred (nothing preferred)
    assert category(result, "skills").earned == 50.0

def test_zero_required_skills_matched():
    job = JobMatchInput(required_skills=(ref("Python"), ref("Docker")))
    user = UserMatchInput(skills=(skill("Java"),))
    result = compute_match(job, user)
    # 0 for required (0/2), 10 for preferred (nothing to match)
    assert category(result, "skills").earned == 10.0


def test_partial_required_skills():
    job = JobMatchInput(required_skills=(ref("Python"), ref("SQL"), ref("Docker"), ref("AWS")))
    user = UserMatchInput(skills=(skill("Python"), skill("SQL")))
    result = compute_match(job, user)
    # 40 * (2/4) = 20, plus 10 for empty preferred = 30
    assert category(result, "skills").earned == 30.0


def test_preferred_skills_add_bonus():
    job = JobMatchInput(
        required_skills=(ref("Python"),),
        preferred_skills=(ref("Redis"), ref("Kubernetes")),
    )
    user = UserMatchInput(skills=(skill("Python"), skill("Redis")))
    result = compute_match(job, user)
    # 40 * 1 + 10 * (1/2) = 45
    assert category(result, "skills").earned == 45.0


def test_no_skills_at_all_adds_note():
    job = JobMatchInput()
    user = UserMatchInput()
    result = compute_match(job, user)
    assert any("No skills" in n for n in result.notes)


def test_missing_required_skills_are_listed():
    job = JobMatchInput(required_skills=(ref("Python"), ref("Docker"), ref("AWS")))
    user = UserMatchInput(skills=(skill("Python"),))
    result = compute_match(job, user)
    assert result.missing_required_skills == ["AWS", "Docker"]


def test_matched_skills_include_context():
    job = JobMatchInput(required_skills=(ref("Python"),))
    user = UserMatchInput(skills=(skill("Python", context="detected in Projects section"),))
    result = compute_match(job, user)
    assert result.matched_required_skills[0].context == "detected in Projects section"


# ---------- Experience ----------

def test_exact_experience_match():
    job = JobMatchInput(experience_level="junior")
    user = UserMatchInput(experience_level="junior")
    assert category(compute_match(job, user), "experience").earned == 20.0


def test_overqualified_is_full_credit():
    job = JobMatchInput(experience_level="junior")
    user = UserMatchInput(experience_level="senior")
    assert category(compute_match(job, user), "experience").earned == 20.0


def test_one_level_under():
    job = JobMatchInput(experience_level="mid")
    user = UserMatchInput(experience_level="junior")
    assert category(compute_match(job, user), "experience").earned == 15.0


def test_two_levels_under():
    job = JobMatchInput(experience_level="senior")
    user = UserMatchInput(experience_level="junior")
    assert category(compute_match(job, user), "experience").earned == 8.0


def test_three_levels_under():
    job = JobMatchInput(experience_level="senior")
    user = UserMatchInput(experience_level="student")
    assert category(compute_match(job, user), "experience").earned == 0.0


def test_missing_experience_gives_full_credit():
    job = JobMatchInput(experience_level="senior")
    user = UserMatchInput(experience_level=None)
    assert category(compute_match(job, user), "experience").earned == 20.0


# ---------- Education ----------

def test_no_education_requirement():
    job = JobMatchInput()
    user = UserMatchInput(degree="B.Tech")
    assert category(compute_match(job, user), "education").earned == 10.0


def test_bachelor_meets_bachelor():
    job = JobMatchInput(education_requirements="Bachelor's degree required")
    user = UserMatchInput(degree="B.Tech in CS")
    assert category(compute_match(job, user), "education").earned == 10.0


def test_master_exceeds_bachelor():
    job = JobMatchInput(education_requirements="Bachelor's degree")
    user = UserMatchInput(degree="M.Tech in CS")
    assert category(compute_match(job, user), "education").earned == 10.0


def test_bachelor_below_master():
    job = JobMatchInput(education_requirements="Master's degree preferred")
    user = UserMatchInput(degree="B.Tech")
    assert category(compute_match(job, user), "education").earned == 3.0


# ---------- Location ----------

def test_remote_job_user_wants_remote():
    job = JobMatchInput(remote_type="remote")
    user = UserMatchInput(remote_preference="remote")
    assert category(compute_match(job, user), "location").earned == 10.0


def test_remote_job_user_wants_onsite():
    job = JobMatchInput(remote_type="remote")
    user = UserMatchInput(remote_preference="onsite")
    # Partial credit — remote still workable but not preferred
    assert category(compute_match(job, user), "location").earned == 7.0


def test_onsite_job_location_match():
    job = JobMatchInput(remote_type="onsite", location="Bangalore, India")
    user = UserMatchInput(
        remote_preference="onsite",
        preferred_locations=("Bangalore",),
    )
    assert category(compute_match(job, user), "location").earned == 10.0


def test_onsite_job_location_mismatch():
    job = JobMatchInput(remote_type="onsite", location="Mumbai")
    user = UserMatchInput(
        remote_preference="onsite",
        preferred_locations=("Bangalore",),
    )
    assert category(compute_match(job, user), "location").earned == 3.0


# ---------- Employment type ----------

def test_employment_type_match():
    job = JobMatchInput(employment_type="internship")
    user = UserMatchInput(preferred_employment_types=("internship", "full-time"))
    assert category(compute_match(job, user), "employment_type").earned == 10.0


def test_employment_type_mismatch():
    job = JobMatchInput(employment_type="contract")
    user = UserMatchInput(preferred_employment_types=("internship",))
    assert category(compute_match(job, user), "employment_type").earned == 0.0


# ---------- Overall ----------

def test_perfect_match_scores_100():
    job = JobMatchInput(
        required_skills=(ref("Python"),),
        experience_level="junior",
        education_requirements="Bachelor's degree",
        remote_type="remote",
        employment_type="full-time",
    )
    user = UserMatchInput(
        skills=(skill("Python"),),
        experience_level="junior",
        degree="B.Tech",
        remote_preference="remote",
        preferred_employment_types=("full-time",),
    )
    assert compute_match(job, user).score == 100


def test_score_is_deterministic():
    job = JobMatchInput(required_skills=(ref("Python"), ref("Docker")))
    user = UserMatchInput(skills=(skill("Python"),))
    a = compute_match(job, user).score
    b = compute_match(job, user).score
    assert a == b


def test_breakdown_sums_correctly():
    job = JobMatchInput(required_skills=(ref("Python"),))
    user = UserMatchInput(skills=(skill("Python"),))
    result = compute_match(job, user)
    total_possible = sum(c.possible for c in result.breakdown)
    assert total_possible == 100