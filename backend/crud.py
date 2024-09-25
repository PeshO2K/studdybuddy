from sqlalchemy.orm import Session
from utility.fileutility import  update_json_data
from . import schemas, auth , models
import uuid
from .schemas import UserSchema
from typing import Optional
from .mongodb import save_chat_log,update_chat_log,get_chat_logs
DB_BASE_PATH = 'utility/'

# TODO: Cleanup, refactor, comment



# # ------------ USER CRUD FUNCTIONS ---------------- #
# Create a new user
def create_user(db: Session, user: schemas.UserCreateSchema):   
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username,
                          email=user.email,
                            hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Get a user by id
def get_user(db: Session, user_id: uuid):
    return db.query(models.User).filter(models.User.id == user_id).first()

#Get a user by username
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

#Get a user by email
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# Get a user by refresh token
def get_user_by_token(db: Session, token: str):
    return db.query(models.User).filter(models.User.refresh_token == token).first()

# Get all users, or range of users: ----ToDo: Remove if unnecessary
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()



# # ## ------- CHAT SESSIONS -------------- ###

# Add new session
def create_chat_session_meta(db: Session, chat_session: schemas.ChatSessionCreateSchema, user_id: str):    
    db_chat_session = models.ChatSession(title=chat_session.title,
                                         user_id=user_id )
    db.add(db_chat_session)
    db.commit()
    db.refresh(db_chat_session)
    return db_chat_session

# ToDo:  Add function to creat mongo db chat log using the chat id
def create_chat_session_log(chat_log, chat_session: dict, session_id: str):
    return save_chat_log(session_id,chat_session.messages,chat_log)

# ToDo:  Add function to combine creating log abd meta
def create_chat_session(db: Session, chat_log, chat_session: dict, user_id: str):
    # first create metadata and get uuid
    db_session = create_chat_session_meta(db,chat_session,user_id)
    if db_session:
        session_log = create_chat_session_log(chat_log, chat_session,db_session.id)
        if session_log:
            return db_session
        # delete db_session otherwise
        
        db.delete(db_session)
        db.commit()
    return None

def session_formatter(sessions:list):
    formatted_sessions={}
    for session in sessions:
        
        formatted_sessions[session.id] = {"title": session.title, "messages": []}
    return formatted_sessions

# Get all chat_sessions, or range of chat_sessions: ----ToDo: Remove if unnecessary
# Add optional user_id parameter, returns list of session ids
def get_chat_sessions(db: Session, skip: int = 0, limit: int = 100, user_id: Optional[str]=None):
    if user_id:
        user_sessions = db.query(models.ChatSession).filter(models.ChatSession.user_id==user_id).offset(skip).limit(limit).all()
        return session_formatter(user_sessions)
    return db.query(models.ChatSession).offset(skip).limit(limit).all()


def get_session_metadata(db: Session, chat_session_id: uuid.UUID):
    if isinstance(chat_session_id, str):
        chat_session_id = uuid.UUID(chat_session_id)
    return db.query(models.ChatSession).filter(models.ChatSession.id == chat_session_id).first()

# TODO: mongo db version:
def get_session_log(chat_log, chat_session_id: uuid.UUID):
    session_log = get_chat_logs(chat_session_id,chat_log)
    return session_log

# TODO: combine both to return a completed session
def get_session(db, chat_log, chat_session_id: uuid.UUID):
    session_meta= get_session_metadata(db,chat_session_id)
    if session_meta:
        session_log = get_session_log(chat_log, chat_session_id)
        if session_log:
            chat_session = {"meta":session_meta,** session_log}
            return chat_session
    return None

# TODO: update mongo chat log:
def update_session_log(chat_log, chat_session_id: str, new_messages: list):
    session_log = update_chat_log(chat_session_id,new_messages,chat_log)
    return session_log

# # ## ------- AUTHENTICATION -------------- ###

def update_refresh_token(db: Session, username: str, refresh_token: Optional[str]=None):
    db_user = get_user_by_username(db, username)
    db_user.refresh_token = refresh_token
    db.commit()
    db.refresh(db_user)
    return db_user
