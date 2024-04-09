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
name="user_proxy-me"
system_message="A human admin."

# --------------------------------------------------


# create a UserProxyAgent instance named "user_proxy"
user_proxy = autogen.UserProxyDAgent(
    name=name,
    system_message=system_message,
    human_input_mode="ALWAYS",
    code_execution_config={"last_n_messages": 2, "work_dir": "temp_dir"},
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