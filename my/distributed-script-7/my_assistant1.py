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
name="assistant1-coder"
system_message="""You are a helpful AI assistant.
    Solve tasks using your coding and language skills.
    In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute.
        1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time, check the operating system. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself.
        2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly.
    Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill.
    When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user.
    If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user.
    If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
    When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.
    Reply "TERMINATE" in the end when everything is done."""

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