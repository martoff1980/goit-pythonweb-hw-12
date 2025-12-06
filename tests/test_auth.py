import pytest


@pytest.mark.asyncio
async def test_register_user(client):
    payload = {"email": "test@example.com", "password": "MyPass123!", "full_name": "Test User"}

    response = await client.post("/register", data=payload)
    assert response.status_code == 303
    assert response.headers["location"] == "/login?success=1"

@pytest.mark.asyncio
async def test_login_unverified(client):
    payload = {"email": "test@example.com", "password": "MyPass123!","full_name": "Test User"}

    response = await client.post("/login", data=payload)
    assert response.status_code == 401
    assert (
        response.json()["detail"] == "Email is not verified. Please check your inbox."
    )
