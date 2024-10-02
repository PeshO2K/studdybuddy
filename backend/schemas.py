from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, Any


# Create Chat Session Schemas
class ChatSessionBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    messages: list
    


class ChatSessionCreateSchema(ChatSessionBaseSchema):
    title: str
    

class ChatSessionUpdateSchema(ChatSessionCreateSchema):
    pass

class ChatSessionDetailsSchema(ChatSessionCreateSchema):
    updated_at: datetime


class ChatSessionSchema(ChatSessionCreateSchema):
    id: UUID
    user_id: UUID



        


# Create User Schemas
class UserBaseSchema(BaseModel):
    username: str
    
    # refresh_token: str

class UserLogInSchema(UserBaseSchema):
    password: str

class UserProfileSchema(UserBaseSchema):
    email: EmailStr
class UserRegisteredSchema(UserProfileSchema):
    details: str

class UserCreateSchema(UserLogInSchema):
    email: EmailStr
    
class UserSchema(UserBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: EmailStr
    refresh_token: Optional[str]
    chat_sessions: list[ChatSessionSchema]=[]
    hashed_password:str # to remove
    


#   Token
class TokenSchema(BaseModel):
    access_token: str
    token_type:str
class SendEmailSchema(BaseModel):
    email_to: EmailStr
    subject: str
    body: Any

# Passswords

class PasswordResetRequest(BaseModel):
    email: EmailStr


class AccountVerificationSchema(BaseModel):
    token: str


class PasswordResetConfirm(AccountVerificationSchema):
    new_password: str
