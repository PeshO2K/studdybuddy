from sqlalchemy import Column, String, ForeignKey, UUID, DateTime, Boolean
from sqlalchemy.orm import relationship
from .sql_db import Base
import uuid
from datetime import datetime, timezone 


class ParentModel:
    id = Column(UUID(as_uuid=True), primary_key=True,
                 default=uuid.uuid4, index=True)
    created_at = Column(DateTime, nullable=False,default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(
        timezone.utc), onupdate=datetime.now(timezone.utc))

    def __init__(self,*args,**kwargs):
        self.id= uuid.uuid4()
        self.created_at = datetime.now(timezone.utc)
        self.updated_at=self.created_at
        if kwargs:
            for key, value in kwargs.items():
                if key in ["created_at", "updated_at"]:
                    setattr(self, key, datetime.fromisoformat(value))
                elif key != "__class__":
                    setattr(self, key, value)
    def __str__(self):
        """Returns a string representation of the instance"""
        cls = (str(type(self)).split('.')[-1]).split('\'')[0]
        my_dict = {}
        my_dict.update(self.to_dict())
        del my_dict["__class__"]
        return '[{}] ({}) {}'.format(cls, self.id, my_dict)


    def to_dict(self):
        """Convert instance into dict format"""
        dictionary = {}
        dictionary.update(self.__dict__)
        dictionary.update({'__class__':
                          (str(type(self)).split('.')[-1]).split('\'')[0]})
        dictionary['created_at'] = self.created_at.isoformat()
        dictionary['updated_at'] = self.updated_at.isoformat()
        if '_sa_instance_state' in dictionary.keys():
            del dictionary['_sa_instance_state']
        return dictionary



class User(ParentModel,Base):
    __tablename__ = "users"
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    refresh_token = Column(String, nullable=True)
    is_verified = Column(Boolean, nullable=False, default=False)

    chat_sessions = relationship("ChatSession", back_populates="user")

# Model to store chat session metadata
class ChatSession(ParentModel,Base):
    __tablename__ = "chat_sessions"
    title = Column(String)
    user_id = Column(UUID, ForeignKey("users.id"))

    user = relationship("User", back_populates="chat_sessions")
