def test_public_quiz_list_only_shows_published(client, published_quiz_id):
    response = client.get("/quizzes")
    assert response.status_code == 200
    ids = [item["id"] for item in response.json()]
    assert published_quiz_id in ids


def test_quiz_detail_does_not_expose_correct_answers(client, published_quiz_id):
    response = client.get(f"/quizzes/{published_quiz_id}")
    assert response.status_code == 200
    body = response.json()
    assert len(body["questions"]) == 2
    for question in body["questions"]:
        assert "correct_option_index" not in question
        assert "explanation" not in question


def test_unpublished_quiz_not_publicly_accessible(client, admin_headers, sample_quiz_payload):
    created = client.post("/admin/quizzes", json=sample_quiz_payload, headers=admin_headers)
    assert created.status_code == 201
    response = client.get(f"/quizzes/{created.json()['id']}")
    assert response.status_code == 404


def test_quiz_attempt_requires_auth(client, published_quiz_id):
    response = client.post(
        f"/quizzes/{published_quiz_id}/attempts",
        json={"answers": [{"question_id": 1, "selected_option_index": 0}]},
    )
    assert response.status_code == 401


def test_quiz_attempt_success(client, login_headers, published_quiz_id):
    detail = client.get(f"/quizzes/{published_quiz_id}").json()
    answers = [
        {"question_id": question["id"], "selected_option_index": index}
        for index, question in enumerate(detail["questions"])
    ]
    response = client.post(
        f"/quizzes/{published_quiz_id}/attempts",
        json={"answers": answers},
        headers=login_headers,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["quiz_id"] == published_quiz_id
    assert body["total_questions"] == 2
    assert body["score"] == 2
    assert body["percentage"] == 100
    assert body["xp_awarded"] == 20


def test_quiz_attempt_rejects_empty_answers(client, login_headers, published_quiz_id):
    response = client.post(
        f"/quizzes/{published_quiz_id}/attempts",
        json={"answers": []},
        headers=login_headers,
    )
    assert response.status_code == 422


def test_quiz_attempt_history_requires_auth(client):
    response = client.get("/quizzes/attempts/me")
    assert response.status_code == 401


def test_admin_quiz_routes_forbid_student(client, auth_headers):
    response = client.get("/admin/quizzes", headers=auth_headers)
    assert response.status_code == 403
