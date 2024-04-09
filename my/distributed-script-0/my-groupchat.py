import sys
sys.path.append('./')
import os
from dotenv import load_dotenv
from typing import Callable
import autogen
import asyncio
import threading
import pymongo

load_dotenv()

print("GroupChat START")
print("[group_chat] thread name: ", threading.current_thread())
print("[group_chat] event loop: ", asyncio.get_event_loop())

# --------------------------------------------------
# ENV VARS
broker_config = {
    "url": os.getenv("BROKER_URL", "127.0.0.1"),
    "port": os.getenv("BROKER_PORT", "4222"),
    "user": os.getenv("BROKER_USER", "alice"),
    "password": os.getenv("BROKER_PASSWORD", "foo"),
}
print("broker_config: ", broker_config)

db_config = {
    "url": os.getenv("DB_URL", "localhost"),
    "port": os.getenv("DB_PORT", "27017"),
    "name": os.getenv("DB_NAME", "AutogenDB"), 
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", "password"),
}
print("db_config: ", db_config)

team_name="my_team"
name="groupchat_manager"

# --------------------------------------------------

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST.json",
    file_location="./",
)

print("config_list: ", config_list)

llm_config={
    "config_list": config_list,  
    "temperature": 0,  
}
print("llm_config: ", llm_config)
# --------------------------------------------------

# GET FROM DATABASE (table TEAMS) info about the team


# connect to mongo
db = autogen.MongoDbService(db_config["name"], db_config["url"], db_config["port"], db_config["user"], db_config["password"])
team_members = db.get_team_members(team_name)
print("team_members: ", team_members)

groupchat = autogen.DGroupChat(agents=team_members, messages=[], max_round=12)
manager = autogen.DGroupChatManager(
    name=name, 
    groupchat=groupchat, 
    llm_config=llm_config, 
    broker_config=broker_config,
    db_config=db_config,
)

subscription = manager.subscribe()

# --------------------------------------------------

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(subscription)
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

print("GroupChat END")