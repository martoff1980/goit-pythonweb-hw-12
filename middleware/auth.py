from fastapi import FastAPI, Request, Form, Depends, Query, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from jose import JWTError, jwt
from config import get_settings
from starlette.middleware.base import BaseHTTPMiddleware
from services.auth import create_access_token
from routers.users import get_user_by_id
from database import get_session

settings=get_settings()

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # path = request.url.path
        path = request.url.path.rstrip("/")

        # Маршрути без захисту
        public_paths = [
            "/",
            "/login",
            "/register",
            "/static",
            "/favicon.ico",
            "/auth/token",
            "/auth/confirm-email",
            "/users/resend-confirmation",
            "/users/request-password-reset",
            "/verify-info",
            "/resend-confirmation",
            "/docs",
            "/openapi.json",
        ]

        if any(path == pub or path.startswith(pub + "/") for pub in public_paths):
            return await call_next(request)

        # Отримання токенів з cookie
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        # 🔥 Якщо cookie видалени — НЕ авторизуємося!
        if not access_token and not refresh_token:
            return RedirectResponse("/login", status_code=303)

        user_id = None
        payload = None

        # Перевірка access token
        if access_token:
            try:
                payload = jwt.decode(
                    access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
                )
                user_id = payload.get("sub")
                return await call_next(request)
            except:
                access_token = None  # invalid token

        # Перевірка refresh token
        if refresh_token:
            try:
                payload = jwt.decode(
                    refresh_token,
                    settings.REFRESH_SECRET_KEY,
                    algorithms=[settings.ALGORITHM],
                )
                user_id = payload.get("sub")
                new_access = create_access_token(user_id)
                response = await call_next(request)
                response.set_cookie(
                    "access_token",
                    new_access,
                    httponly=True,
                    secure=True,
                    samesite="None",
                    path="/",
                )
                return response
            except Exception:
                return RedirectResponse("/login", status_code=303)

        if not user_id:
            return RedirectResponse("/login", status_code=303)

        # Отримання користувача з БД
        async with get_session()() as db:
            user = await get_user_by_id(db,user_id)
            if not user:
                return RedirectResponse("/login", status_code=303)

            # Превірка підтверждення email
            if (
                not user.is_verified
                and not path.startswith("/verify-info")
                and not path.startswith("/users/resend-confirmation")
            ):
                # return RedirectResponse("/verify-info", status_code=303)
                return RedirectResponse(f"/verify-info?email={user.email}", status_code=303)

            return await call_next(request)
        # return RedirectResponse("/login", status_code=303)
