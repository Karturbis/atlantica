import sqlite3
import json

json_file = "language_handler_de_data/verben_0-1mio.json"
database = "language_handler_de_data/test_json_to.sqlite"
database_table = "verben"


with open(json_file, "r", encoding="utf-8") as reader:
    data = json.load(reader)


class DatabaseHandler:
    """Handles the sqlite instances,
    reads and writes to sqlite databases..."""

    def __init__(self, database: str) -> None:
        self.__connection = sqlite3.connect(database)
        self.__cursor = self.__connection.cursor()

    def execute_command(self, command):
        self.__cursor.execute(command)
        self.__connection.commit()


db_handler = DatabaseHandler(database)

for i in data:
    command = f"INSERT INTO {database_table}(id, form, lemma, tags, last_modified, lemma_with_prefix_marker)\nVALUES("
    for key, value in i.items():
        command = f"{command}'{value}',"
    command = f"{command[:-1]});"
    print(command)
    db_handler.execute_command(command)
