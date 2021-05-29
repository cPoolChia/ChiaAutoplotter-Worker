from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi_utils.api_model import APIModel

from pydantic import Field


class PlottingData(APIModel):
    final_dir: str
    temp_dir: str
    pool_key: str
    farmer_key: str
    plots_amount: int
    k: int
    threads: int
    ram: int


class PlottingReturn(APIModel):
    id: UUID
