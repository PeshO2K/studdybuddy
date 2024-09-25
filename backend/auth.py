from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
# from fastapi_jwt_auth import AuthJWT
from jose import jwt,JWTError
from passlib.context import CryptContext
# from .models import User
from .schemas import *
from sqlalchemy.orm import Session
from .sql_db import get_db
from . import crud, schemas
from datetime import datetime, timedelta, timezone

#TODO: refactor, cleanup,comment, remove test data

ALGORITHM = 'HS256'
ACCESS_TOKEN_EXP = timedelta(seconds=20)
ACCESS_TOKEN_KEY = 'veryfakeaccesstokenprivatekey'
REFRESH_TOKEN_EXP = timedelta(minutes=40)
REFRESH_TOKEN_KEY = 'veryfakerefreshtokenprivatekey'


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(db = Depends(get_db),token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Not Authorised",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # TODO: Remove
    # forbidden_except = HTTPException(403, "Forbidden!")
    # credentials_exception1 = HTTPException(
    #     status_code=401,
    #     detail="Decode Error",
    #     headers={"WWW-Authenticate": "Bearer"},
    # )
    # credentials_exception2 = HTTPException(
    #     status_code=401,
    #     detail="User not found in payload",
    #     headers={"WWW-Authenticate": "Bearer"},
    # )
    # credentials_exception3 = HTTPException(
    #     status_code=401,
    #     detail="User not found in db",
    #     headers={"WWW-Authenticate": "Bearer"},
    # )

    try:
        payload = jwt.decode(token, ACCESS_TOKEN_KEY, algorithms=[ALGORITHM])
        # return payload
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenDataSchema(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.UserSchema = Depends(get_current_user)):
    return current_user



def verify_password(plain_password, hashed_password):
    # return get_password_hash(plain_password) == hashed_password
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    # return (f"hashed_password_{password}")
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    user = crud.get_user_by_username(db, username)
    
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False


    return user

def handle_refresh(refresh_token,db):
    forbidden_except = HTTPException(403,"Forbidden!")
    unauthorised_except = HTTPException(401,"Unauthorised!")
    
    try:
        payload = jwt.decode(refresh_token, REFRESH_TOKEN_KEY,
                             algorithms=[ALGORITHM])
        username = payload.get('sub')
        if username is None:
            raise forbidden_except
        db_user = crud.get_user_by_token(db,refresh_token)
        if db_user is None:
            raise forbidden_except
        if username == db_user.username:
            # token_data = schemas.TokenDataSchema(username=username)
            token_data = {"sub":username}
            access_token = create_access_token(token_data)
            return access_token
        else:
            # delete found user's refresh token
            crud.update_refresh_token(db, db_user.username)
            raise forbidden_except
    except:
        raise unauthorised_except

def handle_logout(refresh_token,db):
    
    # try:
        db_user = crud.get_user_by_token(db, refresh_token)
        if db_user is None:
            return {"404": "db User not found"}  # clear cookie
        crud.update_refresh_token(db, db_user.username)  # clear cookie
    # except:
    #     raise HTTPException(401, "Forbidden!!!")
    


    


# Create tokens general function
def create_token(data: dict, expires_delta: timedelta,secret_key):
    to_encode = data.copy()
    
    expire =  datetime.now(timezone.utc)+ expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt

# Create access token


def create_access_token(data: dict):
    token = schemas.TokenSchema(access_token=create_token(
        data, ACCESS_TOKEN_EXP, ACCESS_TOKEN_KEY), token_type='bearer')
    
    return token

# Create refresh  token


def create_refresh_token(data: dict):
    token = create_token(data, REFRESH_TOKEN_EXP, REFRESH_TOKEN_KEY)
    return token


def generate_tokens(data: dict, db:Session):
    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)
    if crud.update_refresh_token(db,data['sub'],refresh_token):
       return access_token, refresh_token
    return None
