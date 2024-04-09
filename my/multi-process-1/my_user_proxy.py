import sys
sys.path.append('./')

from typing import Callable
import autogen
import asyncio
import threading

print("UserProxyAgent START")
print("[user_proxy] thread name: ", threading.current_thread())
print("[user_proxy] event loop: ", asyncio.get_event_loop())

# --------------------------------------------------

# create a UserProxyAgent instance named "user_proxy"
user_proxy = autogen.UserProxyDAgent(
    name="user_proxy",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "temp_dir", "use_docker": False},
)

subscription = user_proxy.subscribe("nats://127.0.0.1:4222")

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