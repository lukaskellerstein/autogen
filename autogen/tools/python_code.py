
from autogen.agentchat.tool import BaseTool


class PythonCodeTool(BaseTool):

    def __init__(self, name = "Python Code runner", description = "This tools is able to run a python code") -> None:
        super().__init__(name, description)


    def run(self, *args, **kwargs):
        """run the tool"""
        print("PythonCode.run()")