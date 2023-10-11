import sys
sys.path.append('../')

import autogen

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST.json",
    file_location="../",
)

print("config_list: ", config_list)
 
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
    code_execution_config={"work_dir": "temp_dir"},
)


# the assistant receives a message from the user, which contains the task description
user_proxy.initiate_chat(
    assistant,
    message="""
Plot a chart of NVDA and TESLA stock price change YTD and save it in file.
""",
)
