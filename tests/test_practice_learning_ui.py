def _publish_practice_exercise(client, admin_headers, *, expected="pwd"):
    created = client.post(
        "/admin/practice",
        headers=admin_headers,
        json={
            "title": "Show current directory",
            "description": "Practice a basic navigation command.",
            "instructions": "Enter the Linux command that prints the current working directory.",
            "expected_answers": [expected],
            "difficulty": "beginner",
            "display_order": 0,
            "is_published": False,
        },
    )
    assert created.status_code == 201, created.text
    exercise_id = created.json()["id"]
    published = client.patch(
        f"/admin/practice/{exercise_id}/publish", headers=admin_headers
    )
    assert published.status_code == 200, published.text
    return exercise_id


def test_dashboard_renders_practice_section_and_answer_dialog(client):
    response = client.get("/app/dashboard")

    assert response.status_code == 200
    assert 'id="practice-grid"' in response.text
    assert 'id="practice-dialog"' in response.text
    assert 'id="practice-history"' in response.text


def test_dashboard_loads_practice_catalog_history_and_submission_script(client):
    page = client.get("/app/dashboard")
    script = client.get("/static/js/achievements.js")

    assert page.status_code == 200
    assert "Practice exercises" in page.text
    assert script.status_code == 200
    assert "api('/practice')" in script.text
    assert "api('/practice/attempts/me')" in script.text
    assert "submitPracticeAnswer" in script.text


def test_correct_practice_submission_updates_xp_progress_badge_and_history(
    client, admin_headers, login_headers
):
    exercise_id = _publish_practice_exercise(client, admin_headers)
    submitted = client.post(
        f"/practice/{exercise_id}/attempts",
        headers=login_headers,
        json={"answer": "PWD"},
    )
    assert submitted.status_code == 200, submitted.text
    result = submitted.json()
    assert result["is_correct"] is True
    assert result["xp_awarded"] == 15
    assert [badge["code"] for badge in result["newly_unlocked"]] == [
        "command_learner"
    ]

    dashboard = client.get("/dashboard", headers=login_headers)
    history = client.get("/practice/attempts/me", headers=login_headers)

    assert dashboard.status_code == 200, dashboard.text
    assert dashboard.json()["progress"]["practice_completed"] == 1
    assert dashboard.json()["xp"]["total_xp"] == 15
    assert history.status_code == 200, history.text
    assert len(history.json()) == 1
    assert history.json()[0]["exercise_id"] == exercise_id
    assert history.json()[0]["is_correct"] is True


def test_incorrect_practice_answer_is_recorded_without_xp(
    client, admin_headers, login_headers
):
    exercise_id = _publish_practice_exercise(client, admin_headers)
    submitted = client.post(
        f"/practice/{exercise_id}/attempts",
        headers=login_headers,
        json={"answer": "ls"},
    )

    assert submitted.status_code == 200, submitted.text
    assert submitted.json()["is_correct"] is False
    assert submitted.json()["xp_awarded"] == 0
    dashboard = client.get("/dashboard", headers=login_headers)
    history = client.get("/practice/attempts/me", headers=login_headers)
    assert dashboard.json()["progress"]["practice_completed"] == 0
    assert dashboard.json()["xp"]["total_xp"] == 0
    assert len(history.json()) == 1
    assert history.json()[0]["is_correct"] is False


def test_practice_normalizes_multiple_spaces_inside_command(
    client, admin_headers, login_headers
):
    exercise_id = _publish_practice_exercise(
        client, admin_headers, expected="ls -la"
    )

    response = client.post(
        f"/practice/{exercise_id}/attempts",
        headers=login_headers,
        json={"answer": "ls    -la"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["is_correct"] is True
