from pymongo import MongoClient
import os
from dotenv import load_dotenv
# MONGO_DATABASE_URL = 'mongodb://localhost:27017/'
# MONGO_DB = 'chat_db'

# client = MongoClient(MONGO_DATABASE_URL,
#                      uuidRepresentation='standard')
# db = client[MONGO_DB]

load_dotenv()

# Get MongoDB details from environment variables
MONGO_DATABASE_URL = os.getenv(
    'MONGO_DATABASE_URL', 'mongodb://localhost:27017/')
MONGO_DB = os.getenv('MONGO_DB', 'chat_db')

# Connect to MongoDB
client = MongoClient(MONGO_DATABASE_URL, uuidRepresentation='standard')
db = client[MONGO_DB]

study_chat_logs_collection = db.chat_logs



def get_collection():
    return study_chat_logs_collection
