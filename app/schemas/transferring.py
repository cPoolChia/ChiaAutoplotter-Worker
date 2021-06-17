from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi_utils.api_model import APIModel

from pydantic import Field


class TransferringData(APIModel):
    filedir: str
    filename: str
    destination_folder: str
    destination_host: int
    destination_port: str
    destination_user: str
    destination_password: str


class TransferringReturn(APIModel):
    id: UUID
    status_code: Optional[int] = None
    finished: bool = False
