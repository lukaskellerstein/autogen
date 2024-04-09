import pymongo

class MongoDbService:

    chat_messages_table = "chat_messages"
    teams_table = "teams"

    def __init__(self, db_name = "AutogenDB", host = "localhost", port = "27017", user = "admin", password = "password"):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.client = pymongo.MongoClient(f"mongodb://{user}:{password}@{host}:{port}/")
        self.db = self.client[db_name]

    def insert_message(self, chat_id, message):
        table = self.db[self.chat_messages_table + "_" + chat_id]
        table.insert_one(message)

    def get_team_members(self, team_name):
        table = self.db[self.teams_table]
        team = table.find_one({"name": team_name})
        team_members = team["members"]
        return team_members