from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from services.deps import require_role
from database import get_db
from models import Role
import crud, schemas

router = APIRouter(prefix="/admin", tags=["admin"])

templates = Jinja2Templates(directory="templates")


@router.get("/users")
async def admin_users(
    request: Request,
    q: str | None = None,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_role(Role.admin)),
):
    users = await crud.list_users(db, q=q)
    return templates.TemplateResponse(
        "admin_users.html", {"request": request, "users": users, "query": q or ""}
    )


@router.get("/users/{user_id}/edit")
async def admin_edit_user_form(
    request: Request,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_role(Role.admin)),
):
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        return RedirectResponse("/admin/users", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        "edit_user.html", {"request": request, "user": user}
    )


@router.post("/users/{user_id}/edit")
async def admin_edit_user(
    user_id: int,
    role: str = Form(...),
    is_active: str = Form(...),
    is_verified: str = Form(...),
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_role(Role.admin)),
):
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        return RedirectResponse("/admin/users", status_code=status.HTTP_303_SEE_OTHER)
    # convert form values
    is_active_bool = True if is_active == "on" else False
    is_verified_bool = True if is_verified == "on" else False
    await crud.update_user_role_and_status(
        db, user, role=role, is_active=is_active_bool, is_verified=is_verified_bool
    )
    return RedirectResponse("/admin/users", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/users/{user_id}/delete")
async def admin_delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_role("admin")),
):
    user = await crud.get_user_by_id(db, user_id)
    if user:
        await crud.delete_user(db, user)
    return RedirectResponse("/admin/users", status_code=status.HTTP_303_SEE_OTHER)

# Для тестів 
@router.get("/users/api")
async def admin_users_api(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_role(Role.admin)),
):
    users = await crud.list_users(db)
    return {"users": users}

