from fastapi import  HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt,JWTError
from passlib.context import CryptContext
from .schemas import *
from itsdangerous import URLSafeTimedSerializer
from . import crud, schemas
from datetime import datetime, timedelta, timezone
import logging
import os
from dotenv import load_dotenv
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
#TODO: refactor, cleanup,comment, remove test data

ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXP = timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXP')))
ACCESS_TOKEN_KEY = 'veryfakeaccesstokenprivatekey'
REFRESH_TOKEN_EXP = timedelta(minutes=int(os.getenv('REFRESH_TOKEN_EXP')))
REFRESH_TOKEN_KEY = os.getenv('REFRESH_TOKEN_KEY')
VERIFICATION_TOKEN_KEY = os.getenv('VERIFICATION_TOKEN_KEY')
RESET_TOKEN_KEY = os.getenv('RESET_TOKEN_KEY')


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class PasswordHandler:
    """
    Handles password hashing and verification using bcrypt.
    """
    __pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    def hash_password(self,password):
        """
        Hashes the given password.

        :param password: The plain text password to be hashed.
        :return: The hashed password.
        """
        # return (f"hashed_password_{password}")
        return self.__pwd_context.hash(password)
    
    def verify_password(self,plain_password, hashed_password):
        """
        Verifies a plain text password against a hashed password.

        :param plain_password: The plain text password.
        :param hashed_password: The hashed password to compare against.
        :return: True if the passwords match, False otherwise.
        """
        return self.__pwd_context.verify(plain_password, hashed_password)
 
 

class TokenHandler:
    """
    Manages JWT token creation and verification.
    """
    
    def _getserializer(self, secret_key, salt:str):
        return URLSafeTimedSerializer(secret_key=secret_key, salt=salt)

    def generate_url_safe_token(self, data: dict, serializer):
        
        return serializer.dumps(data)
    def decode_url_safe_token(self, token: str, serializer):
        try:
            payload = serializer.loads(token)
            email : EmailStr = payload.get('sub')
            if not email:
                raise HTTPException(401, "[decode url token] Unauthorised")
            return email
        except Exception as e:
            logger.error(f"Error decoding url token: {e}")

    


    # Create tokens general function
    def _create_token(self, data: dict, expires_delta: timedelta, secret_key):
        """
        Creates a JWT token with the specified expiration.

        :param data: The payload data to include in the token.
        :param expires_delta: The time delta for the token's expiration.
        :param secret_key: The secret key used to sign the token.
        :return: The encoded JWT token.
        """
        to_encode = data.copy()

        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
        return encoded_jwt

    

    # Create access token
    def generate_access_token(self, data: dict):
        """
        Generates an access token.

        :param data: The payload data for the token.
        :return: A TokenSchema containing the access token.
        """
        token = schemas.TokenSchema(access_token=self._create_token(
            data, ACCESS_TOKEN_EXP, ACCESS_TOKEN_KEY), token_type='bearer')
        return token

    # Create refresh  token
    def generate_refresh_token(self, data: dict):
        """
        Generates a refresh token.

        :param data: The payload data for the token.
        :return: The refresh token as a string.
        """
        token = self._create_token(data, REFRESH_TOKEN_EXP, REFRESH_TOKEN_KEY)

        return token
    def _decode_token(self, token, TOKEN_KEY):
        """
        Decodes a JWT token and extracts the username.

        :param token: The JWT token to decode.
        :param TOKEN_KEY: The secret key used for decoding.
        :return: The username extracted from the token.
        :raises HTTPException: If the token is invalid or expired.
        """
        credentials_exception = HTTPException(
            status_code=401,
            detail="Not Authorised",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, TOKEN_KEY,
                                 algorithms=[ALGORITHM])
            # return payload
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            return username
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def verify_token(self, token, token_type:str):
        """
        Verifies the validity of a token (either access or refresh).

        :param token: The JWT token to verify.
        :param token_type: The type of the token ('access' or 'refresh').
        :return: The corresponding database user and username.
        :raises ValueError: If token_type is invalid.
        :raises HTTPException: If the token is invalid or user not found.
        """
        credentials_exception = HTTPException(
            status_code=401,
            detail="Not Authorised",
            headers={"WWW-Authenticate": "Bearer"},
        )
        # Define mappings for token types and filter criteria
        token_mapping = {
            'access': (ACCESS_TOKEN_KEY, 'username'),
            'refresh': (REFRESH_TOKEN_KEY, 'refresh_token')
        }

        # Validate token_type
        if token_type not in token_mapping:
            raise ValueError("token_type must either be 'access' or 'refresh'")

        # Retrieve the correct TOKEN_KEY and filter field based on token_type
        TOKEN_KEY, filter_field = token_mapping[token_type]
        try:
            username= self._decode_token(token, TOKEN_KEY)
            # Create filter criteria dynamically
            find_criteria = {filter_field: token if token_type ==
                         'refresh' else username}
            db_user = self.user_crud.find_by(**find_criteria)
            if db_user is None:
                raise credentials_exception
            return db_user , username               
        except:
            raise credentials_exception
        

class Auth(PasswordHandler, TokenHandler):
    """
    Authentication class that combines password handling and token management.
    """
    def __init__(self, user_crud):
        """
        Initializes the Auth class with the user CRUD operations.

        :param user_crud: The CRUD operations for user management.
        """
        
        self.user_crud = user_crud

    def get_current_user(self, token):
        """
        Retrieves the current user based on the access token.

        :param token: The access token to validate.
        :return: The database user associated with the token.
        :raises HTTPException: If the token is invalid or user is unauthorized.
        """
        db_user = self.verify_token(token, 'access')[0]
        if db_user.refresh_token:
            return db_user
        raise HTTPException(401, "Unauthorised")
    
    def verify_email(self, token:str):
        """
        Verifies a user's email address and returns the user if verified

        :param token: The token containing an encoded email
        :return: The user if verified otherwise, None
        :raises HTTPException: If verification fails.
        """
        serializer = self._getserializer(
            VERIFICATION_TOKEN_KEY, "email-configuration")
        email = self.decode_url_safe_token(token, serializer)
        db_user = self.user_crud.find_by(email=email)
        if db_user:
           return self.user_crud.update_fields(db_user.id,is_verified=True) is not None
               
        raise HTTPException(401, "[verify_email] Email could not be verified")

   
    def authenticate_user(self,  user:schemas.UserLogInSchema):
        """
        Authenticates a user and generates access and refresh tokens.

        :param user: The user login schema containing username and password.
        :return: A tuple containing the access token and refresh token.
        :raises HTTPException: If authentication fails.
        """
        db_user = self.user_crud.find_by(username=user.username)
        if not db_user.is_verified:
            raise HTTPException(403,"Email is not verfied")
        if db_user and self.verify_password(user.password, db_user.hashed_password):
            to_encode = {"sub": user.username}
            access_token = self.generate_access_token(to_encode)
            refresh_token = self.generate_refresh_token(to_encode)
            # db_user.refresh_token = refresh_token
            self.user_crud.update_fields(db_user.id, refresh_token=refresh_token)
            return access_token, refresh_token
        raise HTTPException(
            status_code=403, detail="Invalid username or password")
    
    def __create_user(self,  user:schemas.UserCreateSchema):
        """
        Creates  a new user in the database.

        :param user: The user creation schema containing user details.
        :raises HTTPException: If the email or username is already taken.
        :return: The newly created user.
        """
        if self.user_crud.find_by(email=user.email):
            raise HTTPException(
                status_code=400, detail="Email already registered")
        if self.user_crud.find_by(username=user.username):
            raise HTTPException(
                status_code=400, detail="Username already exists")
        return self.user_crud.create_new(user)
    

    def register_user(self, user:schemas.UserCreateSchema):
        """
        Registers a new user in the database.

        :param user: The user creation schema containing user details.
        :raises HTTPException: If the email or username is already taken.
        :return: The newly created user and the verification url token.
        """
        # Create new user
        new_user = self.__create_user(user)

        #generate verification token
        serializer = self._getserializer(VERIFICATION_TOKEN_KEY,"email-configuration")
        verification_token = self.generate_url_safe_token({"sub":new_user.email},serializer)

        return new_user, verification_token
    
    def request_reset(self, email):
        """
        Send reset link for password reset.

        :param email: The email to send the verification link to.
        :raises HTTPException: If the email or username is already taken.
        :return: The newly created user and the verification url token.
        """
        # Find th db_user
        db_user = self.user_crud.find_by(email=email)
        if not  db_user:
            raise HTTPException(404, "Email is not registered")
        # generate reset token link
        serializer = self._getserializer(RESET_TOKEN_KEY,"password-reset")
        reset_token = self.generate_url_safe_token({"sub":email},serializer)

        return reset_token

    def reset_password(self, token: str,password:str):
        """
        Verifies a user's email address and returns the user if verified

        :param token: The token containing an encoded email
        :return: The user if verified otherwise, None
        :raises HTTPException: If verification fails.
        """
        serializer = self._getserializer(RESET_TOKEN_KEY, "password-reset")
        email = self.decode_url_safe_token(token, serializer)

        db_user = self.user_crud.find_by(email=email)
        if db_user:
           hashed_password = self.hash_password(password)
           return self.user_crud.update_fields(db_user.id, hashed_password=hashed_password) is not None

        raise HTTPException(404, "[verify_email] Email could not be verified")


    def refresh(self, refresh_token):
        """
        Generates a new access token using the provided refresh token.

        :param refresh_token: The refresh token for the user.
        :return: The new access token.
        :raises HTTPException: If the refresh token is invalid or forbidden.
        """
        forbidden_except = HTTPException(403, "Forbidden!")

        # return username
        db_user, username = self.verify_token(refresh_token,'refresh')
        if username == db_user.username:
                # token_data = schemas.TokenDataSchema(username=username)
                encode_data = {"sub": username}
                access_token = self.generate_access_token(encode_data)
                return access_token
        else:
            # delete found user's refresh token
            self.user_crud.update_fields(db_user.id,refresh_token=None)
            raise forbidden_except


    def logout(self, refresh_token, username:str):
        """
        Logs out a user by invalidating their refresh token.

        :param refresh_token: The refresh token to invalidate.
        :param username: The username of the user attempting to log out.
        :raises HTTPException: If the user is unauthorized.
        """
        try:
            db_user = self.user_crud.find_by(refresh_token=refresh_token)
            if db_user is None:
                    return
            if db_user.username != username:                
                raise HTTPException('401','Unauthorised')
                 # reset token
        except:
            unauth_user = self.user_crud.find_by(username=username)
            self.user_crud.update_fields(
                unauth_user.id, refresh_token=None)
        
        self.user_crud.update_fields(db_user.id, refresh_token=None)

        


   
