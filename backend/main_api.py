from fastapi import FastAPI, Depends, HTTPException , Cookie, Response
from fastapi.security import OAuth2PasswordRequestForm
# import uvicorn
# from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from .sql_db import get_db, engine
from .mongodb import get_chat_logs_collection
from . import crud, schemas, auth ,models
from fastapi.responses import JSONResponse
import uuid

# TODO: Clean UP, comments
models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# Response.set_cookie()
# Sign up a new user
@app.post('/signup',  status_code=201, tags=['Registration'])
async def signup_user(user:schemas.UserCreateSchema, db:Session=Depends(get_db)):
    db_user_email = crud.get_user_by_email(db, email=user.email)
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user_username = crud.get_user_by_username(db, username=user.username)
    if db_user_username:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    return crud.create_user(db=db, user=user)


# Log in user
#  Sending a cookie at initial log in and subsequent login when the token expires
@app.post('/login', response_model=schemas.TokenSchema, status_code=200, tags=['Registration'])
# async def login_user(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
async def login_user(user: schemas.UserLogInSchema, db: Session = Depends(get_db)):
    db_user = auth.authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token, refresh_token = auth.generate_tokens(
        data={'sub': user.username},db=db)
     
    # --- minor fix to handle error:
    token = access_token.access_token
    token_type = access_token.token_type
    access_token = {'access_token':token,'token_type':token_type}

    # access_token = {"message": "Come to the dark side, we have cookies"}
    # ------ToDo: Also send back an HTTPOnly cookie with refresh token, inside the response....
    response = JSONResponse(content=access_token)
    response.set_cookie(key="jwt", value=refresh_token)
    return response
    #return access_token

# Log out user
#  Delete cookie
@app.get('/logout', status_code=200, tags=['Registration'])
async def logout_user( response:Response, jwt: str=Cookie(None),db:Session = Depends(get_db)):
    auth.handle_logout(jwt,db)    
    response.delete_cookie(key="jwt")
    return {'Success': jwt}
    #return access_token


# get new access token
# @app.get("/refresh", response_model=schemas.TokenDataSchema, tags=['Registration'])
@app.get("/refresh", tags=['Registration'])
# has to be the same name as the key parameter
async def refresh_access(jwt: str = Cookie(None), db: Session = Depends(get_db)):
        if jwt:
            return auth.handle_refresh(jwt,db)
        raise HTTPException(401, "Unauthorised")

#Get all sessions
@app.get('/sessions', status_code=200,tags=['Chat'])
async def get_sessions(db: Session = Depends(get_db)):
    return crud.get_chat_sessions(db=db)


#Get User Profile
@app.get('/users/me', status_code=200, tags=['User'])
async def get_user_details(current_user: schemas.UserSchema = Depends(auth.get_current_active_user)):
    return current_user

#Get a User's Sessions
@app.get('/users/me/sessions/', status_code=200,tags=['User Session'])
async def get_user_sessions(current_user: schemas.UserSchema = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    return crud.get_chat_sessions(db=db,user_id=current_user.id)


# Add a new chat session
@app.post('/users/me/sessions/', status_code=201, tags=['User Session'])
async def add_session(chat_session: schemas.ChatSessionCreateSchema, db: Session = Depends(get_db), chat_log: list = Depends(get_chat_logs_collection), current_user: schemas.UserSchema = Depends(auth.get_current_active_user)):
    new_session = crud.create_chat_session(db, chat_log, chat_session, current_user.id)
    # return the session id {'session': new_session, 'db':db}
    # return {'session': new_session, 'msg':chat_session}
    return {"session_id":new_session.id}


#Get chat session info
@app.get('/users/me/sessions/{session_id}', status_code=200, tags=['User Session'])
async def get_session(session_id: uuid.UUID, db: Session = Depends(get_db), chat_log: list = Depends(get_chat_logs_collection), current_user: schemas.UserSchema = Depends(auth.get_current_active_user)):
    return crud.get_session(db,chat_log, session_id)
# Get chat session log
@app.get('/users/me/sessions/{session_id}/log', status_code=200, tags=['User Session'])
async def get_session(session_id: uuid.UUID, chat_log: list = Depends(get_chat_logs_collection), current_user: schemas.UserSchema = Depends(auth.get_current_active_user)):
    session_log =  crud.get_session_log(chat_log, session_id)
    if session_log:
        return session_log
    raise HTTPException(404, "Could not fetch chat log")

# Add messages to chat session log


@app.put('/users/me/sessions/{session_id}', status_code=200, tags=['User Session'])
async def update_session(session_id: uuid.UUID, chat_session: schemas.ChatSessionUpdateSchema, chat_log: list = Depends(get_chat_logs_collection),  current_user: schemas.UserSchema = Depends(auth.get_current_active_user)):
    session_updated = crud.update_session_log(chat_log, session_id, chat_session.messages)
    if session_updated:
        return {"detail": "Updated successfully!"}
    raise HTTPException(404, detail="Could not update session")
