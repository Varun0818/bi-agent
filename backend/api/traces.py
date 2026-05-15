from typing import Any

from fastapi import APIRouter

from services.trace_service import get_trace

router = APIRouter(prefix="/traces")


@router.get("/{query_id}")
def get_query_trace(query_id: str) -> list[dict[str, Any]]:
    return get_trace(query_id)
