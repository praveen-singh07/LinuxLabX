from app.core.security import hash_password
from app.models.user import User


def test_admin_user_directory_search_filters_and_paginates(
    client, db, admin_headers, test_user, admin_user
):
    test_user.is_active = False
    db.commit()

    response = client.get(
        "/admin/users?search=student%40example.com&status_filter=suspended&limit=1&offset=0",
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["id"] == test_user.id
    assert body["items"][0]["is_active"] is False


def test_admin_can_suspend_and_reactivate_student(
    client, admin_headers, test_user
):
    suspended = client.patch(
        f"/admin/users/{test_user.id}/status",
        headers=admin_headers,
        json={"is_active": False},
    )
    assert suspended.status_code == 200, suspended.text
    assert suspended.json()["is_active"] is False

    activated = client.patch(
        f"/admin/users/{test_user.id}/status",
        headers=admin_headers,
        json={"is_active": True},
    )
    assert activated.status_code == 200, activated.text
    assert activated.json()["is_active"] is True


def test_admin_cannot_suspend_own_account(client, admin_headers, admin_user):
    response = client.patch(
        f"/admin/users/{admin_user.id}/status",
        headers=admin_headers,
        json={"is_active": False},
    )

    assert response.status_code == 400


def test_admin_can_suspend_another_admin_while_remaining_active(
    client, db, admin_headers, admin_user
):
    other_admin = User(
        name="Second Admin",
        email="second.admin@example.com",
        password_hash=hash_password("TestPassword123!"),
        role="admin",
        is_active=True,
    )
    db.add(other_admin)
    db.commit()
    db.refresh(other_admin)

    response = client.patch(
        f"/admin/users/{other_admin.id}/status",
        headers=admin_headers,
        json={"is_active": False},
    )

    assert response.status_code == 200, response.text
    assert response.json()["is_active"] is False


def test_admin_cannot_demote_own_administrator_role(
    client, admin_headers, admin_user
):
    response = client.patch(
        f"/admin/users/{admin_user.id}/role",
        headers=admin_headers,
        json={"role": "student"},
    )

    assert response.status_code == 400


def test_admin_can_promote_student_and_old_token_requires_new_login(
    client, admin_headers, auth_headers, test_user
):
    response = client.patch(
        f"/admin/users/{test_user.id}/role",
        headers=admin_headers,
        json={"role": "admin"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["role"] == "admin"
    assert client.get("/admin/users", headers=auth_headers).status_code == 401

    new_login = client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "TestPassword123!"},
    )
    refreshed_headers = {
        "Authorization": f"Bearer {new_login.json()['access_token']}"
    }
    assert client.get("/admin/users", headers=refreshed_headers).status_code == 200


def test_admin_can_demote_another_admin_while_remaining_active(
    client, db, admin_headers, admin_user
):
    other_admin = User(
        name="Second Admin",
        email="second.admin@example.com",
        password_hash=hash_password("TestPassword123!"),
        role="admin",
        is_active=True,
    )
    db.add(other_admin)
    db.commit()
    db.refresh(other_admin)

    response = client.patch(
        f"/admin/users/{other_admin.id}/role",
        headers=admin_headers,
        json={"role": "student"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["role"] == "student"


def test_student_cannot_access_user_management_or_platform_overview(
    client, auth_headers
):
    users = client.get("/admin/users", headers=auth_headers)
    overview = client.get("/admin/overview", headers=auth_headers)

    assert users.status_code == 403
    assert overview.status_code == 403


def test_admin_overview_counts_users_and_content(client, admin_headers):
    response = client.get("/admin/overview", headers=admin_headers)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["users_total"] == 1
    assert body["users_active"] == 1
    assert body["users_suspended"] == 0
    assert body["lessons"] == 0


