from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.db.session import DatabaseSession
from app.core.config import settings
from app.db.base_class import Base


app = FastAPI(
    title=f"{settings.PROJECT_NAME} Rest API",
    description=f"An API for {settings.PROJECT_NAME}",
    version="0.2.1",
    openapi_tags=[
        {
            "name": "Login",
            "description": "Operations related to login.",
        },
        {
            "name": "User",
            "description": "Operations related to user account.",
        },
    ],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.on_event("startup")
def startup_event() -> None:
    session = DatabaseSession()
    Base.metadata.create_all(bind=session.bind)