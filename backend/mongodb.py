from bson.binary import Binary
from pymongo import MongoClient
from bson.binary import UuidRepresentation
from uuid import UUID
MONGO_DATABASE_URL = 'mongodb://localhost:27017/'
MONGO_DB = 'chat_db'

client = MongoClient(MONGO_DATABASE_URL,
                     uuidRepresentation='standard')
db = client[MONGO_DB]

study_chat_logs_collection = db.chat_logs



def get_chat_logs_collection():
    return study_chat_logs_collection


def save_chat_log(session_id, messages, chat_logs_collection):
    chat_log = {
        "_id": session_id,
        "messages": messages
    }
    if chat_logs_collection.insert_one(chat_log):
        return True
    return None


def get_chat_logs(session_id, chat_logs_collection):
    return chat_logs_collection.find_one({"_id": session_id})


def update_chat_log(session_id, new_messages, chat_logs_collection):
    """
    Appends new messages to the existing chat log of a session.
    
    :param session_id: The unique ID of the session.
    :param new_messages: A list of new messages to append (e.g. [{"role": "user", "content": "new message"}])
    """
    # if chat_logs_collection.update_one(
    #     {"_id": session_id},  # Filter by session ID
    #     # Append new messages to the messages array
    #     {"$push": {"messages": {"$each": new_messages}}}
    # ):
    #     return True
    # return None
    # bson_session_id = Binary.from_uuid(session_id, uuid_representation=4)

    # Perform the update operation
    result = chat_logs_collection.update_one(
        {"_id": session_id},  # Filter by session ID
        {"$push": {"messages": {"$each": new_messages}}}  # Append new messages
    )

    # Check if any document was modified
    if result.modified_count > 0:
        return True
    return False
