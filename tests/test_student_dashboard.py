def _create_learning_path_with_lesson(client, admin_headers):
    path_response = client.post(
        "/admin/learning-paths",
        headers=admin_headers,
        json={
            "title": "Linux Foundations",
            "description": "Start with essential Linux commands.",
            "display_order": 0,
            "is_published": True,
        },
    )
    assert path_response.status_code == 201, path_response.text
    path_id = path_response.json()["id"]

    topic_response = client.post(
        f"/admin/learning-paths/{path_id}/topics",
        headers=admin_headers,
        json={
            "title": "Getting Started",
            "description": "First steps in the terminal.",
            "display_order": 0,
            "is_published": True,
        },
    )
    assert topic_response.status_code == 201, topic_response.text
    topic_id = topic_response.json()["id"]

    lesson_response = client.post(
        "/admin/lessons",
        headers=admin_headers,
        json={
            "title": "Print the current directory",
            "description": "Learn where you are in the filesystem.",
            "command": "pwd",
            "syntax": "pwd",
            "examples": [{"command": "pwd", "output": "/home/student"}],
            "expected_output": "/home/student",
            "options": [],
            "tips": ["pwd prints the working directory."],
            "common_mistakes": [],
            "difficulty": "beginner",
            "display_order": 0,
            "is_published": True,
        },
    )
    assert lesson_response.status_code == 201, lesson_response.text
    lesson_id = lesson_response.json()["id"]

    link_response = client.put(
        f"/admin/learning-paths/topics/{topic_id}/lessons",
        headers=admin_headers,
        json={"lesson_id": lesson_id, "display_order": 0},
    )
    assert link_response.status_code == 200, link_response.text
    return path_id, lesson_id


def test_dashboard_page_and_static_assets_are_served(client):
    page = client.get("/app/dashboard")
    script = client.get("/static/js/achievements.js")

    assert page.status_code == 200
    assert "Student Dashboard" in page.text
    assert script.status_code == 200
    assert "Learning paths" in page.text
    assert "Global leaderboard" in page.text
    assert "stat-streak" in page.text


def test_admin_content_studio_page_and_assets_are_served(client):
    page = client.get("/app/admin")
    script = client.get("/static/js/admin.js")
    styles = client.get("/static/css/admin.css")

    assert page.status_code == 200
    assert "Admin Content Studio" in page.text
    assert "Challenges" in page.text
    assert script.status_code == 200
    assert "admin/quizzes" in script.text
    assert styles.status_code == 200


def test_dashboard_api_requires_authentication(client):
    response = client.get("/dashboard")
    assert response.status_code == 401


def test_new_student_dashboard_starts_with_zero_progress(
    client, login_headers, test_user
):
    response = client.get("/dashboard", headers=login_headers)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["user_id"] == test_user.id
    assert body["xp"] == {"total_xp": 0, "level": 1}
    assert body["progress"]["lessons_completed"] == 0
    assert body["progress"]["progress_percentage"] == 0


def test_dashboard_lists_learning_path_and_reflects_lesson_completion(
    client, admin_headers, login_headers
):
    path_id, lesson_id = _create_learning_path_with_lesson(client, admin_headers)

    paths = client.get("/learning-paths", headers=login_headers)
    assert paths.status_code == 200, paths.text
    assert any(item["id"] == path_id for item in paths.json())

    path = client.get(f"/learning-paths/{path_id}", headers=login_headers)
    assert path.status_code == 200, path.text
    assert path.json()["topics"][0]["lessons"][0]["id"] == lesson_id

    completed = client.post(
        f"/lessons/{lesson_id}/complete", headers=login_headers
    )
    assert completed.status_code == 200, completed.text

    dashboard = client.get("/dashboard", headers=login_headers)
    assert dashboard.status_code == 200, dashboard.text
    assert dashboard.json()["progress"]["lessons_completed"] == 1
    assert dashboard.json()["xp"]["total_xp"] == 10
