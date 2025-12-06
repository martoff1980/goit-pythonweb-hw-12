import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
import models, crud

@pytest.mark.asyncio
async def test_create_contact(client, token, db, fresh_loop):
    form_data = {
        "first_name": "John",
        "last_name": "Smith",
        "email": "john@gmail.com",
        "phone": "123456789",
        "birthday": "1990-04-01",
        "information": "friend",
    }

    response = await client.post("/contacts/add",data=form_data , cookies={"access_token": token},follow_redirects=False,)  # треба спіймати 303
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers["location"] == "/contacts"

    q = await db.execute(select(models.Contact).where(models.Contact.email == "john@example.com"))
    contact = q.scalar_one_or_none()

    assert contact is not None
    assert contact.first_name == "John"
    assert contact.last_name == "Smith"
    assert contact.phone == "123456789"
    assert str(contact.date_of_birth) == "1990-01-01"
    assert contact.information == "friend"