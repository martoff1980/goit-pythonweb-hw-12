from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from email.message import EmailMessage
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models import Contact, User
from database import get_db
import smtplib
from datetime import datetime, timedelta

_settings=None

def get_email_settings():
    global _settings
    if _settings is None:
        from config import get_settings
        _settings = get_settings()
    return _settings

router = APIRouter(prefix="/auth", tags=["auth"])

settings=get_email_settings()

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASS,
    MAIL_FROM=settings.SMTP_USER,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_FROM_NAME="Contacts App",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)


# helper to send verification email (simple SMTP)
async def send_verification_email(to_email: str, token: str):
    settings = get_email_settings()
    verify_link = (
        f"http://localhost:{settings.SERVER_PORT}/auth/confirm-email?token={token}"
    )
    msg = EmailMessage()
    msg["Subject"] = "Verify your account"
    msg["From"] = "no-reply@example.com"
    msg["To"] = to_email
    msg.set_content(f"Click to verify: {verify_link}")
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        smtp.send_message(msg)


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()  # .scalar_one_or_none()


def create_email_confirmation_token(email: str):
    settings = get_email_settings()
    expire = datetime.utcnow() + timedelta(hours=24)
    payload = {"sub": email, "exp": expire}
    token = jwt.encode(payload, settings.SECRET_EMAIL, algorithm=settings.ALGORITHM)
    return token


def verify_email_token(token: str):
    settings = get_email_settings()
    try:
        payload = jwt.decode(
            token, settings.SECRET_EMAIL, algorithms=[settings.ALGORITHM]
        )
        return payload["sub"]
    except ExpiredSignatureError:
        # "Token expired"
        return None
    except JWTError as e:
        # "Invalid token:" + str(e)
        return None


@router.get("/confirm-email")
async def confirm_email(token: str = Query(...), db: AsyncSession = Depends(get_db)):
    email = verify_email_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = await get_user_by_email(db, email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        return RedirectResponse("/login?info=already_verified", status_code=303)
        # raise HTTPException(status_code=400, detail="Email already confirmed")

    # Оновлення флагу is_verified
    user.is_verified = True
    db.add(user)
    await db.commit()

    return RedirectResponse("/login?info=email_verified", status_code=303)


async def send_reset_email(to_email: str, token: str):
    settings = get_email_settings()
    reset_link = f"http://localhost:{settings.SERVER_PORT}/users/reset-password?email={to_email}&token={token}"
    # mail sending code here (MailHog / SMTP)
    msg = EmailMessage()
    msg["Subject"] = "Verify your account"
    msg["From"] = "no-reply@example.com"
    msg["To"] = to_email
    msg.set_content(f"Click to reset your password: {reset_link}")
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        smtp.send_message(msg)
