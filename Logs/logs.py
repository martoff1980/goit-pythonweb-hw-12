# print("=== ROUTES START ===")
    # for route in app.routes:
    #     print(route.path, route.methods)
    # print("=== ROUTES END ===")
    

# @router.get("/verification-logs")
# async def admin_verification_logs(
#     request: Request, db: AsyncSession = Depends(get_db), admin=Depends(require_role(Role.admin))
# ):
#     logs = await crud.get_verification_logs(db)
#     return templates.TemplateResponse(
#         "admin/verification_logs.html", {"request": request, "logs": logs}
#     )

# async def get_verification_logs(db: AsyncSession, limit: int = 100):
#     res = await db.execute(select(EmailVerificationLog).order_by(EmailVerificationLog.confirmed_at.desc()).limit(limit))
#     return res.scalars().all()
