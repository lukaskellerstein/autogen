import sys
sys.path.append('../')

import autogen


from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())  # read local .env file

config_list = autogen.config_list_from_models(model_list=["gpt-4"])

# config_list = autogen.config_list_from_json(
#     "OAI_CONFIG_LIST.json",
#     file_location="../",
# )

# print("config_list: ", config_list)
 
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

# user_proxy.initiate_chat(
#     assistant,
#     message="""
# My goal is to understand the difference between LangChain and AutoGen. Provide me steps that I can follow and use a python code or sh scripts in these steps, so I can follow and run it step by step and achieve the result.
# """,
# )

# user_proxy.initiate_chat(
#     assistant,
#     message="""
# Write a code that search on the web what is LangChain and AutoGen, run the code, compare the results of your findings and give me a summary.
# """,
# )

user_proxy.initiate_chat(
    assistant,
    message="""
Search on the web what is LangChain and AutoGen, compare the results of your findings and give me a summary.

Use a google-search-results library. Here is a SERPAPI_API_KEY=9c2c704a267e5e078e3d6f7ee70d032acc338511f038359d61069eea91065e78
""",
)
