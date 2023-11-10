import threading
from threading import Thread
import autogen
import asyncio
import websockets
import json

from typing import Callable

async def init_my_autogen():
    print("[init_my_autogen] thread name: ", threading.current_thread())
    print("[init_my_autogen] event loop: ", asyncio.get_event_loop())

    config_list = autogen.config_list_from_json(
        "OAI_CONFIG_LIST.json",
        file_location="./",
    )

    # create an AssistantAgent instance named "assistant"
    assistant = autogen.AssistantAgent(
        name="assistant",
        llm_config={
            "config_list": config_list,  
            "temperature": 0,  
        }, 
    )

    # create a UserProxyAgent instance named "user_proxy"
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply=10,
        code_execution_config={"work_dir": "temp_dir", "use_docker": False},
    )

    # Listening for a start of conversation
    try:
        name = "init_chat"
        async with websockets.connect("ws://localhost:8000") as websocket:

            # send registration message
            register_message = json.dumps({"action": "register", "payload": name})
            await websocket.send(register_message)

            # start listening
            while True:
                message = await websocket.recv()
                print(f"[{name}] receive message: {message}")

                user_proxy.initiate_chat(
                    assistant,
                    message=message,
                )

    except websockets.ConnectionClosed as e:
        print(f"WebSocket connection closed: {e}")
    except Exception as e:
        print(f"Error occurred: {e}")


# ---------------------------------------------------
# Threads
# ---------------------------------------------------
def launch_event_loops(async_method: Callable):
    print("[launch_event_loops] thread name: ", threading.current_thread())
    
    # get a new event loop
    loop = asyncio.new_event_loop()

    # set the event loop for the current thread
    asyncio.set_event_loop(loop)

    print("[launch_event_loops] event loop: ", asyncio.get_event_loop())

    try:
        # run a coroutine on the event loop
        loop.run_until_complete(async_method())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


if __name__ == "__main__":

    print("[MAIN] thread name: ", threading.current_thread())
    print("[MAIN] event loop: ", asyncio.get_event_loop())

    t1 = Thread(target=launch_event_loops, args=[autogen.message_broker])
    t2 = Thread(target=launch_event_loops, args=[init_my_autogen])

    t1.start()
    t2.start()

    # Block the main tread
    print("t1.join()")
    t1.join()
    print("t2.join()")
    t2.join()



print("DONE")