import pytest


def test_user_cannot_update_avatar(client, user_token):
    response = client.patch(
        "/users/default-avatar",
        json={"new_avatar": "link.jpg"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403


def test_admin_can_update_avatar(client, admin_token):
    response = client.patch(
        "/users/default-avatar",
        json={"new_avatar": "link.jpg"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

