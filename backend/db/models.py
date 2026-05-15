from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from db.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    session_id = Column(String, primary_key=True, index=True)
    session_name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, nullable=True)
    message_count = Column(Integer, default=0)

    conversations = relationship("ConversationHistory", back_populates="session")
    queries = relationship("QueryHistory", back_populates="session")


class ConversationHistory(Base):
    __tablename__ = "conversation_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String, ForeignKey("chat_sessions.session_id"))
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="conversations")


class QueryHistory(Base):
    __tablename__ = "query_history"

    query_id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.session_id"))
    user_query = Column(Text)
    generated_sql = Column(Text, nullable=True)
    success = Column(Boolean, nullable=True)
    retry_count = Column(Integer, default=0)
    row_count = Column(Integer, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="queries")
    traces = relationship("TraceLog", back_populates="query")


class TraceLog(Base):
    __tablename__ = "trace_logs"

    trace_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    query_id = Column(String, ForeignKey("query_history.query_id"))
    node_name = Column(String)
    input_data = Column(Text)
    output_data = Column(Text)
    latency_ms = Column(Integer)
    token_count = Column(Integer, nullable=True)
    step_order = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    query = relationship("QueryHistory", back_populates="traces")


class Feedback(Base):
    __tablename__ = "feedback"

    feedback_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    query_id = Column(String)
    rating = Column(Integer)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class EvalResult(Base):
    __tablename__ = "eval_results"

    eval_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    run_name = Column(String)
    query_ref = Column(String)
    test_query = Column(Text)
    generated_sql = Column(Text, nullable=True)
    expected_pattern = Column(Text)
    passed = Column(Boolean)
    latency_ms = Column(Integer)
    retry_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class AssistantResult(Base):
    __tablename__ = "assistant_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, index=True, nullable=False)
    query_id = Column(String, nullable=False)
    result_json = Column(Text, nullable=False)
    turn_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
