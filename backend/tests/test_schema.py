# python tests/test_schema.py
import sys; sys.path.insert(0,".")
from services.schema_service import schema_service
schema_service.embed_schema()
r = schema_service.search_schema("monthly sales by region")
assert "orders" in r.lower(), f"Got: {r[:100]}"
print("✅ Schema service OK")