from fastapi import HTTPException
from sqlalchemy import select, or_, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime, timedelta
from models import Contact, User
from schemas import ContactCreate, ContactUpdate
from typing import List, Optional


async def create_contact(
    db: AsyncSession, contact: ContactCreate, owner_id: int
) -> Contact:
    """
    
    Створення нового контакту в базі даних.
    
    :param db: AsyncSession SQLAlchemy
    :param contact: Схема ContactCreate з даними нового контакту
    :param owner_id: Ідентифікатор власника контакту
    :return: Екземпляр створеного контакту
    
    """
    
    contact_data = contact.dict()
    contact_data["owner_id"] = owner_id
    db_obj = Contact(**contact_data)
    db.add(db_obj)
    try:
        await db.commit()
        await db.refresh(db_obj)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=400, detail="Contact with this email already exists."
        )
    return db_obj


async def get_contact(db: AsyncSession, contact_id: int) -> Optional[Contact]:
    """ 
    
    Отримання контакту за його ідентифікатором.
    
    :param db: AsyncSession SQLAlchemy
    :param contact_id: Ідентифікатор контакту
    
    """
    
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    return result.scalars().first()


async def list_contacts(
    db: AsyncSession,
    user_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
) -> List[Contact]:
    """
    
    Отримання списку контактів з можливістю фільтрації.
    
    :param db: AsyncSession SQLAlchemy
    :param user_id: Ідентифікатор користувача
    :param first_name: Фільтр за ім'ям (необов'язково)
    :param last_name: Фільтр за прізвищем (необов'язково)
    :param email: Фільтр за email (необов'язково)
    
    """
    
    q = select(Contact).where(Contact.owner_id == user_id)

    conditions = []
    if first_name:
        conditions.append(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        conditions.append(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        conditions.append(Contact.email.ilike(f"%{email}%"))
    if conditions:
        q = q.where(or_(*conditions))
    result = await db.execute(q.order_by(Contact.last_name, Contact.first_name))
    return result.scalars().all()


async def update_contact(
    db: AsyncSession, contact_id: int, contact: ContactUpdate
) -> Optional[Contact]:
    """
    
    Оновлення інформації про контакт.
    
    :param db: AsyncSession SQLAlchemy
    :param contact_id: Ідентифікатор контакту
    :param contact: Схема ContactUpdate з оновленими даними контакту
    
    """
    stmt = select(Contact).where(Contact.id == contact_id)
    res = await db.execute(stmt)
    db_obj = res.scalars().first()
    if not db_obj:
        return None
    for field, value in contact.dict(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def delete_contact(db: AsyncSession, contact_id: int) -> bool:
    """
    
    Видалення контакту за його ідентифікатором.
    
    :param db: AsyncSession SQLAlchemy
    :param contact_id: Ідентифікатор контакту
    
    """
    
    stmt = select(Contact).where(Contact.id == contact_id)
    res = await db.execute(stmt)
    db_obj = res.scalars().first()
    if not db_obj:
        return False
    await db.delete(db_obj)
    await db.commit()
    return True


async def search_contacts(db: AsyncSession, query: str, user_id: int):
    """
    
    Пошук контактів за ім'ям, прізвищем або email.
    
    :param db: AsyncSession SQLAlchemy
    :param query: Пошуковий запит
    :param user_id: Ідентифікатор користувача
    
    """
    
    like = f"%{query.lower()}%"
    result = await db.execute(
        select(Contact)
        .where(Contact.owner_id == user_id)
        .where(
            or_(
                Contact.first_name.ilike(like),
                Contact.last_name.ilike(like),
                Contact.email.ilike(like),
            )
        )
    )
    return result.scalars().all()


async def upcoming_birthdays(
    db: AsyncSession, user_id: int, days: int = 7
) -> List[Contact]:
    """ 
    
    Отримання списку контактів з найближчими днями народження.
    
    :param db: AsyncSession SQLAlchemy
    :param user_id: Ідентифікатор користувача
    :param days: Кількість днів для пошуку найближчих днів народження
    
    """
    # Вибірка всіх контактів
    result = await db.execute(select(Contact).where(Contact.owner_id == user_id))
    contacts = result.scalars().all()

    today = date.today()
    next_week = today + timedelta(days=days)

    # Фільтруємо на Python
    upcoming = []

    for contact in contacts:
        if not contact.date_of_birth:
            continue

        # День народження цього року
        bday_this_year = contact.date_of_birth.replace(year=today.year)

        # Якщо вже минув, то наступного року
        if bday_this_year < today:
            bday_this_year = bday_this_year.replace(year=today.year + 1)

        # Інтервал між сьогодні і через 7 днів
        if today <= bday_this_year <= next_week:
            upcoming.append((bday_this_year, contact))

    # Сортуання за найближчою датою народження
    upcoming.sort(key=lambda x: x[0])

    # Повертання тільки контакти (без дати)
    return [contact for _, contact in upcoming]


async def get_user_by_id(db: AsyncSession, user_id: int):
    """ 
    
    Отримання користувача за його ідентифікатором.
    
    :param db: AsyncSession SQLAlchemy
    :param user_id: Ідентифікатор користувача
    
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def update_avatar(db: AsyncSession, current_user, avatar_url: str):
    """
    
    Обновлення аватару користувача в базе даних.

    :param db: AsyncSession SQLAlchemy
    :param current_user: Поточний користувач
    :param avatar_url: URL нового аватара
    
    """
    stmt = (
        update(User)
        .where(User.id == current_user.id)
        .values(avatar_url=avatar_url)
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(stmt)
    await db.commit()


async def list_users(db: AsyncSession, q: str | None = None):
    """
    
    Повертає список всіх користувачів.
    
    Якщо передано q — виконує пошук за email або full_name.
    
    """
    stmt = select(User)

    if q:
        q_like = f"%{q}%"
        stmt = stmt.where((User.email.ilike(q_like)) | (User.full_name.ilike(q_like)))

    # stmt = stmt.order_by(User.created_at.desc())  # сортування за датою створення
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_user_role_and_status(
    db: AsyncSession,
    user: User,
    role: str | None = None,
    is_active: bool | None = None,
    is_verified: bool | None = None,
):
    """

    Оновлення ролі та статусу користувача.
    
    :param db: AsyncSession SQLAlchemy
    :param user: Екземпляр користувача для оновлення
    :param role: Нова роль користувача (необов'язково)

    """

    if role is not None:
        user.role = role
    if is_active is not None:
        user.is_active = is_active
    if is_verified is not None:
        user.is_verified = is_verified
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User):
    """ 
    
    Видалення користувача з бази даних.
    
    :param db: AsyncSession SQLAlchemy
    :param user: Екземпляр користувача для видалення
    
    """
    await db.delete(user)
    await db.commit()
    return True


