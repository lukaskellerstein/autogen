# import sys
# sys.path.append('../')

import autogen

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST.json",
    file_location="./",
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
    code_execution_config={"work_dir": "temp_dir", "use_docker": True},
)

user_proxy.initiate_chat(
    assistant,
    message="""
Is the code below correct? Do you some problems with it? If so, please fix it.

```python
print("--------------------------------------------")
print("--------------------------------------------")
print("--------------------------------------------")
print("HAHAHAHAHA FROM USER PROXY")
print("--------------------------------------------")
print("--------------------------------------------")
print("--------------------------------------------")
```
""",
)



print("DONE")