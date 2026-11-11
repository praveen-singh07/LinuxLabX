from app.core.security import create_access_token
from app.models.user import User


def _create_path_with_lessons(client, admin_headers, lesson_count=2):
    path = client.post("/admin/learning-paths", headers=admin_headers, json={
        "title": "Linux Essentials", "description": "A guided Linux course.",
        "display_order": 1, "is_published": True,
    })
    assert path.status_code == 201, path.text
    path_id = path.json()["id"]
    topic = client.post(f"/admin/learning-paths/{path_id}/topics", headers=admin_headers, json={
        "title": "Terminal basics", "description": "Start with core commands.",
        "display_order": 1, "is_published": True,
    })
    assert topic.status_code == 201, topic.text
    topic_id = topic.json()["id"]
    lesson_ids = []
    for order in range(lesson_count):
        lesson = client.post("/admin/lessons", headers=admin_headers, json={
            "title": f"Linux lesson {order + 1}", "description": "Practice a command.",
            "command": "pwd", "syntax": "pwd", "examples": [],
            "expected_output": "/home/student", "options": [], "tips": [],
            "common_mistakes": [], "difficulty": "beginner", "display_order": order,
            "is_published": True,
        })
        assert lesson.status_code == 201, lesson.text
        lesson_id = lesson.json()["id"]
        link = client.put(f"/admin/learning-paths/topics/{topic_id}/lessons", headers=admin_headers,
                          json={"lesson_id": lesson_id, "display_order": order})
        assert link.status_code == 200, link.text
        lesson_ids.append(lesson_id)
    return path_id, topic_id, lesson_ids


def test_path_progress_requires_login(client):
    assert client.get("/learning-paths/progress/me").status_code == 401


def test_path_progress_resumes_next_lesson_and_completes(client, admin_headers, auth_headers):
    path_id, topic_id, lessons = _create_path_with_lessons(client, admin_headers)
    url = "/learning-paths/progress/me"

    initial_response = client.get(url, headers=auth_headers)
    assert initial_response.status_code == 200, initial_response.text
    initial = next(row for row in initial_response.json() if row["learning_path_id"] == path_id)
    assert initial["total_lessons"] == 2
    assert initial["completed_lessons"] == 0
    assert initial["progress_percent"] == 0
    assert initial["next_lesson_id"] == lessons[0]
    assert initial["topics"] == [{
        "topic_id": topic_id, "title": "Terminal basics", "total_lessons": 2,
        "completed_lessons": 0, "progress_percent": 0,
    }]

    completed = client.post(f"/lessons/{lessons[0]}/complete", headers=auth_headers)
    assert completed.status_code == 200, completed.text
    halfway = next(row for row in client.get(url, headers=auth_headers).json()
                   if row["learning_path_id"] == path_id)
    assert halfway["completed_lessons"] == 1
    assert halfway["progress_percent"] == 50
    assert halfway["next_lesson_id"] == lessons[1]
    assert halfway["topics"][0]["progress_percent"] == 50

    completed = client.post(f"/lessons/{lessons[1]}/complete", headers=auth_headers)
    assert completed.status_code == 200, completed.text
    finished = next(row for row in client.get(url, headers=auth_headers).json()
                    if row["learning_path_id"] == path_id)
    assert finished["completed_lessons"] == 2
    assert finished["progress_percent"] == 100
    assert finished["is_complete"] is True
    assert finished["next_lesson_id"] is None


def test_path_progress_is_specific_to_signed_in_user(client, admin_headers, auth_headers, db):
    path_id, _, lessons = _create_path_with_lessons(client, admin_headers, lesson_count=1)
    assert client.post(f"/lessons/{lessons[0]}/complete", headers=auth_headers).status_code == 200
    second_user = User(
        name="Second Student", email="second.path.student@example.com",
        password_hash="unused-auth-token-test", role="student", is_active=True,
    )
    db.add(second_user)
    db.commit()
    other_headers = {"Authorization": f"Bearer {create_access_token(user_id=second_user.id, role=second_user.role)}"}
    other_progress = client.get("/learning-paths/progress/me", headers=other_headers)
    assert other_progress.status_code == 200
    other_path = next(row for row in other_progress.json() if row["learning_path_id"] == path_id)
    assert other_path["completed_lessons"] == 0
    assert other_path["progress_percent"] == 0


def test_dashboard_path_cards_show_progress_and_continue_controls(client):
    html = client.get("/app/dashboard").text
    script = client.get("/static/js/achievements.js").text
    styles = client.get("/static/css/achievements.css").text
    assert "learning-paths/progress/me" in script
    assert "Continue learning" in script
    assert "path-progress-track" in script
    assert "path-progress-track" in styles
