def _create_published_exercise(client, admin_headers):
    payload = {
        "title": "Show current directory",
        "description": "Basic navigation command",
        "instructions": "Enter the Linux command that prints the current working directory.",
        "expected_answers": ["pwd"],
        "difficulty": "beginner",
        "display_order": 1,
        "is_published": False,
    }
    response = client.post("/admin/practice", json=payload, headers=admin_headers)
    assert response.status_code == 201, response.text
    exercise_id = response.json()["id"]
    response = client.patch(
        f"/admin/practice/{exercise_id}/publish", headers=admin_headers
    )
    assert response.status_code == 200, response.text
    return exercise_id


def test_admin_can_create_and_publish_practice(client, admin_headers):
    exercise_id = _create_published_exercise(client, admin_headers)
    response = client.get("/practice")
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [exercise_id]
    assert "expected_answers" not in response.json()[0]


def test_students_cannot_manage_practice(client, auth_headers):
    response = client.post("/admin/practice", json={
        "title": "Test", "instructions": "Test", "expected_answers": ["test"]
    }, headers=auth_headers)
    assert response.status_code == 403


def test_practice_requires_authentication_to_submit(client, admin_headers):
    exercise_id = _create_published_exercise(client, admin_headers)
    response = client.post(f"/practice/{exercise_id}/attempts", json={"answer": "pwd"})
    assert response.status_code == 401


def test_correct_answer_awards_15_xp_once(client, admin_headers, auth_headers):
    exercise_id = _create_published_exercise(client, admin_headers)
    first = client.post(f"/practice/{exercise_id}/attempts", json={"answer": "  PWD  "},
                        headers=auth_headers)
    assert first.status_code == 200, first.text
    assert first.json()["is_correct"] is True
    assert first.json()["xp_awarded"] == 15
    assert first.json()["total_xp"] == 15
    assert first.json()["practice_completed"] == 1

    second = client.post(f"/practice/{exercise_id}/attempts", json={"answer": "pwd"},
                         headers=auth_headers)
    assert second.status_code == 200, second.text
    assert second.json()["xp_awarded"] == 0
    assert second.json()["total_xp"] == 15
    assert second.json()["practice_completed"] == 1


def test_incorrect_answer_does_not_award_xp(client, admin_headers, auth_headers):
    exercise_id = _create_published_exercise(client, admin_headers)
    response = client.post(f"/practice/{exercise_id}/attempts", json={"answer": "ls"},
                           headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["is_correct"] is False
    assert response.json()["xp_awarded"] == 0
    assert response.json()["total_xp"] == 0
    assert response.json()["practice_completed"] == 0


def test_unpublished_practice_is_hidden_and_cannot_be_submitted(
    client, admin_headers, auth_headers
):
    response = client.post("/admin/practice", json={
        "title": "Draft", "instructions": "Try it", "expected_answers": ["pwd"]
    }, headers=admin_headers)
    exercise_id = response.json()["id"]
    assert all(item["id"] != exercise_id for item in client.get("/practice").json())
    result = client.post(f"/practice/{exercise_id}/attempts", json={"answer": "pwd"},
                         headers=auth_headers)
    assert result.status_code == 404


def test_practice_history_contains_attempts(client, admin_headers, auth_headers):
    exercise_id = _create_published_exercise(client, admin_headers)
    client.post(f"/practice/{exercise_id}/attempts", json={"answer": "pwd"},
                headers=auth_headers)
    response = client.get("/practice/attempts/me", headers=auth_headers)
    assert response.status_code == 200, response.text
    assert len(response.json()) == 1
    assert response.json()[0]["is_correct"] is True


def test_exercise_with_attempts_cannot_be_deleted(client, admin_headers, auth_headers):
    exercise_id = _create_published_exercise(client, admin_headers)
    client.post(f"/practice/{exercise_id}/attempts", json={"answer": "pwd"},
                headers=auth_headers)
    response = client.delete(f"/admin/practice/{exercise_id}", headers=admin_headers)
    assert response.status_code == 409
