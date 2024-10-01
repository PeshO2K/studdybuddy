from fastapi import  HTTPException
from . import models, schemas
from .auth import PasswordHandler
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from uuid import UUID
from typing import Optional, List,Dict
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CRUDMongo:
    """
    Handles CRUD operations for MongoDB chat logs.
    """
    def __init__(self, collection):
        """
        Initializes the CRUDMongo instance with a specified collection.

        Args:
            collection: The MongoDB collection to operate on.
        """
        self.collection = collection

    def save_chat_log(self, session_id: UUID, messages: List[Dict]) -> bool:
        """
        Saves a chat log to the MongoDB collection.
        
        Args:
            session_id (UUID): The unique identifier for the chat session.
            messages (List[Dict]): A list of message dictionaries to be saved.

        Returns:
            bool: True if the chat log was saved successfully, False otherwise.
        """
        
        try:
            chat_log = {
                "_id": session_id,
                "messages": messages,
                "updated_at": datetime.now(timezone.utc)
            }
            result = self.collection.insert_one(chat_log)
            return result.acknowledged
        except Exception as e:
            logger.error(f"Error saving chat log for session {session_id}: {e}")
            return False
        

    def get_chat_log(self, session_id: UUID) -> Optional[Dict]:
        """
        Retrieves a chat log from the MongoDB collection.
        
        Args:
            session_id (UUID): The unique identifier for the chat session.

        Returns:
            Optional[Dict]: The chat log as a dictionary if found, None otherwise.
        """
        return self.collection.find_one({"_id": session_id})

    def update_chat_log(self, session_id: UUID, new_messages: List[Dict]) -> bool:
        """
        Updates an existing chat log by appending new messages.
        
        Args:
            session_id (UUID): The unique identifier for the chat session.
            new_messages (List[Dict]): A list of new message dictionaries to append.

        Returns:
            bool: True if the chat log was updated successfully, False otherwise.
        """
        try:
            result = self.collection.update_one(
                {"_id": session_id},
                {"$push": {"messages": {"$each": new_messages}},
                 "$set": {"updated_at": datetime.now(timezone.utc)}
                #  "$currentDate": {"updated_at": True}
                 }

            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating chat log for session {session_id}: {e}")
            return False


        

    def delete_chat_log(self, session_id: UUID) -> bool:
        """
        Deletes a chat log from the MongoDB collection.
        
        Args:
            session_id (UUID): The unique identifier for the chat session.

        Returns:
            bool: True if the chat log was deleted successfully, False otherwise.
        """
        try:
            result = self.collection.delete_one({"_id": session_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting chat log for session {session_id}: {e}")
            return False
        

    def find_all_chat_logs(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """
        Retrieves all chat logs from the MongoDB collection with pagination.
        
        Args:
            skip (int): The number of documents to skip (for pagination).
            limit (int): The maximum number of documents to return.

        Returns:
            List[Dict]: A list of chat logs as dictionaries.
        """
        return list(self.collection.find().skip(skip).limit(limit))


class CRUDSql:
    """
    Handles CRUD operations for SQL database models.
    """
    def __init__(self, db: Session):
        """
        Initializes the CRUDSql instance with a specified SQL session.
        
        Args:
            db (Session): The SQLAlchemy session to operate on.
        """
        self.db = db

    def create(self, obj):
        """
        Creates a new object in the database.
        
        Args:
            obj: The object to create.

        Returns:
            The created object if successful, None otherwise.
        """
        try:
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
        except Exception as e:
            logger.error(f"Error creating: {e}")
            self.db.rollback()
            obj = None
        return obj

    def update(self, model, id, **kwargs):
        """
        Updates an existing object in the database.
        
        Args:
            model: The model class of the object to update.
            id: The unique identifier of the object to update.
            **kwargs: The fields to update.

        Returns:
            The updated object if successful, None otherwise.
        """
        existing_obj = self.find_by(model, id=id)
        if existing_obj:
            try:
                for key, value in kwargs.items():
                    setattr(existing_obj, key, value)
                self.db.commit()
                self.db.refresh(existing_obj)
                return existing_obj
            except Exception as e:
                logger.error(f"Error updating object {id}: {e}")
                self.db.rollback()

        return None

    def delete(self, obj):
        """
        Deletes an object from the database.
        
        Args:
            obj: The object to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        try:
            self.db.delete(obj)
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting object: {e}")
            self.db.rollback()
            return False

    def save(self):
        """
        Commits the current transaction.
        
        Returns:
            bool: True if the save was successful, False otherwise.
        """
        try:
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving: {e}")
            self.db.rollback()
            return False

    def find_by(self, model: models, **kwargs):
        """
        Finds an object in the database by specified criteria.

        Args:
            model: The model class to query.
            **kwargs: The criteria to filter by.

        Returns:
            The found object if any, None otherwise.
        """
        return self.db.query(model).filter_by(**kwargs).first()

    def find_all(self, model: models, skip: int = 0, limit: int = 100, **kwargs) -> List:
        """
        Finds all objects in the database matching specified criteria with pagination.
        
        Args:
            model: The model class to query.
            skip (int): The number of documents to skip (for pagination).
            limit (int): The maximum number of documents to return.
            **kwargs: The criteria to filter by.

        Returns:
            List: A list of found objects.
        """
        return self.db.query(model).filter_by(**kwargs).offset(skip).limit(limit).all()

# User-specific CRUD operations


class UserCRUD(PasswordHandler):
    """
    Handles user-specific CRUD operations.
    """
    def __init__(self, db: Session):
        """
        Initializes the UserCRUD instance with a specified SQL session.

        Args:
            db (Session): The SQLAlchemy session to operate on.
        """
        self.db_crud = CRUDSql(db)

    def create_new(self, user_data: schemas.UserCreateSchema) -> Optional[models.User]:
        """
        Creates a new user in the database.
        
        Args:
            user_data (schemas.UserCreateSchema): The user data to create.

        Returns:
            Optional[models.User]: The created user object if successful, None otherwise.
        """
        hashed_password = self.hash_password(user_data.password)
        new_user = models.User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )

        return self.db_crud.create(new_user)

    def update_fields(self, user_id, **kwargs) -> Optional[models.User]:
        """
        Updates specified fields of a user.
        
        Args:
            user_id: The unique identifier of the user to update.
            **kwargs: The fields to update.

        Returns:
            Optional[models.User]: The updated user object if successful, None otherwise.
        """
        return self.db_crud.update(models.User, user_id, **kwargs)

    def find_by(self, **kwargs) -> Optional[models.User]:
        """
        Finds a user in the database by specified criteria.
        
        Args:
            **kwargs: The criteria to filter by.

        Returns:
            Optional[User]: The found user object if any, None otherwise.
        """
        return self.db_crud.find_by(models.User, **kwargs)

    def find_all(self, **kwargs) -> Optional[List[models.User]]:
        """
        Finds all users in the database matching specified criteria.

        Args:
            **kwargs: The criteria to filter by.

        Returns:
            Optional[List[models.User]]: A list of found user objects, or None if no users were found.
        """
        return self.db_crud.find_all(models.User, **kwargs)


class Formatter:
    """
    Provides methods for formatting and transforming data.
    """
    def reformat(self, item_list: list = [], key: str = 'id') ->  Optional[Dict]:
        """
        Reformats a list of items into a dictionary keyed by a specified key.
        
        Args:
            item_list (list): A list of items to format.
            key (str): The key to use for the dictionary keys.

        Returns:
            Optional[Dict]: A dictionary with the specified key as keys and formatted items as values if the list is not empty, None otherwise.
        """

        if len(item_list):
            formatted_dict={}
            for item in item_list:
                item  = self.exclude_keys([],item)
                formatted_dict[item[key]] = self.exclude_keys(
                    [key, '__class__'], item)
                # formatted_dict[item[key]] = {x:item[x] for x in item if x != key and  x!='__class__'}
            return formatted_dict

        return None
    def to_datetime(self, datetime_str):
        """
        Converts a string to a datetime object.
        
        Args:
            datetime_str: The string representation of a datetime.

        Returns:
            datetime: A datetime object if the input is valid, otherwise it attempts to parse it.
        """
        date_format = "%Y-%m-%dT%H:%M:%S.%f"
        if isinstance(datetime_str, datetime):
            return datetime_str
        return datetime.strptime(datetime_str,date_format)
    
    def __to_dict(self,dict_obj):
        """
        Converts an object to a dictionary representation.
        
        Args:
            dict_obj: The object to convert.

        Returns:
            dict: A dictionary representation of the object.
        """
        try:
            dict_obj = dict_obj.to_dict()
        except:
            dict_obj = dict_obj.model_dump()
        return dict_obj
    
    def exclude_keys(self, keys_to_exclude=[], dictionary=None):
        """
        Excludes specified keys from a dictionary.
        
        Args:
            keys_to_exclude (list): The keys to exclude from the dictionary.
            dictionary (dict, optional): The original dictionary from which to exclude keys.

        Returns:
            dict: A new dictionary excluding the specified keys.
        """
        
        if dictionary:
            if not isinstance(dictionary,dict):
                dictionary = self.__to_dict(dictionary)
            formatted_dict = {
                key: dictionary[key] for key in dictionary if key not in keys_to_exclude}
            return formatted_dict
        
    def include_keys(self, keys_to_include=[], dictionary=None):
        """
        Includes only specified keys from a dictionary.
        
        Args:
            keys_to_include (list): The keys to include in the new dictionary.
            dictionary (dict, optional): The original dictionary to filter.

        Returns:
            dict: A new dictionary containing only the specified keys.
        """
        if dictionary and len(keys_to_include):
            if not isinstance(dictionary, dict):
                dictionary = self.__to_dict(dictionary)
            formatted_dict = {
                key: dictionary[key] for key in dictionary if key in keys_to_include}
            return formatted_dict



# Chat session-specific CRUD operations
class ChatSessionCRUD(Formatter):   
    """
    Handles CRUD operations for chat sessions while utilizing the Formatter class for data formatting.
    """
    def __init__(self, db: Session, collection=None):
        """
        Initializes the ChatSessionCRUD instance with a specified SQL session and optional MongoDB collection.
        
        Args:
            db (Session): The SQLAlchemy session to operate on.
            collection: The MongoDB collection for chat logs (if any).
        """
        self.sql_crud = CRUDSql(db)
        
        self.mongo_crud = CRUDMongo(collection) if collection is not None else None

    def create_new(self, chat_session_data: schemas.ChatSessionCreateSchema, user_id: str) -> Optional[models.ChatSession]:
        """
        Creates a new chat session and saves its metadata and logs.
        
        Args:
            chat_session_data (schemas.ChatSessionCreateSchema): The data for the new chat session.
            user_id (str): The ID of the user creating the session.

        Returns:
            Optional[models.ChatSession]: The created chat session object if successful, None otherwise.
        """
        new_chat_session = models.ChatSession(
            title=chat_session_data.title,
            user_id=user_id
        )
        # Create metadata first in sql:
        chat_metadata = self.sql_crud.create(new_chat_session)
        if chat_metadata:
            # create an empty log for the chat
            chat_log = self.mongo_crud.save_chat_log(
                chat_metadata.id, chat_session_data.messages)
            if chat_log:
                return chat_metadata
            self.sql_crud.delete(chat_metadata)
        return None

    def format(self, session_list, key:str='id') -> Optional[Dict]:
        """
        Formats a list of chat sessions into a dictionary keyed by the specified key.
        
        Args:
            session_list: A list of chat sessions to format.
            key (str): The key to use for the dictionary keys.

        Returns:
            Optional[Dict]: A formatted dictionary if successful, None otherwise.
        """
        return self.reformat(session_list,key)
        
    def find_by(self, **kwargs) -> Optional[models.ChatSession]:
        """
        Finds a chat session by specified criteria.
        
        Args:
            **kwargs: The criteria to filter by.

        Returns:
            Optional[models.ChatSession]: The found chat session object if any, None otherwise.
        """
        return self.sql_crud.find_by(models.ChatSession, **kwargs)
    
    def is_user_session(self, user_id, session_id) -> Optional[models.ChatSession]:
        """
        Checks if a given session belongs to the specified user.
        
        Args:
            user_id: The ID of the user to check.
            session_id: The ID of the session to check.

        Returns:
            Optional[models.ChatSession]: The chat session object if found, raises an exception if not found.
        """
        user_session = self.sql_crud.find_by(
            models.ChatSession, id=session_id, user_id=user_id)
        if user_session:
            return user_session
        raise HTTPException(404,"Session Not Found")
    
        # return self.sql_crud.find_by(models.ChatSession, id=session_id,user_id=user_id)

    def find_all(self, **kwargs) -> Optional[List[models.ChatSession]]:
        """
        Finds all chat sessions matching specified criteria.

        Args:
            **kwargs: The criteria to filter by.

        Returns:
            Optional[List[models.ChatSession]]: A list of found chat session objects, or None if no sessions were found.
        """
        return self.sql_crud.find_all(models.ChatSession, **kwargs)

    def update_chat(self, session_id, chat_session: schemas.ChatSessionUpdateSchema, user_id) -> Optional[models.ChatSession]:
        """
        Updates the chat session details and logs for a specific session.
        
        Args:
            session_id: The ID of the session to update.
            chat_session (schemas.ChatSessionUpdateSchema): The updated session data.
            user_id: The ID of the user making the update.

        Returns:
            Optional[models.ChatSession]: The updated session object if successful, None otherwise.
        """
        db_session = self.is_user_session(user_id,session_id)
        updated_title = False
        updated_log = False

        # update the title
        if chat_session.title and chat_session.title != db_session.title:
            #update the title
            updated_title = self.update_fields(session_id, title=chat_session.title, updated_at=datetime.now(timezone.utc))
        if chat_session.messages:
            updated_log = self.update_logs(session_id, chat_session.messages)
        return updated_title , updated_log
        
        # return self.sql_crud.update(models.ChatSession, session_id, **kwargs)
    
    def update_fields(self, session_id, **kwargs)-> Optional[models.ChatSession]:
        """
        Updates specified fields of a chat session.

        Args:
            session_id: The ID of the session to update.
            **kwargs: The fields to update.

        Returns:
            Optional[models.ChatSession]: The updated chat session object if successful, None otherwise.
        """
        return self.sql_crud.update(models.ChatSession, session_id, **kwargs)

    def update_logs(self, session_id, messages) -> bool:
        """
        Updates the chat logs for a specific session.
        
        Args:
            session_id: The ID of the session to update.
            messages: The messages to update in the chat log.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        return self.mongo_crud.update_chat_log(session_id, messages)
    
    def get_logs(self, session_id,user_id)-> Optional[Dict]:
        """
        Retrieves the chat logs for a specific session.

        Args:
            session_id: The ID of the session to retrieve logs for.
            user_id: The ID of the user requesting the logs.

        Returns:
            Optional[Dict]: The chat logs if successful, None otherwise.
        """
        self.is_user_session(user_id,session_id)
        return self.mongo_crud.get_chat_log(session_id)
    
    def get_session(self, session_id, user_id) -> Dict:
        """
        Retrieves both metadata and logs for a specific chat session.
        
        Args:
            session_id: The ID of the session to retrieve.
            user_id: The ID of the user requesting the session.

        Returns:
            Dict: A dictionary containing both chat metadata and logs.
        """
        chat_metadata = self.is_user_session(user_id, session_id).to_dict()
        chat_log = self.mongo_crud.get_chat_log(session_id)
        metadata_updated_at = self.to_datetime(chat_metadata['updated_at'])
        log_updated_at = self.to_datetime(chat_log['updated_at'])
        
        # return most recent update date
        try:
            if metadata_updated_at > log_updated_at:
                log_date = chat_log.pop('updated_at', None)
                chat_log['log_updated_at'] = log_date
                
            else:
                meta_date = chat_metadata.pop('updated_at', None)
                chat_metadata['metadata_updated_at'] = meta_date
                
            
        except Exception as e:
            logger.error(f"Error updating chat log for session {session_id}: {e}")
            raise HTTPException(500, f"An error has occured during retrieval")

                
        # return chat_metadata, chat_log
        return {**chat_metadata, ** chat_log}
