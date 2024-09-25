from sqlalchemy import Column, String, ForeignKey, UUID
from sqlalchemy.orm import relationship
from .sql_db import Base
import uuid

# TODO: Alternative approach, Classes with custom functions
# Model to store user information
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    # id = Column(UUID, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    # Add field to store refresh token
    refresh_token = Column(String, nullable=True)

    chat_sessions = relationship("ChatSession", back_populates="user")

# Model to store chat session metadata
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True,
          default=uuid.uuid4, index=True)
    title = Column(String)
    user_id = Column(UUID, ForeignKey("users.id"))

    user = relationship("User", back_populates="chat_sessions")
