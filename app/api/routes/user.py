from app import crud, models, schemas
from app.api import deps
from app.api.routes.base import BaseCBV
from fastapi import Depends, HTTPException
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

router = InferringRouter()


@cbv(router)
class UserCBV(BaseCBV):
    @router.get("/")
    async def get_user_data(
        self, user: models.User = Depends(deps.get_current_user)
    ) -> schemas.UserReturn:
        """ Get your user data. """

        return user.__dict__

    @router.post("/")
    async def reg_new_user(self, data: schemas.UserCreate) -> schemas.UserReturn:
        """ Register a user to be able to connect. """

        if crud.user.get_multi(self.db)[0] > 0:
            raise HTTPException(403, detail="Only first user can be registered")

        user = crud.user.create(self.db, obj_in=data)
        return schemas.UserReturn.from_orm(user)
