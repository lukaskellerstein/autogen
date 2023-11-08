import sys
sys.path.append('../autogen')

import autogen

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST.json",
    file_location="./",
)

print("config_list: ", config_list)



# CUSTOM FUNCTIONS ------------------------------------------------------------
planner = autogen.AssistantAgent(
    name="planner",
    llm_config={"config_list": config_list},
    # the default system message of the AssistantAgent is overwritten here
    system_message="You are a helpful AI assistant. You suggest coding and reasoning steps for another AI assistant to accomplish a task. Do not suggest concrete code. For any action beyond writing code or reasoning, convert it to a step which can be implemented by writing code. For example, the action of browsing the web can be implemented by writing code which reads and prints the content of a web page. Finally, inspect the execution result. If the plan is not good, suggest a better plan. If the execution is wrong, analyze the error and suggest a fix."
)
planner_user = autogen.UserProxyAgent(
    name="planner_user",
    max_consecutive_auto_reply=0,  # terminate without auto-reply
    human_input_mode="NEVER",
)

# Implementation
def ask_planner(message):
    planner_user.initiate_chat(planner, message=message)
    # return the last message received from the planner
    return planner_user.last_message()["content"]

# -----------------------------------------------------------------------------

# OpenAI definition
functions = [
    {
        "name": "ask_planner",
        "description": "ask planner to: 1. get a plan for finishing a task, 2. verify the execution result of the plan and potentially suggest new plan.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "question to ask planner. Make sure the question include enough context, such as the code and the execution result. The planner does not know the conversation between you and the user, unless you share the conversation with the planner.",
                },
            },
            "required": ["message"],
        },
    }
]

 
# create an AssistantAgent instance named "assistant"
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={
        "config_list": config_list,  
        "temperature": 0,  
        "functions": functions,
    }, 
)


function_map={
        "ask_planner": ask_planner
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
Suggest how to implement statistical arbitrage in python.
""",
)

print("DONE")
