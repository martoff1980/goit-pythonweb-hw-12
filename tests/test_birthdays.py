import pytest


@pytest.mark.asyncio
async def test_upcoming_birthdays(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/contacts/birthdays/upcoming", headers=headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)
