import sys
sys.path.append('./')

import autogen
import asyncio
import threading

print("AssistantAgent START")
print("[assistant] thread name: ", threading.current_thread())
print("[assistant] event loop: ", asyncio.get_event_loop())

# --------------------------------------------------

print(autogen.__file__)

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST.json",
    file_location="./",
)

print("config_list: ", config_list)

# create an AssistantAgent instance named "assistant"
assistant = autogen.AssistantDAgent(
    name="assistant",
    llm_config={
        "config_list": config_list,  
        "temperature": 0,  
    }, 
)

subscription = assistant.subscribe("nats://127.0.0.1:4222")

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