
import pytest
from httpx import AsyncClient
from asgi_lifespan import LifespanManager
from main import app
from services.deps import require_role
from fastapi import status
from sqlalchemy.future import select
from models import User, Role
from crud import get_user_by_id

@pytest.mark.asyncio
async def test_user_cannot_access_admin_users(client, user_token, fresh_loop):
    response = await client.get(
        "/admin/users/api",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403
    assert "detail" in response.json()
    
@pytest.mark.asyncio
async def test_admin_can_access_admin_users(client, admin_token,fresh_loop):
    response = await client.get(
        "/admin/users/api",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "id" in data[0]
        assert "email" in data[0]


@pytest.mark.asyncio
async def test_admin_edit_user_get_and_post(client: AsyncClient, token: str, db, fresh_loop):
    test_user = User(
        email="edit_user@example.com",
        first_name="Test",
        last_name="User",
        role=Role.user,
        is_active=True,
        is_verified=True,
        password_hash="hashedpassword"
    )
    db.add(test_user)
    await db.commit()
    await db.refresh(test_user)

    user_id = test_user.id

    headers = {"Authorization": f"Bearer {token}"}

    response_get = await client.get(f"/users/{user_id}/edit", headers=headers)
    assert response_get.status_code == status.HTTP_200_OK
    assert "edit_user.html" in response_get.text  # проверка шаблона
    assert "Test" in response_get.text  # проверка, что данные пользователя в шаблоне

    form_data = {
        "role": Role.admin.value,  
        "is_active": "on",         
        "is_verified": "on"        
    }

    response_post = await client.post(
        f"/users/{user_id}/edit",
        data=form_data,
        headers=headers,
        follow_redirects=False
    )

    assert response_post.status_code == status.HTTP_303_SEE_OTHER
    assert response_post.headers["location"] == "/admin/users"

    updated_user = await db.get(User, user_id)
    assert updated_user.role == Role.admin
    assert updated_user.is_active is True
    assert updated_user.is_verified is True

@pytest.mark.asyncio
async def test_admin_delete_user(client: AsyncClient, db, admin_token):
    new_user = User(
        email="delete_me@test.com",
        first_name="Delete",
        last_name="Me",
        is_active=True,
        is_verified=True,
        role="user",
        password="hashed_password"
    )
    async with db() as session:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        user_id = new_user.id

    response = await client.post(
        f"/users/{user_id}/delete",
        cookies={"access_token": admin_token},
        follow_redirects=False
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/admin/users"

    async with db() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        deleted_user = result.scalar_one_or_none()
        assert deleted_user is None
