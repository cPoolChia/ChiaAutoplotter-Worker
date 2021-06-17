import asyncio
import os.path
import pathlib
import time
from uuid import UUID
import uuid

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
class TransferringCBV(BaseAuthCBV):
    executor: BaseCommandExecutor = Depends(deps.get_command_executor)

    @router.get("/{execution_id}/")
    async def get_transferring(self, execution_id: UUID) -> schemas.TransferringReturn:
        if execution_id not in self.executor:
            raise HTTPException(404, detail="No transferring with such id found")

        result = self.executor.result(execution_id)
        if result is None:
            return schemas.TransferringReturn(id=execution_id)
        return schemas.TransferringReturn(
            id=execution_id, finished=True, status_code=result[0]
        )

    @router.post("/")
    async def start_transferring(
        self, data: schemas.TransferringData
    ) -> schemas.TransferringReturn:
        """ Start a new plotting task. """

        file_path = os.path.join(data.filedir, data.filename)
        uuid.uuid3(uui)

        try:
            execution_id = await self.executor.execute(
                "rsync -aHAXxv --numeric-ids --delete "
                '--progress -e "ssh -T -c aes128-gcm@openssh.com -o Compression=no -x" '
                f"{file_path} "  # rsync what
                f"{data.destination_user}@{data.destination_host}:"
                f"{data.destination_port}/{data.destination_folder} ;"  # rsync where
                f"rm {file_path}",
                filter_id=data.queue_id,
                stdin=f"{password}\n".encode("utf8"),
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
        return await send_console_json(executor.result(execution_id))

    if execution_id not in executor:
        return await websocket.send_json({"error": "No such execution id"})

    await executor.listen(send_console_json, execution_id)
