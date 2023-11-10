
class MessagesStorage(object):
    messages = []
    def __init__(self) -> None:
        pass

    def add_message(self, message):
        self.messages.append(message)
        print("[MessagesStorage] messages: ", self.messages)
    
    def get_messages(self):
        return self.messages