from fastapi_utils.inferring_router import InferringRouter
from app import schemas
import toml

router = InferringRouter()


@router.get("/")
def get_metadata() -> schemas.MetadataReturn:
    poetry_project_config = toml.load("pyproject.toml")
    raise Exception(poetry_project_config)
    return schemas.MetadataReturn(
        version=poetry_project_config["tool.poetry"]["version"]
    )
