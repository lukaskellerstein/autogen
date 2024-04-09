import sys
sys.path.append('../autogen')

import autogen

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST.json",
    file_location="./",
)

print("config_list: ", config_list)

llm_config={
        "config_list": config_list,  
        "temperature": 0,  
    }

print("llm_config: ", llm_config)


# create a UserProxyAgent instance named "user_proxy"
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    system_message="A human admin.",
    human_input_mode="TERMINATE",
    code_execution_config={"last_n_messages": 2, "work_dir": "temp_dir"},
)

# create an AssistantAgent instance named "assistant"
coder = autogen.AssistantAgent(
    name="assistant1-coder",
    llm_config=llm_config 
)

pm = autogen.AssistantAgent(
    name="assistant2-product_manager",
    system_message="Creative in software product ideas.",
    llm_config=llm_config,
)

# ----------
# Group Chat
# ----------
groupchat = autogen.GroupChat(agents=[user_proxy, coder, pm], messages=[], max_round=12)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)


# the assistant receives a message from the user, which contains the task description
user_proxy.initiate_chat(
    manager,
    message="""
Find a latest paper about gpt-4 on arxiv and find its potential applications in software.
""",
)

print("DONE")
