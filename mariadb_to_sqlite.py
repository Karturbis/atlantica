import sqlite3
import json

lines = 12

with open("language_handler_de_data/verben_0-500000.json", "r") as reader:
    data = json.load(reader)
class DatabaseHandler:
    """Handles the sqlite instances,
    reads and writes to sqlite databases..."""

    def __init__(self, database: str) -> None:
        self.__connection = sqlite3.connect(database)
        self.__cursor = self.__connection.cursor()
    
    def execute_command(self, command):
        return self.__cursor.execute(command)

db_handler = DatabaseHandler("language_handler_de_data/test_json_to.sqlite")

for i in data:
    for j in i:
        db_handler.execute_command(j)