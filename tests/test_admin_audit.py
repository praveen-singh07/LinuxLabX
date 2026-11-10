from app.models.admin_audit import AdminAuditLog


def test_account_changes_record_actor_target_and_values(
    client, db, admin_headers, admin_user, test_user
):
    suspended = client.patch(
        f"/admin/users/{test_user.id}/status",
        headers=admin_headers,
        json={"is_active": False},
    )
    promoted = client.patch(
        f"/admin/users/{test_user.id}/role",
        headers=admin_headers,
        json={"role": "admin"},
    )

    assert suspended.status_code == 200, suspended.text
    assert promoted.status_code == 200, promoted.text
    response = client.get("/admin/audit-logs", headers=admin_headers)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["total"] == 2
    assert {entry["action"] for entry in body["items"]} == {
        "account.status",
        "account.role",
    }
    status_entry = next(
        entry for entry in body["items"] if entry["action"] == "account.status"
    )
    role_entry = next(
        entry for entry in body["items"] if entry["action"] == "account.role"
    )
    assert status_entry["actor_user_id"] == admin_user.id
    assert status_entry["actor_name"] == admin_user.name
    assert status_entry["target_user_id"] == test_user.id
    assert status_entry["target_name"] == test_user.name
    assert (status_entry["previous_value"], status_entry["new_value"]) == (
        "active",
        "suspended",
    )
    assert (role_entry["previous_value"], role_entry["new_value"]) == (
        "student",
        "admin",
    )
    assert status_entry["occurred_at"]


def test_no_op_account_updates_do_not_create_audit_entries(
    client, db, admin_headers, test_user
):
    status = client.patch(
        f"/admin/users/{test_user.id}/status",
        headers=admin_headers,
        json={"is_active": True},
    )
    role = client.patch(
        f"/admin/users/{test_user.id}/role",
        headers=admin_headers,
        json={"role": "student"},
    )

    assert status.status_code == 200, status.text
    assert role.status_code == 200, role.text
    assert db.query(AdminAuditLog).count() == 0


def test_audit_log_filters_paginates_and_requires_admin(
    client, admin_headers, auth_headers, test_user
):
    for path, body in (
        (f"/admin/users/{test_user.id}/status", {"is_active": False}),
        (f"/admin/users/{test_user.id}/role", {"role": "admin"}),
        (f"/admin/users/{test_user.id}/role", {"role": "student"}),
    ):
        changed = client.patch(path, headers=admin_headers, json=body)
        assert changed.status_code == 200, changed.text

    filtered = client.get(
        "/admin/audit-logs?action=account.role&search=Test%20Student&limit=1&offset=1",
        headers=admin_headers,
    )
    assert filtered.status_code == 200, filtered.text
    result = filtered.json()
    assert result["total"] == 2
    assert result["limit"] == 1
    assert result["offset"] == 1
    assert len(result["items"]) == 1
    assert result["items"][0]["action"] == "account.role"

    assert client.get("/admin/audit-logs").status_code == 401
    assert client.get("/admin/audit-logs", headers=auth_headers).status_code == 403
