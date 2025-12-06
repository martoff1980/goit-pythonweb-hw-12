import pytest
from services.auth import create_reset_token


@pytest.mark.asyncio
async def test_reset_password_request(client):
    resp = await client.post(
        "/users/request-password-reset", json={"email": "test@gmail.com"}
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_reset_password(client):
    token = create_reset_token({"sub": "test@gmail.com"})
    resp = await client.post(
        "/auth/reset-password", json={"token": token, "new_password": "NewPass123"}
    )
    assert resp.status_code == 200
