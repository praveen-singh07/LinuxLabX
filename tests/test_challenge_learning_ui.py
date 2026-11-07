def _publish_challenge(client, admin_headers):
    created = client.post(
        "/admin/challenges",
        headers=admin_headers,
        json={
            "title": "Locate the system log",
            "description": "Search for a named log file.",
            "scenario": "A file called system.log is somewhere inside /var/log.",
            "instructions": "Enter a command that searches from /var/log by filename.",
            "expected_answers": [
                "find /var/log -name system.log",
                "find /var/log -name 'system.log'",
            ],
            "hints": ["Use find.", "The -name option matches a filename."],
            "difficulty": "beginner",
            "display_order": 0,
            "is_published": False,
        },
    )
    assert created.status_code == 201, created.text
    challenge_id = created.json()["id"]
    published = client.patch(
        f"/admin/challenges/{challenge_id}/publish", headers=admin_headers
    )
    assert published.status_code == 200, published.text
    return challenge_id


def test_dashboard_renders_challenge_cards_and_scenario_dialog(client):
    response = client.get("/app/dashboard")

    assert response.status_code == 200
    assert 'id="challenge-grid"' in response.text
    assert 'id="challenge-dialog"' in response.text
    assert 'id="challenge-history"' in response.text


def test_dashboard_loads_challenge_catalog_history_and_submission_script(client):
    page = client.get("/app/dashboard")
    script = client.get("/static/js/achievements.js")

    assert page.status_code == 200
    assert "Challenges" in page.text
    assert script.status_code == 200
    assert "api('/challenges')" in script.text
    assert "api('/challenges/attempts/me')" in script.text
    assert "submitChallengeAnswer" in script.text


def test_correct_challenge_updates_xp_progress_badge_and_history(
    client, admin_headers, login_headers
):
    challenge_id = _publish_challenge(client, admin_headers)
    submitted = client.post(
        f"/challenges/{challenge_id}/attempts",
        headers=login_headers,
        json={"answer": "find /var/log -name system.log"},
    )
    assert submitted.status_code == 200, submitted.text
    result = submitted.json()
    assert result["is_correct"] is True
    assert result["xp_awarded"] == 30
    assert [badge["code"] for badge in result["newly_unlocked"]] == [
        "challenge_solver"
    ]

    dashboard = client.get("/dashboard", headers=login_headers)
    history = client.get("/challenges/attempts/me", headers=login_headers)

    assert dashboard.status_code == 200, dashboard.text
    assert dashboard.json()["progress"]["challenges_completed"] == 1
    assert dashboard.json()["xp"]["total_xp"] == 30
    assert history.status_code == 200, history.text
    assert len(history.json()) == 1
    assert history.json()[0]["challenge_id"] == challenge_id
    assert history.json()[0]["is_correct"] is True


def test_incorrect_challenge_is_recorded_without_xp(
    client, admin_headers, login_headers
):
    challenge_id = _publish_challenge(client, admin_headers)
    submitted = client.post(
        f"/challenges/{challenge_id}/attempts",
        headers=login_headers,
        json={"answer": "ls"},
    )

    assert submitted.status_code == 200, submitted.text
    assert submitted.json()["is_correct"] is False
    assert submitted.json()["xp_awarded"] == 0
    dashboard = client.get("/dashboard", headers=login_headers)
    history = client.get("/challenges/attempts/me", headers=login_headers)
    assert dashboard.json()["progress"]["challenges_completed"] == 0
    assert dashboard.json()["xp"]["total_xp"] == 0
    assert len(history.json()) == 1
    assert history.json()[0]["is_correct"] is False
