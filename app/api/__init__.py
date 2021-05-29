from fastapi import APIRouter

from app.api.routes import user, login, plotting

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["Login"])
api_router.include_router(user.router, prefix="/user", tags=["User"])
api_router.include_router(plotting.router, prefix="/plotting", tags=["Plotting"])