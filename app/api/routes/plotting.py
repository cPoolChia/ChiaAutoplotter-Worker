from app.core.console.base import BaseCommandExecutor
from app import crud, models, schemas
from app.core import console
from app.api import deps
from app.api.routes.base import BaseAuthCBV
from fastapi import Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
import asyncio

from uuid import UUID
import time
from fastapi.encoders import jsonable_encoder
import asyncio

router = InferringRouter()


@cbv(router)
class PlottingCBV(BaseAuthCBV):
    executor: BaseCommandExecutor = Depends(deps.get_command_executor)

    @router.get("/{execution_id}/")
    async def get_plotting(self, execution_id: UUID) -> schemas.PlottingReturn:
        if execution_id not in self.executor:
            raise HTTPException(404, detail="No plotting with such id found")

        result = self.executor.result(execution_id)
        if result is None:
            return schemas.PlottingReturn(id=execution_id)
        return schemas.PlottingReturn(
            id=execution_id, finished=True, status_code=result[0]
        )

    @router.post("/")
    async def start_plotting(
        self, data: schemas.PlottingData
    ) -> schemas.PlottingReturn:
        """ Start a new plotting task. """

        execution_id = await self.executor.execute(
            "cd /root/chia-blockchain ; "
            ". ./activate ; "
            "chia "
            "plots "
            "create "
            f"-t {data.temp_dir} "
            f"-d {data.final_dir} "
            f"-n {data.plots_amount} "
            f"-p {data.pool_key} "
            f"-f {data.farmer_key} "
            f"-k {data.k} "
            f"-r {data.threads} "
            f"-b {data.ram} "
        )

        return schemas.PlottingReturn(id=execution_id)


@router.websocket("/ws/")
async def websocket_endpoint(
    websocket: WebSocket,
    execution_id: UUID,
    # user: models.User = Depends(deps.get_current_user),
    executor: BaseCommandExecutor = Depends(deps.get_command_executor),
) -> None:
    await websocket.accept()

    send_console_json = lambda output: websocket.send_json({"output": output})
    if executor.finished(execution_id):
        return await send_console_json(executor.result(execution_id))

    if execution_id not in executor:
        return await websocket.send_json({"error": "No such execution id"})

    await executor.listen(send_console_json, execution_id)