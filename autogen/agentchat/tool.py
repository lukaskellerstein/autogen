from abc import ABC, abstractmethod

class BaseTool(ABC):
    def __init__(self, name, description) -> None:
        super().__init__()
        self.name = name
        self.description = description

    @abstractmethod
    def run(self, *args, **kwargs):
        """run the tool"""

