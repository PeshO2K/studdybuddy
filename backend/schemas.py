from pydantic import BaseModel,EmailStr
from uuid import UUID
from typing import Optional


# Create Chat Session Schemas
class ChatSessionBaseSchema(BaseModel):
    title: str


class ChatSessionCreateSchema(ChatSessionBaseSchema):
    messages: list
    


class ChatSessionUpdateSchema(BaseModel):
    messages: list

class ChatSessionSchema(ChatSessionBaseSchema):
    id: UUID
    user_id: UUID

    class Config:
        orm_mode = True
        

# Create User Schemas
class UserBaseSchema(BaseModel):
    username: str
    
    # refresh_token: str

class UserLogInSchema(UserBaseSchema):
    password: str


class UserCreateSchema(UserLogInSchema):
    email: EmailStr
    
class UserSchema(UserBaseSchema):
    id: UUID
    email: EmailStr
    refresh_token: Optional[str]
    chat_sessions: list[ChatSessionSchema]=[]
    hashed_password:str # to remove
    class Config:
        orm_mode = True


#   Token
class TokenSchema(BaseModel):
    access_token: str
    token_type:str

#  Token Data
class TokenDataSchema(BaseModel):
    username: str
