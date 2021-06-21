import uuid
from pydantic import BaseModel
from typing import Optional


class PlotData(BaseModel):
    name: str
    plotting: bool
    queue: Optional[uuid.UUID]

    def __hash__(self) -> int:
        return hash((type(self), self.name, self.plotting, self.queue))


class DiskData(BaseModel):
    total: int
    free: int
    used: int


class DirInfo(BaseModel):
    plots: list[PlotData] = []
    disk_size: Optional[DiskData] = None
