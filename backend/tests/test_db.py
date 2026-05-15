# run as: python tests/test_db.py (create this manually)
import sys; sys.path.insert(0,".")
from db.database import app_engine
from db.models import Base
from db import crud
from sqlalchemy.orm import Session
Base.metadata.create_all(bind=app_engine)
db = Session(bind=app_engine)
crud.create_chat_session(db, "t1", "Test")
assert crud.get_chat_session(db, "t1").session_name == "Test"
print("✅ DB layer OK")
db.close()