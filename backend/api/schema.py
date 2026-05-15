from typing import Any

from fastapi import APIRouter

from services.schema_service import schema_service

router = APIRouter(prefix="/schema")


@router.get("/")
def get_schema() -> dict[str, Any]:
    return {"tables": schema_service.get_schema_dict()}
