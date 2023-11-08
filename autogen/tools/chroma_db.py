
from autogen.agentchat.tool import BaseTool


class ChromaDbTool(BaseTool):

    def __init__(self, name = "Chroma DB", description = "This tools is able to access any data stored in vector database.") -> None:
        super().__init__(name, description)


    def run(self, *args, **kwargs):
        """run the tool"""
        print("ChromaDbTool.run()")