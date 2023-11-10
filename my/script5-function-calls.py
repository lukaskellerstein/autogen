import sys

from autogen.code_utils import execute_code
sys.path.append('../autogen')

import subprocess
import autogen

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST.json",
    file_location="./",
)

print("config_list: ", config_list)



# CUSTOM FUNCTIONS ------------------------------------------------------------

# Implementation
def run_python_code(code: str, language: str = "python"):
    print("run_python_code - input: ", code)

    result = execute_code(code, filename="temp.py", work_dir="temp_dir", use_docker=False)

    print("run_python_code - output: ", result)
    return result

def run_shell_code(command: str):
    print("run_shell_code: ", command)
    return { "result": "True" }

def query_chroma_db(query: str):
    print("query_chroma_db: ", query)
    return { "result" : "Some result from ChromaDB" }

def search_web(query: str):
    print("search_web: ", query)
    return { "result" : "65 years" }

def browser_web(url: str):
    print("browser_web: ", url)
    return { "result" : "Some result from browser_web" }


# OpenAI definition
functions = [
    {
        "name": "run_python_code",
        "description": "Use this function to run any Python code. The code needs to be in a markdown code block. The output will be in string representing result of Python code.",
        "parameters": {
            "type": "object",
            "properties": {
                "language": {
                    "type": "string",
                    "description": "The language of the code, e.g. 'python'",
                },
                "code": {
                    "type": "string",
                    "description": "The python code to run, e.g. ```Python print('Hello World')```",
                }
            },
            "required": ["code"],
        },
    },
    {
        "name": "run_shell_code",
        "description": "Use this function to run any shell command. The command needs to be in a markdown code block. The output will be in JSON format.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to run, e.g. ```Shell echo 'Hello World'```",
                }
            },
            "required": ["command"],
        },
    },
    {
        "name": "query_chroma_db",
        "description": "Use this function to query ChromaDB. The query is string representing searched text. The output will be in JSON format.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to run, e.g. 'What is CDP?'",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "search_web",
        "description": "Use this function to search the web. The query is string representing searched text. The output will be in JSON format.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to run, e.g. 'What is CDP?'",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "browser_web",
        "description": "Use this function to browser the web. The url is string representing the url to browser. The output will be in JSON format.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The url to browser, e.g. 'https://www.google.com'",
                }
            },
            "required": ["url"],
        },
    },
]

 
# create an AssistantAgent instance named "assistant"
assistant = autogen.AssistantAgent(
    name="assistant",
    system_message="For coding tasks, only use the functions you have been provided with. After each fix of the code, use again the functions that you have been provided with. Reply TERMINATE when the task is done.",
    llm_config={
        "config_list": config_list,  
        "temperature": 0,  
        "functions": functions,
        "function_call": "auto"
    }, 
)


function_map={
        "run_python_code": run_python_code,
        "run_shell_code": run_shell_code,
        "query_chroma_db": query_chroma_db,
        "search_web": search_web,
        "browser_web": browser_web,
    }

# create a UserProxyAgent instance named "user_proxy"
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "temp_dir"},
    function_map=function_map,
)


# the assistant receives a message from the user, which contains the task description
user_proxy.initiate_chat(
    assistant,
    message="""
Draw two agents chatting with each other with an example dialog. Don't add plt.show().
""",
)

print("DONE")
