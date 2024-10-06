from fastapi import FastAPI, Depends, HTTPException, Cookie, Response
from sqlalchemy.orm import Session
from .sql_db import get_db, engine
from .mongo_db import get_collection
from . import crud, schemas, auth, models
from fastapi.responses import JSONResponse
import uuid
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
FRONTEND_BASE_URL = os.getenv('FRONTEND_BASE_URL')


mail_conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=os.getenv("MAIL_PORT"),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS"),
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS"),
    USE_CREDENTIALS=os.getenv("USE_CREDENTIALS"),
    VALIDATE_CERTS=os.getenv("VALIDATE_CERTS"),
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates'
)


# TODO: Clean UP, comments
models.Base.metadata.create_all(bind=engine)
app = FastAPI()
mail = FastMail(mail_conf)

# Dependencies

# Provides an instance of UserCRUD
# This is used to perform CRUD operations on the users table in the database
# Takes in a database session and returns a UserCRUD object


def get_user_crud(db: Session = Depends(get_db)):
    return crud.UserCRUD(db)

# Provides an instance of ChatSessionCRUD
# This is used to perform CRUD operations on chat sessions (without logs)
# Takes in a database session and returns a ChatSessionCRUD object


def get_chat_crud(db: Session = Depends(get_db)):
    return crud.ChatSessionCRUD(db)

# Provides an instance of ChatSessionCRUD with log handling
# This is used to perform CRUD operations on chat sessions, including logs (chat history)
# Takes in a database session and a MongoDB collection (for storing chat logs)
# Returns a ChatSessionCRUD object configured to manage both database and log collection


def get_chat_with_log_crud(db: Session = Depends(get_db), collection=Depends(get_collection)):
    return crud.ChatSessionCRUD(db, collection=collection)

# Verifies the user's authentication status
# Extracts the JWT token using OAuth2 scheme, and uses it to retrieve the current authenticated user
# Takes in the token and a UserCRUD instance and returns the authenticated user's details


def is_user_auth(token: str = Depends(auth.oauth2_scheme), user_crud=Depends(get_user_crud)):
    return auth.Auth(user_crud).get_current_user(token)

# Utility functions
# Function to retrieve and format all chat sessions for a specific user
# Takes in the user's ID and a ChatSessionCRUD instance
# Finds all chat sessions for the user, formats them, and returns the formatted list


def get_formatted_chat_sessions(user_id, chat_crud):
    sessions = chat_crud.find_all(user_id=user_id)
    if sessions:
        for session in sessions:
          session.messages = []
        formatted_sessions = chat_crud.format(sessions)
        return dict(sorted(formatted_sessions.items(), key=lambda item: item[1]["updated_at"], reverse=True))
    return {}


def create_message(email_to: str, subject: str, body: dict):
    message = MessageSchema(
        recipients=[email_to],
        subject=subject,
        template_body=body,
        subtype=MessageType.html
    )
    return message


async def send_mail(details: schemas.SendEmailSchema, email_template: str):
    email = create_message(details.email_to,
                           details.subject,
                           details.body
                           )
    await mail.send_message(email, email_template)
    return {"details": "Email sent Successfully"}


# Registers a new user in the system
# Expects a payload matching the UserCreateSchema
# Returns the newly created user's details after successful registration
@app.post('/signup', response_model=schemas.UserRegisteredSchema,  status_code=201, tags=['Registration'])
async def signup_user(user: schemas.UserCreateSchema, user_crud=Depends(get_user_crud)):
    # return auth.Auth(user_crud).register_user(user)
    new_user, verification_token = auth.Auth(user_crud).register_user(user)
    # TODO:
    # 1. Send Verification Email with a link
    verification_link = FRONTEND_BASE_URL+f'/?token={verification_token}'
    html_body = {"link": verification_link}
#     html_body=f"""
#     <h1>Verify your email</h1>
# <p>Please click this <a href="{verification_link}">link</a> to verify your email address</p>

#     """
    details = schemas.SendEmailSchema(
        email_to=new_user.email, subject="Verify your email", body=html_body)
    await send_mail(details, "verification.html")
    return {**new_user.to_dict(), "details": "User created successfully, check email for verification link"}


@app.post('/verify', status_code=200, tags=['Resgistration'])
async def verify_email(token_data: schemas.AccountVerificationSchema, user_crud=Depends(get_user_crud)):
    if auth.Auth(user_crud).verify_email(token_data.token):
        return {'detail': "Email has been verified"}

# Reset Password


@app.post('/forgot-password', status_code=200, tags=["Registration"])
async def request_password_reset(reset_data: schemas.PasswordResetRequest, user_crud=Depends(get_user_crud)):
    reset_token = auth.Auth(user_crud).request_reset(reset_data.email)
    reset_link = FRONTEND_BASE_URL+f'/?reset={reset_token}'
    html_body = {"link": reset_link}

    details = schemas.SendEmailSchema(
        email_to=reset_data.email, subject="Password Reset", body=html_body)
    await send_mail(details, "reset.html")
    return {"email": reset_data.email, "details": "Password reset initiated check email for reset link"}


@app.post('/reset-password', status_code=200, tags=["Registration"])
async def reset_user_password(reset_data: schemas.PasswordResetConfirm, user_crud=Depends(get_user_crud)):
    if reset_data.new_password:
        if auth.Auth(user_crud).reset_password(reset_data.token, reset_data.new_password):
            return {'detail': "Password has been rest successfully"}
    raise HTTPException(400, "Please enter a password")


# Authenticates a user and provides access & refresh tokens
# Sets the refresh token as a secure, HTTP-only cookie
# Expects user login details (username, password) matching UserLogInSchema
# Returns the access token in the response body and sets refresh token in the cookie
@app.post('/login', response_model=schemas.TokenSchema, status_code=200, tags=['Registration'])
async def login_user(user: schemas.UserLogInSchema, user_crud=Depends(get_user_crud)):
    access_token, refresh_token = auth.Auth(user_crud).authenticate_user(user)
    response = JSONResponse(content=access_token.model_dump())
    response.set_cookie(key="jwt", value=refresh_token,
                        httponly=True, secure=True)
    return response


# Logs out the currently authenticated user by invalidating the refresh token
# Deletes the 'jwt' cookie from the user's browser
# Expects the current JWT to be provided in cookies
@app.get('/logout', status_code=204, tags=['Registration'])
async def logout_user(response: Response, jwt: str = Cookie(None), current_user: schemas.UserSchema = Depends(is_user_auth), user_crud=Depends(get_user_crud)):
    auth.Auth(user_crud).logout(jwt, current_user.username)
    response.delete_cookie(key="jwt")


# Generates a new access token using the refresh token
# Expects the refresh token to be provided in cookies
# Returns a new access token in the response body
@app.get("/refresh", response_model=schemas.TokenSchema, tags=['Registration'])
async def refresh_access(jwt: str = Cookie(None), user_crud=Depends(get_user_crud)):
    return auth.Auth(user_crud).refresh(jwt)


# Retrieves the currently authenticated user's profile
# Expects the JWT token for authentication
# Returns the user's profile data matching the UserProfileSchema
@app.get('/users/me', status_code=200, response_model=schemas.UserProfileSchema, tags=['User'])
async def get_user_details(current_user: schemas.UserSchema = Depends(is_user_auth)):
    return current_user

# Retrieves all chat sessions belonging to the authenticated user
# Expects the JWT token for authentication
# Returns a formatted list of the user's chat sessions


@app.get('/users/me/sessions/', status_code=200, tags=['User Session'])
async def get_user_sessions(current_user: schemas.UserSchema = Depends(is_user_auth), chat_crud=Depends(get_chat_crud)):
    return get_formatted_chat_sessions(current_user.id,  chat_crud)


# Creates a new chat session for the authenticated user
# Expects a payload matching ChatSessionCreateSchema
# Returns the newly created session's ID
@app.post('/users/me/sessions/', status_code=201, tags=['User Session'])
async def add_session(chat_session: schemas.ChatSessionCreateSchema, chat_crud=Depends(get_chat_with_log_crud), current_user: schemas.UserSchema = Depends(is_user_auth)):
    new_session = chat_crud.create_new(chat_session, current_user.id)
    return {"session_id": new_session.id}

# Retrieves detailed information about a specific chat session
# Expects a valid session_id in the URL path and the user must be authenticated
# Returns the session's details matching ChatSessionDetailsSchema


@app.get('/users/me/sessions/{session_id}', response_model=schemas.ChatSessionDetailsSchema, status_code=200, tags=['User Session'])
async def get_session(session_id: uuid.UUID, chat_crud=Depends(get_chat_with_log_crud), current_user: schemas.UserSchema = Depends(is_user_auth)):
    return chat_crud.get_session(session_id, current_user.id)


# Retrieves the log (messages) of a specific chat session for the authenticated user
# Expects a valid session_id in the URL path and the user must be authenticated
# Returns the chat log or raises a 404 error if the log could not be retrieved
@app.get('/users/me/sessions/{session_id}/log', status_code=200, response_model=schemas.ChatSessionBaseSchema, tags=['User Session'])
async def get_session(session_id: uuid.UUID, chat_crud=Depends(get_chat_with_log_crud), current_user: schemas.UserSchema = Depends(is_user_auth)):
    chat_log = chat_crud.get_logs(session_id, current_user.id)
    if chat_log:
        return chat_log
    raise HTTPException(404, "Could not fetch chat log")

# Updates an existing chat session for the authenticated user
# Expects a valid session_id in the URL path and a payload matching ChatSessionUpdateSchema
# Returns a message if the session was updated, or if no changes were made


@app.put('/users/me/sessions/{session_id}', status_code=200, tags=['User Session'])
async def update_session(session_id: uuid.UUID, chat_session: schemas.ChatSessionUpdateSchema, chat_crud=Depends(get_chat_with_log_crud), current_user: schemas.UserSchema = Depends(is_user_auth)):
    if chat_session.title or chat_session.messages:
        title_updated, log_updated = chat_crud.update_chat(
            session_id, chat_session, current_user.id)
        if title_updated or log_updated:
            return {"detail": f"Session updated successfully"}
    return {"detail": "Session is already up to date"}
