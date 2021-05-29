from typing import Iterator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import DatabaseSession

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"/login/access-token")


def get_db() -> Iterator[Session]:
    db = DatabaseSession()
    try:
        yield db
    finally:
        db.close()


def get_token_data(token: str = Depends(reusable_oauth2)) -> schemas.AuthTokenPayload:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.AuthTokenPayload(**payload)
    except (jwt.JWTError, ValidationError) as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from error
    return token_data


def get_current_user_raw(
    db: Session = Depends(get_db),
    token_data: schemas.AuthTokenPayload = Depends(get_token_data),
) -> models.User:
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_user(
    token_data: schemas.AuthTokenPayload = Depends(get_token_data),
    user: models.User = Depends(get_current_user_raw),
) -> models.User:
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_REFRESH_EXPIRE_MINUTES
    )
    token_login_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_login_expires_date = (
        token_data.exp - access_token_expires + token_login_expires
    )
    if datetime.now(token_login_expires_date.tzinfo) > token_login_expires_date:
        raise HTTPException(403, detail="Login time for token has been expired")
    return user