def test_dashboard_renders_quiz_section_and_attempt_dialog(client):
    response = client.get("/app/dashboard")

    assert response.status_code == 200
    assert 'id="quiz-grid"' in response.text
    assert 'id="quiz-dialog"' in response.text
    assert 'id="quiz-history"' in response.text


def test_dashboard_loads_quiz_catalog_and_history_script(client):
    page = client.get("/app/dashboard")
    script = client.get("/static/js/achievements.js")

    assert page.status_code == 200
    assert "Quizzes" in page.text
    assert script.status_code == 200
    assert "api('/quizzes')" in script.text
    assert "api('/quizzes/attempts/me')" in script.text
    assert "submitCurrentQuiz" in script.text


def test_quiz_attempt_appears_in_dashboard_summary_and_history(
    client, login_headers, published_quiz_id
):
    quiz = client.get(f"/quizzes/{published_quiz_id}")
    answers = [
        {"question_id": question["id"], "selected_option_index": index}
        for index, question in enumerate(quiz.json()["questions"])
    ]
    submitted = client.post(
        f"/quizzes/{published_quiz_id}/attempts",
        headers=login_headers,
        json={"answers": answers},
    )
    assert submitted.status_code == 200, submitted.text

    dashboard = client.get("/dashboard", headers=login_headers)
    history = client.get("/quizzes/attempts/me", headers=login_headers)

    assert dashboard.status_code == 200, dashboard.text
    assert dashboard.json()["progress"]["quizzes_completed"] == 1
    assert history.status_code == 200, history.text
    assert len(history.json()) == 1
    assert history.json()[0]["quiz_id"] == published_quiz_id
    assert history.json()[0]["percentage"] == 100
