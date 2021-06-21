import pathlib
import shutil

from typing import Optional
import uuid
import collections
from app import schemas
from app.core import disk
from app.api.routes.base import BaseAuthCBV
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

router = InferringRouter()


@cbv(router)
class DirectoriesCBV(BaseAuthCBV):
    @router.post("/")
    async def scan_directories(
        self, directories: set[pathlib.Path]
    ) -> dict[pathlib.Path, Optional[schemas.DirInfo]]:
        result: dict[pathlib.Path, Optional[schemas.DirInfo]] = collections.defaultdict(
            schemas.DirInfo
        )

        for directory in directories:
            if not directory.exists() or not directory.is_dir():
                result[directory] = None
                continue

            plots: set[schemas.PlotData] = set()
            for file in directory.iterdir():
                if file.is_file() and ".plot" in file.name:
                    plotting = file.name.endswith(".plot")
                    name = ".".join(file.name.split(".")[:2])
                    plots.add(
                        schemas.PlotData(name=name, plotting=plotting, queue=None)
                    )
                elif file.is_dir():
                    try:
                        queue_id = uuid.UUID(hex=file.name)
                    except ValueError:
                        pass
                    else:
                        for sub_file in file.iterdir():
                            plotting = sub_file.name.endswith(".plot")
                            plots.add(
                                schemas.PlotData(
                                    name=sub_file.name,
                                    plotting=plotting,
                                    queue=queue_id,
                                )
                            )

            result[directory] = schemas.DirInfo(
                plots=plots, disk_size=disk.get_disk_data(directory)
            )

            print(result)

        return result
