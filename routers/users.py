from fastapi import (
    APIRouter,
    Request,
    Depends,
    HTTPException,
    status,
    Cookie,
    UploadFile,
    File,
    Form,
)
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse, JSONResponse
from slowapi.util import get_remote_address
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from services.auth import get_token_from_cookie, create_reset_token
from services.email import (
    send_verification_email,
    create_email_confirmation_token,
    get_user_by_email,
    send_reset_email,
)
from database import get_db
from models import User, Role
from config import get_settings
from jose import jwt, JWTError
from middleware.rate_limit import limiter
from schemas import ResetPasswordRequest
from services.auth import get_password_hash
import crud
import cloudinary.uploader
from typing import Optional
import redis
import redis.asyncio as aioredis
import cloudinary
import cloudinary.uploader
from services.deps import require_role
import tempfile,os

settings=get_settings()

templates = Jinja2Templates(directory="templates")

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

RATE_LIMIT = 5  # requests
RATE_WINDOW = 60  # seconds

router = APIRouter(prefix="/users", tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# create redis connection pool
redis = None


async def get_redis():
    global redis
    if redis is None:
        redis = await aioredis.from_url(settings.REDIS_URL)
    return redis


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_token_from_cookie),  # Bearer из Authorization
    access_token: str = Cookie(None),  # Cookie
):
    actual_token = token or access_token

    if actual_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    try:
        payload = jwt.decode(
            actual_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: int = int(payload.get("sub"))

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user = await db.get(User, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # 🚫 Заборона доступу, якщо email не підтверджений
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Email is not verified"
        )

    return user


async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()  # result.scalar_one_or_none()


@router.get("/me")
@limiter.limit(f"{RATE_LIMIT}/{RATE_WINDOW}seconds")
async def get_me(request: Request, current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "avatar_url": current_user.avatar_url,
    }


@router.post("/resend-confirmation")
@limiter.limit(f"{RATE_LIMIT}/{RATE_WINDOW}seconds")  # rate limit
async def resend_confirmation(
    request: Request, email: EmailStr = Form(...), db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")

    token = create_email_confirmation_token(user.email)
    await send_verification_email(user.email, token)

    return RedirectResponse(url=f"/login?info=email_sent", status_code=303)


@router.get("/reset-password")
async def reset_password_page(
    request: Request, token: str, email: Optional[str] = None
):
    return templates.TemplateResponse(
        "reset_password.html", {"request": request, "token": token, "email": email}
    )


@router.post("/reset-password")
async def reset_password(
    token: str = Form(...),
    new_password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = jwt.decode(
            token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = await get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = get_password_hash(new_password)
    await db.flush()
    await db.commit()

    return RedirectResponse(url="/login?info=password_reset_done", status_code=303)


@router.get("/request-password-reset")
async def reset_password_page_test(request: Request, email: str):
    return templates.TemplateResponse(
        "reset_password.html",
        {"request": request, "email": email},  # Додано порожні значення
    )


@router.post("/request-password-reset")
async def request_password_reset(
    request: Request, email: EmailStr = Form(...), db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = create_reset_token(user.email)
    await send_reset_email(user.email, reset_token)
    return templates.TemplateResponse("sent_email.html", {"request": request})

# в users router
@router.post("/default-avatar", dependencies=[Depends(require_role(Role.admin))], status_code=201)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),    
):
    contents = await file.read()
    res = cloudinary.uploader.upload(
        contents, folder="avatars", public_id=f"user_{current_user.id}", overwrite=True
    )
    url = res.get("secure_url")
    await crud.update_avatar(db, current_user, url)
    return {"avatar_url": url}


@router.patch("/default-avatar")
async def update_default_avatar(
    new_avatar: str, payload=Depends(require_role(Role.admin))
):
    # TODO: Cloudinary upload or update default avatar logic
    return {"message": "Default avatar updated by admin only"}

