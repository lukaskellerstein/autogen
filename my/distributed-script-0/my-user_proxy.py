import sys
sys.path.append('./')
import os
from dotenv import load_dotenv
import autogen
import asyncio
import threading

load_dotenv()

print("UserProxyAgent START")
print("[user_proxy] thread name: ", threading.current_thread())
print("[user_proxy] event loop: ", asyncio.get_event_loop())

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
name="my-user_proxy"
system_message="You are a helpful AI Assistant."

# --------------------------------------------------


# create a UserProxyAgent instance named "user_proxy"
user_proxy = autogen.UserProxyDAgent(
    name=name,
    system_message=system_message,
    human_input_mode="TERMINATE",
    code_execution_config={"work_dir": "temp_dir"},
    broker_config=broker_config,
    db_config=db_config,
)

subscription = user_proxy.subscribe()

# --------------------------------------------------

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(subscription)
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

print("UserProxyAgent END")