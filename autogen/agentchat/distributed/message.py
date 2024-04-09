
from typing import Dict


class Message(object):
    def __init__(self, message: Dict[str, str | object]):
        self.sender = message["sender"]
        self.action = message["action"]
        self.payload = message["payload"]