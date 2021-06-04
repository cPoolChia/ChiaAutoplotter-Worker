from datetime import datetime
from uuid import UUID
from fastapi_utils.api_model import APIModel


class MetadataReturn(APIModel):
    version: str