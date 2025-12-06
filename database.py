# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker, declarative_base
# from config import get_settings

# engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
# AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
# Base = declarative_base()


# async def get_db():
#     async with AsyncSessionLocal() as session:
#         yield session

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from config import get_settings

Base = declarative_base()
_engine = None
_AsyncSessionLocal = None

def get_engine():
    """ Асинхроний двіжок БД """
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.DATABASE_URL, echo=False, future=True
        )
    return _engine

def get_session():
    """ Sessionmaker для асинхроних сесій """
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        _AsyncSessionLocal = sessionmaker(
            get_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _AsyncSessionLocal

async def get_db():
    """ Асинхрона для отримання сессії """
    AsyncSessionLocal = get_session()
    async with AsyncSessionLocal() as session:
        yield session
