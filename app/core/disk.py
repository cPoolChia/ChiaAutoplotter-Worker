import pathlib
import shutil

from app import schemas


def find_mount_point(path: pathlib.Path) -> pathlib.Path:
    while not path.is_mount():
        path = path.parent
    return path


def get_disk_data(path: pathlib.Path) -> schemas.DiskData:
    mount_point = find_mount_point(path)
    total, used, free = shutil.disk_usage(mount_point)
    return schemas.DiskData(total=total, free=free, used=used)