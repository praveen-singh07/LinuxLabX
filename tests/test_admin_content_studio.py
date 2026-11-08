def test_admin_can_view_and_unlink_lessons_from_topic(
    client, admin_headers, auth_headers
):
    path = client.post(
        "/admin/learning-paths",
        headers=admin_headers,
        json={"title": "Linux Basics", "description": "", "display_order": 0},
    ).json()
    topic = client.post(
        f"/admin/learning-paths/{path['id']}/topics",
        headers=admin_headers,
        json={"title": "Files", "description": "", "display_order": 0},
    ).json()
    lesson = client.post(
        "/admin/lessons",
        headers=admin_headers,
        json={
            "title": "List files", "description": "", "command": "ls",
            "syntax": "ls", "examples": [], "expected_output": "",
            "options": [], "tips": [], "common_mistakes": [],
            "difficulty": "beginner", "display_order": 0,
        },
    ).json()
    linked = client.put(
        f"/admin/learning-paths/topics/{topic['id']}/lessons",
        headers=admin_headers,
        json={"lesson_id": lesson["id"], "display_order": 2},
    )

    assert linked.status_code == 200
    links = client.get(
        f"/admin/learning-paths/topics/{topic['id']}/lessons",
        headers=admin_headers,
    )
    assert links.status_code == 200
    assert links.json() == [{"lesson_id": lesson["id"], "title": "List files", "display_order": 2}]

    removed = client.delete(
        f"/admin/learning-paths/topics/{topic['id']}/lessons/{lesson['id']}",
        headers=admin_headers,
    )
    assert removed.status_code == 204
    assert client.get(
        f"/admin/learning-paths/topics/{topic['id']}/lessons",
        headers=admin_headers,
    ).json() == []
    assert client.get(
        f"/admin/learning-paths/topics/{topic['id']}/lessons",
        headers=auth_headers,
    ).status_code == 403


def test_admin_studio_page_loads_for_signed_out_visitors(client):
    response = client.get("/app/admin")

    assert response.status_code == 200
    assert "Admin Content Studio" in response.text
