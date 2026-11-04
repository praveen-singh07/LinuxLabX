def _create_published_challenge(client, admin_headers):
    payload = {
        "title": "Find a file",
        "description": "A scenario-based file search challenge",
        "scenario": "A log file named system.log is somewhere under /var/log.",
        "instructions": "Submit the Linux command that searches for this file from /var/log.",
        "expected_answers": [
            "find /var/log -name system.log",
            "find /var/log -name 'system.log'",
        ],
        "hints": ["Use the find command", "The -name option matches a filename"],
        "difficulty": "beginner",
        "display_order": 1,
        "is_published": False,
    }
    response = client.post("/admin/challenges", json=payload, headers=admin_headers)
    assert response.status_code == 201, response.text
    challenge_id = response.json()["id"]
    response = client.patch(
        f"/admin/challenges/{challenge_id}/publish", headers=admin_headers
    )
    assert response.status_code == 200, response.text
    return challenge_id


def test_admin_can_create_publish_and_list_challenge(client, admin_headers):
    challenge_id = _create_published_challenge(client, admin_headers)
    response = client.get("/challenges")
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [challenge_id]
    assert "expected_answers" not in response.json()[0]


def test_student_cannot_manage_challenges(client, auth_headers):
    response = client.post(
        "/admin/challenges",
        json={
            "title": "Test",
            "scenario": "Scenario",
            "instructions": "Do this",
            "expected_answers": ["answer"],
        },
        headers=auth_headers,
    )
    assert response.status_code == 403


def test_challenge_submission_requires_authentication(client, admin_headers):
    challenge_id = _create_published_challenge(client, admin_headers)
    response = client.post(
        f"/challenges/{challenge_id}/attempts",
        json={"answer": "find /var/log -name system.log"},
    )
    assert response.status_code == 401


def test_correct_challenge_awards_30_xp_once(client, admin_headers, auth_headers):
    challenge_id = _create_published_challenge(client, admin_headers)
    first = client.post(
        f"/challenges/{challenge_id}/attempts",
        json={"answer": " FIND /var/log -name system.log "},
        headers=auth_headers,
    )
    assert first.status_code == 200, first.text
    assert first.json()["is_correct"] is True
    assert first.json()["xp_awarded"] == 30
    assert first.json()["total_xp"] == 30
    assert first.json()["challenges_completed"] == 1

    second = client.post(
        f"/challenges/{challenge_id}/attempts",
        json={"answer": "find /var/log -name system.log"},
        headers=auth_headers,
    )
    assert second.status_code == 200
    assert second.json()["xp_awarded"] == 0
    assert second.json()["total_xp"] == 30
    assert second.json()["challenges_completed"] == 1


def test_incorrect_answer_does_not_award_xp(client, admin_headers, auth_headers):
    challenge_id = _create_published_challenge(client, admin_headers)
    response = client.post(
        f"/challenges/{challenge_id}/attempts",
        json={"answer": "ls"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["is_correct"] is False
    assert response.json()["xp_awarded"] == 0
    assert response.json()["total_xp"] == 0
    assert response.json()["challenges_completed"] == 0


def test_unpublished_challenge_is_not_visible_or_submittable(
    client, admin_headers, auth_headers
):
    response = client.post(
        "/admin/challenges",
        json={
            "title": "Draft",
            "scenario": "Draft scenario",
            "instructions": "Try it",
            "expected_answers": ["answer"],
        },
        headers=admin_headers,
    )
    challenge_id = response.json()["id"]
    assert all(item["id"] != challenge_id for item in client.get("/challenges").json())
    submitted = client.post(
        f"/challenges/{challenge_id}/attempts",
        json={"answer": "answer"},
        headers=auth_headers,
    )
    assert submitted.status_code == 404


def test_challenge_history_contains_submissions(client, admin_headers, auth_headers):
    challenge_id = _create_published_challenge(client, admin_headers)
    client.post(
        f"/challenges/{challenge_id}/attempts",
        json={"answer": "wrong"},
        headers=auth_headers,
    )
    response = client.get("/challenges/attempts/me", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["challenge_id"] == challenge_id


def test_challenge_with_attempts_cannot_be_deleted(client, admin_headers, auth_headers):
    challenge_id = _create_published_challenge(client, admin_headers)
    client.post(
        f"/challenges/{challenge_id}/attempts",
        json={"answer": "wrong"},
        headers=auth_headers,
    )
    response = client.delete(f"/admin/challenges/{challenge_id}", headers=admin_headers)
    assert response.status_code == 409
