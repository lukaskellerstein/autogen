import sys
sys.path.append('../autogen')

import autogen

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST.json",
    file_location="./",
)

print("config_list: ", config_list)



# CUSTOM FUNCTIONS ------------------------------------------------------------
assistant_for_expert = autogen.AssistantAgent(
        name="assistant_for_expert",
        llm_config={
            "temperature": 0,
            "config_list": config_list,
        },
    )

expert = autogen.UserProxyAgent(
    name="expert",
    human_input_mode="ALWAYS",
    code_execution_config={"work_dir": "temp_dir_2"},
)

# Implementation
def ask_expert(message):
    expert.initiate_chat(assistant_for_expert, message=message)
    expert.stop_reply_at_receive(assistant_for_expert)
    # expert.human_input_mode, expert.max_consecutive_auto_reply = "NEVER", 0
    # final message sent from the expert
    expert.send("summarize the solution and explain the answer in an easy-to-understand way", assistant_for_expert)
    # return the last message the expert received
    return expert.last_message()["content"]

def do_nothing(message):
    return f"Do nothing: ${message}"

# -----------------------------------------------------------------------------

# OpenAI definition
functions = [
    {
        "name": "ask_expert",
        "description": "ask expert when you can't solve the problem satisfactorily.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "question to ask expert. Make sure the question include enough context, such as the code and the execution result. The expert does not know the conversation between you and the user, unless you share the conversation with the expert.",
                },
            },
            "required": ["message"],
        },
    },
    {
        "name": "do_nothing",
        "description": "This function does nothing. It is used to test the system.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "message to echo back.",
                },
            },
            "required": ["message"],
        },
    }
]

 
# create an AssistantAgent instance named "assistant"
assistant_for_student = autogen.AssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant. Prefer to use provided functions, only if you are sure you don't need it, don't use it. Reply TERMINATE when the task is done.",
    llm_config={
        "config_list": config_list,  
        "temperature": 0,  
        "functions": functions,
        "function_call": "auto",
    }, 
)

function_map={
        "ask_expert": ask_expert,
        "do_nothing": do_nothing,
    }

# create a UserProxyAgent instance named "user_proxy"
student = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "temp_dir"},
    function_map=function_map,
)


# the assistant receives a message from the user, which contains the task description
student.initiate_chat(
    assistant_for_student,
    message="""Find $a + b + c$, given that $x+y \\neq -1$ and 
\\begin{align}
	ax + by + c & = x + 7,\\
	a + bx + cy & = 2x + 6y,\\
	ay + b + cx & = 4x + y.
\\end{align}.
""",
)

print("DONE")
