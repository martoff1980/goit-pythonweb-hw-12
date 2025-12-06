from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class ContactBase(BaseModel):
    """
    Схема базової інформації про контакт.

    :param first_name: Ім'я контакту.
    :param last_name: Прізвище контакту.
    :param email: Email контакту.
    :param phone: Номер телефону.
    :param date_of_birth: Дата народження контакту.
    :param information: Додаткова інформація про контакт.

    """

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=3, max_length=50)
    date_of_birth: Optional[date] = None  # date
    information: Optional[str] = None
    # owner_id: int  # ID користувача-власника контакту


class ContactCreate(ContactBase):

    pass


class ContactUpdate(BaseModel):
    """
    Схема для оновлення інформації про контакт.

    :param first_name: Ім'я контакту.
    :param last_name: Прізвище контакту.
    :param email: Email контакту.
    :param phone: Номер телефону.
    :param date_of_birth: Дата народження контакту.
    :param information: Додаткова інформація про контакт.

    """

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=3, max_length=50)
    date_of_birth: Optional[date] = None
    information: Optional[str] = None


class ContactOut(ContactBase):
    """
    Схема виведення інформації про контакт.

    :param id: Унікальний ідентифікатор контакту.
    :param owner_id: Ідентифікатор власника контакту (користувача).

    """

    id: int
    owner_id: int
    model_config = ConfigDict(from_attributes=True)


class ContactInDB(ContactBase):
    """
    Схема для внутрішнього використання, що включає ID контакту.

    :param id: Унікальний ідентифікатор контакту.
    :param model_config: Конфігурація моделі для Pydantic.

    """

    id: int
    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    """
    Схема базової інформації про користувача.

    :param email: Email користувача.
    :param full_name: Повне ім'я користувача.

    """

    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    """
    Схема для створення нового користувача.

    :param email: Email користувача.
    :param password: Пароль користувача.

    """

    email: EmailStr
    password: str = Field(..., min_length=6)


class UserOut(UserBase):
    """
    Схема виведення інформації про користувача.

    :param id: Унікальний ідентифікатор користувача.
    :param is_active: Статус активності користувача.
    :param is_verified: Статус верифікації користувача.
    :param avatar_url: URL аватарки користувача.

    """

    id: int
    is_active: bool
    is_verified: bool
    avatar_url: str | None = None
    model_config = ConfigDict(from_attributes=True)


# Token schemas
class Token(BaseModel):
    """
    Схема токена доступу.

    :param access_token: Токен доступу.
    :param token_type: Тип токена.

    """

    access_token: str
    token_type: str = "bearer"


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
