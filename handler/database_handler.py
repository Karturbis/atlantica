import sqlite3
import platform

class DatabaseHandler:
    """Handles the sqlite instances,
    reads and writes to sqlite databases..."""

    def __init__(self, database: str=None) -> None:
        if platform.system().lower == "windows":
            self.__path_sep = "\\"
        else:
            self.__path_sep = "/"
        self.__readonly_db: str = f"data{self.__path_sep}game_content.sqlite"
        if database and not database == "":
            self.__database: str = database
        else:
            self.__database = self.__readonly_db
        self.__connection = sqlite3.connect(self.__database)
        self.__cursor = self.__connection.cursor()

    def get_data(self, table: str, items: list, data_id: str) -> list:
        """Takes the arguments table, items and data_id.
        Returns a list of entrys in the given data table,
        at the given column(data_id)."""
        command: str = "SELECT "
        for i in items:
            command = f"{command}{i}, "
        command = f"{command[:-2]} FROM {table} WHERE id='{data_id.strip(" ")}'"
        data = self.__cursor.execute(command)
        fetched_data: list = data.fetchall()
        return list(fetched_data[0])

    def get_item_data(self, item_id: str) -> list:
        """Calls the get_data method with
        predesigned parameters."""
        return self.get_data(
            "items", ["nutrition", "description", "damage", "crit_damage"], item_id
        )

    def get_chunk_data(self, chunk_id: str) -> list:
        """Calls the get_data method with
        predesigned parameters."""
        return self.get_data(
            "chunks",
            [
                "north_id",
                "east_id",
                "south_id",
                "west_id",
                "description",
                "items",
                "stage",
                "characters",
                "containers",
                "add_commands",
                "rem_commands",
            ],
            chunk_id,
        )

    def get_character_data(self, character_name: str) -> list:
        return self.get_data(
            "player",
            [
                "health",
                "saturation",
                "speed",
                "strength",
                "level",
                "inventory",
                "position",
            ],
            character_name,
        )

    def new_character(self, name: str, inventory:str="''", position="'000-temple-start'", health=42, saturation=42, speed=42, strength=42, level=1):
        name = f"'{name}'"
        self.set_data("player", [name, health, saturation, speed, strength, level, inventory, position])

    def set_data(self, table: str, attributes: list) -> None:
        """Insert new column with given attributes
        into the given table of the self.__database"""
        if self.__database != self.__readonly_db:
            command: str = f"INSERT INTO {table} VALUES ("
            for i in attributes:
                command = f"{command}{i}, "
            command = f"{command[:-2]})"
            self.__cursor.execute(command)
            self.__connection.commit()
        else:
            return "No gameslot is selected, please make a new game, or load a game."

    def update_character(self, attributes: dict, character_name: str) -> None:
        """Update the attributes of the given character."""
        if self.__database != self.__readonly_db:
            for key, attribute in attributes.items():
                if isinstance(attribute, list):
                    command: str = f"UPDATE player SET {key} = "
                    for i in attribute:
                        command = f"{command} {i}, "
                    command = f"{command[:-2]} WHERE id = {character_name}"
                elif key == "":
                    command = None
                else:
                    command: str = (
                        f'UPDATE player SET {key} = "{attribute}" WHERE id = "{character_name}"'
                    )
                if command:
                    self.__cursor.execute(command)
            self.__connection.commit()
        else:
            return "No gameslot is selected, please make a new game, or load a game."

    def update_items(self, items: list, chunk_id: str) -> None:
        "Update the items of a given chunk"
        if self.__database != self.__readonly_db:
            command: str = 'UPDATE chunks SET items = "'
            if items:
                for i in items:
                    command = f"{command}{i}, "
                command = f'{command[:-2]}" WHERE id = "{chunk_id}"'
            else:
                command = f'{command}" WHERE id = "{chunk_id}"'
            self.__cursor.execute(command)
            self.__connection.commit()
        else:
            return "No gameslot is selected, please make a new game, or load a game."

    def set_chunk_data(self, chunk_id: str, attributes: list) -> None:
        pass

    def set_database(self, database: str) -> None:
        """Sets the database to the input."""
        self.__database: str = database
        self.__connection = sqlite3.connect(self.__database)
        self.__cursor = self.__connection.cursor()
        return f"Database was set to {self.__database}"
