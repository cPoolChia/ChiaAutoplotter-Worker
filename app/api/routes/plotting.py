import asyncio
import os.path
import pathlib
import time
import shutil
from uuid import UUID

from app import crud, models, schemas
from app.api import deps
from app.api.routes.base import BaseAuthCBV
from app.core import console
from app.core.console.base import BaseCommandExecutor
from fastapi import Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

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

        temp_dir_full = os.path.join(data.temp_dir, str(data.queue_id))
        final_dir_full = os.path.join(data.final_dir, str(data.queue_id))

        def on_starting() -> None:
            try:
                shutil.rmtree(temp_dir_full)
            except OSError:
                pass

            pathlib.Path(temp_dir_full).mkdir(parents=True, exist_ok=True)
            pathlib.Path(final_dir_full).mkdir(parents=True, exist_ok=True)

        try:
            execution_id = await self.executor.execute(
                "cd /root/chia-blockchain ; "
                ". ./activate ; "
                "chia "
                "plots "
                "create "
                f"-t {temp_dir_full} "
                f"-d {final_dir_full} "
                f"-n {data.plots_amount} "
                f"-p {data.pool_key} "
                f"-f {data.farmer_key} "
                f"-k {data.k} "
                f"-r {data.threads} "
                f"-b {data.ram} ",
                filter_id=data.queue_id,
                on_starting=on_starting,
            )
        except PermissionError as error:
            raise HTTPException(
                403, f"A queue with id {data.queue_id} is already plotting"
            ) from error

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
        return await send_console_json(executor.result(execution_id)[1])

    if execution_id not in executor:
        return await websocket.send_json({"error": "No such execution id"})

    await executor.listen(send_console_json, execution_id)
