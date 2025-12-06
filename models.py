from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    Enum,
)
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from enum import Enum as PyEnum


class Contact(Base):
    """
    Модель контакту.

    :ivar id: Унікальний ідентифікатор контакту.
    :ivar first_name: Ім'я контакту.
    :ivar last_name: Прізвище контакту.
    :ivar email: Email контакту.
    :ivar phone: Номер телефону.
    :ivar date_of_birth: Дата народження контакту.
    :ivar information: Додаткова інформація про контакт.
    :ivar owner_id: Ідентифікатор власника контакту (користувача).
    :ivar owner: Власник контакту (користувач).

    """

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    information = Column(String, nullable=True)

    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    owner = relationship("User", back_populates="contacts")


class Role(str, PyEnum):
    """

    Ролі користувачів.

    :ivar user: Звичайний користувач.
    :ivar admin: Адміністратор.

    """

    user = "user"
    admin = "admin"


class User(Base):
    """

    Модель користувача.
    
    :ivar id: Унікальний ідентифікатор користувача.
    :ivar email: Email користувача.
    :ivar full_name: Повне ім'я користувача.
    :ivar hashed_password: Хешований пароль користувача.
    :ivar is_active: Статус активності користувача.
    :ivar is_verified: Статус верифікації користувача.
    :ivar avatar_url: URL аватарки користувача.
    :ivar verification_token: Токен для верифікації email користувача.
    :ivar role : Роль користувача (user або admin).

    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, index=True, nullable=False)
    full_name = Column(String(200), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    avatar_url = Column(String(512), nullable=True)
    verification_token = Column(
        String(255), nullable=True
    )  # token for email verification
    role = Column(Enum(Role), default=Role.user)

    contacts = relationship(
        "Contact", back_populates="owner", cascade="all, delete-orphan"
    )
