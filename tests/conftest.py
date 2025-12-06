import os, sys, asyncio
import pytest
import pytest_asyncio
from .test_token import generate_test_token
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from database import get_db, Base
from main import app
from dotenv import load_dotenv
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager
from models import User
from services.email import send_verification_email
from services.auth import get_password_hash,create_access_token
from unittest.mock import AsyncMock, patch

os.environ["SMTP_USER"] = "test@example.com"
os.environ["SMTP_PASS"] = "test"
os.environ["SMTP_HOST"] = "localhost"
os.environ["SMTP_PORT"] = "1025"
os.environ["SECRET_ADMIN"] = "test"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://contacts_db_auth_cache:1234@localhost:6452/contacts_db"
os.environ["SECRET_KEY"] = "test"
os.environ["SECRET_EMAIL"] = "test"
os.environ["ALGORITHM"] = "HS256"
os.environ["SERVER_PORT"] = "8022"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"

# load_dotenv(".env.test")


TEST_SQLALCHEMY_DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_async_engine(TEST_SQLALCHEMY_DATABASE_URL, echo=True, future=True)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

def pytest_configure(config):
    """Настройки pytest перед запуском тестов"""
    config.option.asyncio_default_fixture_loop_scope = "function"

@pytest_asyncio.fixture
async def fresh_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        yield loop
    finally:
        loop.close()
    
@pytest.fixture(scope="session", autouse=True)
def set_event_loop_policy():
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        

@pytest_asyncio.fixture(scope="function", autouse=True)
async def prepare_database():
    """
    Створення таблиць до тестів, очистка після.
    Працює один раз за всю тестову сессію.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Після всіх тестів видалення таблиці
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

engine_test = create_async_engine(TEST_SQLALCHEMY_DATABASE_URL, echo=True)
AsyncSessionTest = sessionmaker(
    bind=engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest_asyncio.fixture
async def db():
    async with AsyncSessionTest() as session:
        yield session

# @pytest_asyncio.fixture(scope="function")
# async def db():
#     """
#     Нова БД-сессія для кожного тесту.
#     """
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     async_session = TestingSessionLocal()
#     yield async_session
#     await async_session.close()

@pytest_asyncio.fixture(autouse=True)
def mock_external_services():
    with patch("cache.redis_client", new=AsyncMock()):
        with patch("services.email", new=AsyncMock()):
            yield
        
@pytest_asyncio.fixture(scope="function")
async def client(db, fresh_loop):
    """
    Подміна залежності get_db → тестову БД.
    """
    # Кліент для реального додотку (підключення локального серверу для тестування)
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    
    app.router.on_startup.clear()
    app.router.on_shutdown.clear()
    
    transport = ASGITransport(app=app)
    
    with patch("cache.redis_client", new=AsyncMock()), \
         patch("services.email.send_verification_email", new=AsyncMock()):

        async with LifespanManager(app):
            async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
                yield ac            
                
@pytest_asyncio.fixture(scope="function")
async def token(db):
    email = "test@example.com"
    password = "StrongPass123!"
    payload = {"email": email, "password": password}

    user=User(email=email, hashed_password=get_password_hash(password),
                is_active=True, is_verified=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    token = generate_test_token(email)
    return token

@pytest_asyncio.fixture
async def user_token(token):
    return token

@pytest_asyncio.fixture
async def admin_token(db):
    user = User(email="admin@example.com", is_superuser=True, hashed_password="fake")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return  create_access_token(subject=user.email, role="admin")