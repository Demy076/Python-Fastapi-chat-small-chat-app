import os
from dotenv import dotenv_values
import pymongo

root_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

config = dotenv_values(os.path.join(root_folder, ".env"))

__client = pymongo.MongoClient(config["MONGO_URI"])
__database = __client["users"]
messages = __database["messages"]
sessions = __database["sessions"]
