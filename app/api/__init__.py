from fastapi import APIRouter

from app.api.routes import user, login, plotting, metadata, directories

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["Login"])
api_router.include_router(user.router, prefix="/user", tags=["User"])
api_router.include_router(plotting.router, prefix="/plotting", tags=["Plotting"])
api_router.include_router(metadata.router, prefix="/metadata", tags=["Metadata"])
api_router.include_router(
    directories.router, prefix="/directories", tags=["Directories"]
)
# api_router.include_router(
#     transferring.router, prefix="/transferring", tags=["Transferring"]
# )
