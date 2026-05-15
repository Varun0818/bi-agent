import json
import logging

from db import crud
from db.database import SessionLocal

logger = logging.getLogger(__name__)


def save_trace(query_id: str, trace_steps: list[dict]) -> None:
    try:
        db = SessionLocal()
        try:
            for i, step in enumerate(trace_steps):
                crud.save_trace_step(
                    db,
                    query_id=query_id,
                    node_name=step["node"],
                    input_data=json.dumps(step.get("input", {})),
                    output_data=json.dumps(step.get("output", {})),
                    latency_ms=step.get("latency_ms", 0),
                    step_order=i,
                )
        finally:
            db.close()
    except Exception as e:
        logger.exception("save_trace failed for query_id=%s: %s", query_id, e)


def get_trace(query_id: str) -> list[dict]:
    db = SessionLocal()
    try:
        logs = crud.get_trace(db, query_id)
        return [
            {
                "node": t.node_name,
                "input": json.loads(t.input_data),
                "output": json.loads(t.output_data),
                "latency_ms": t.latency_ms,
                "step_order": t.step_order,
            }
            for t in logs
        ]
    finally:
        db.close()
