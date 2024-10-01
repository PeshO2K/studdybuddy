from pymongo import MongoClient

MONGO_DATABASE_URL = 'mongodb://localhost:27017/'
MONGO_DB = 'chat_db'

client = MongoClient(MONGO_DATABASE_URL,
                     uuidRepresentation='standard')
db = client[MONGO_DB]

study_chat_logs_collection = db.chat_logs



def get_collection():
    return study_chat_logs_collection
