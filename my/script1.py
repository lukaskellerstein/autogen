# import sys
# sys.path.append('../')

import autogen

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST.json",
    file_location="./",
)

print("config_list: ", config_list)


# tools
# tools = [ autogen.ShellTool(), autogen.PythonCodeTool(), autogen.ChromaDbTool()]


# create an AssistantAgent instance named "assistant"
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={
        "config_list": config_list,  
        "temperature": 0,  
    }, 
    # tools=tools,
)

# create a UserProxyAgent instance named "user_proxy"
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "temp_dir", "use_docker": False},
)


# # the assistant receives a message from the user, which contains the task description
# user_proxy.initiate_chat(
#     assistant,
#     message="""
# Plot a chart of NVDA and TESLA stock price change YTD and save it in file.
# """,
# )

# --------------------------------------------------------------------------------------------
# Idea 1: Support NodeJS, Dotnet, Golang
# --------------------------------------------------------------------------------------------

# user_proxy.initiate_chat(
#     assistant,
#     message="""
# Create a simple expressjs server and run it.
# """,
# )

# user_proxy.initiate_chat(
#     assistant,
#     message="""
# Create a simple ASPNET Core server and run it.
# """,
# )

# user_proxy.initiate_chat(
#     assistant,
#     message="""
# Create a simple Golang server and run it.
# """,
# )

# --------------------------------------------------------------------------------------------
# Idea 2: Support docker
# --------------------------------------------------------------------------------------------
user_proxy.initiate_chat(
    assistant,
    message="""
Create a simple Python server.
""",
)



print("DONE")