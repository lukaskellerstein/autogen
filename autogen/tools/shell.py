
from autogen.agentchat.tool import BaseTool


class ShellTool(BaseTool):
        def __init__(self, name = "Shell runner", description = "This tool is able to run a terminal command") -> None:
            super().__init__(name, description)
    
        def run(self, *args, **kwargs):
            """run the tool"""
            print("ShellTool.run()")