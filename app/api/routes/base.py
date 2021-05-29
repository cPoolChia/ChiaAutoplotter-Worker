from app import models
from app.api import deps
from fastapi import Depends
from sqlalchemy.orm import Session


class BaseCBV:
    db: Session = Depends(deps.get_db)


class BaseAuthCBV(BaseCBV):
    user: models.User = Depends(deps.get_current_user)
