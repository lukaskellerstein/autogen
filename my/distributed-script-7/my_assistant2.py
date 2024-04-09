import sys
sys.path.append('./')
import os
from dotenv import load_dotenv
import autogen
import asyncio
import threading

load_dotenv()

print("AssistantAgent START")
print("[assistant] thread name: ", threading.current_thread())
print("[assistant] event loop: ", asyncio.get_event_loop())

# --------------------------------------------------
# ENV VARS
broker_config = {
    "url": os.getenv("BROKER_URL", "127.0.0.1:4222"),
    "user": os.getenv("BROKER_USER", "alice"),
    "password": os.getenv("BROKER_PASSWORD", "foo"),
}
print("broker_config: ", broker_config)

db_config = {
    "url": os.getenv("DB_URL", "localhost:27017")
}
print("db_config: ", db_config)

team_name="my_first_team"
name="assistant2-product_manager"
system_message="Creative in software product ideas."


# --------------------------------------------------

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST.json",
    file_location="./",
)

llm_config={
    "config_list": config_list,  
    "temperature": 0,  
}
print("llm_config: ", llm_config)

# --------------------------------------------------

# create an AssistantAgent instance named "assistant"
assistant = autogen.AssistantDAgent(
    name=name,
    system_message=system_message,
    llm_config=llm_config, 
    broker_config=broker_config,
    db_config=db_config,
)

subscription = assistant.subscribe()

# --------------------------------------------------

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(subscription)
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

print("AssistantAgent END")