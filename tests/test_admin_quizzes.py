def test_admin_can_create_quiz(client, admin_headers, sample_quiz_payload):
    response = client.post("/admin/quizzes", json=sample_quiz_payload, headers=admin_headers)
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["title"] == sample_quiz_payload["title"]
    assert len(body["questions"]) == 2


def test_admin_quiz_routes_require_auth(client):
    response = client.get("/admin/quizzes")
    assert response.status_code == 401


def test_admin_can_publish_quiz(client, admin_headers, sample_quiz_payload):
    created = client.post("/admin/quizzes", json=sample_quiz_payload, headers=admin_headers)
    quiz_id = created.json()["id"]
    response = client.patch(f"/admin/quizzes/{quiz_id}/publish", headers=admin_headers)
    assert response.status_code == 200, response.text
    assert response.json()["is_published"] is True


def test_admin_cannot_publish_quiz_without_questions(client, admin_headers):
    payload = {
        "title": "Empty Quiz",
        "description": "",
        "difficulty": "beginner",
        "questions": [],
        "is_published": False,
    }
    # Schema requires at least one question, so validation rejects before service execution.
    response = client.post("/admin/quizzes", json=payload, headers=admin_headers)
    assert response.status_code == 422


def test_admin_create_validates_correct_option_index(client, admin_headers):
    payload = {
        "title": "Invalid Question Quiz",
        "questions": [{
            "prompt": "Pick one",
            "options": ["A", "B"],
            "correct_option_index": 4,
        }],
    }
    response = client.post("/admin/quizzes", json=payload, headers=admin_headers)
    assert response.status_code == 422


def test_admin_missing_quiz_returns_404(client, admin_headers, sample_quiz_payload):
    response = client.patch("/admin/quizzes/99999/publish", headers=admin_headers)
    assert response.status_code == 404
