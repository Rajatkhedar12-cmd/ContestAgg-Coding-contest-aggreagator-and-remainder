import pymongo
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Get values from .env
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
users_col = db["users"]
contests_col = db["contests"]
favorites_col = db["favorites"]
