from fastapi import Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.auth import decode_access_token
from jose import JWTError
from sqlalchemy.future import select
from cache.user_cache import get_cached_user, cache_user
from config import get_settings
from jose import JWTError, jwt
import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_dep_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Декодування JWT
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except (JWTError, Exception):
        raise credentials_exception

    # Кешування з Redis
    cached = await get_cached_user(user_id)
    if cached:
        return cached  # ⚡ взяли з кешу

    # Інакше — з БД
    stmt = select(models.User).where(models.User.id == user_id)
    res = await db.execute(stmt)
    user = res.scalars().first()
    if not user:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Сохраняемо в Redis
    await cache_user(user)

    return user


def require_role(required_role: models.Role):
    settings=get_settings()
    
    def wrapper(request: Request):
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token"
            )
        #  якщо в токені "Bearer <token>", убираемо префікс
        if token.startswith("Bearer "):
            token = token[7:]
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        role = payload.get("role")
        if role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
        return payload

    return wrapper
