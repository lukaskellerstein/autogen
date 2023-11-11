from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen import config_list_from_json

# ------------
# Config
# ------------
config_list = config_list_from_json(
    "OAI_CONFIG_LIST.json",
    file_location="./",
)

print("config_list: ", config_list)

# ------------
# Bots
# ------------

assistant = RetrieveAssistantAgent(
    name="assistant",
    llm_config={
        "config_list": config_list,  
        "temperature": 0,  
    }, 
)

user_proxy = RetrieveUserProxyAgent(
    name="user_proxy",
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "temp_dir"},
)


# ------------
# CHAT
# ------------

user_proxy.initiate_chat(
    assistant,
    problem="""
What is ARI?
""",
)


print("DONE")
