"""The main module of the text adventure atlantica.
This module contains all the methods used in the main
game mode of atlantica.
At the moment all methods are in this file, this is
only for developing purposes and will change."""

import random
import shutil  # Used copy the content.sqlite file into a new gameslot
import sqlite3  # Used for all database stuff (see class DatabaseHandler)

from os import remove  # To remove files
from os import listdir  # To list all files of a directory, used in Main.load_game()
from os.path import exists  # Checks if given file exists. Used to prevent errors.
from ast import literal_eval  # Used to evaluate a boolean from a string

from terminal_handler import (
    TerminalHandler,
)  # To display data at the top of the terminal


class Combat:
    """The Combat class contains all
    code, that is used when in combat."""

    def __init__(self):
        self.__combat_commands = {
            "punch": self.punch,
            "kick": self.kick,
            "stab": self.stab,
            "cut": self.cut,
            "flee": self.flee,
        }
        self.__combat_input_handler = InputHandler(self.__combat_commands)
        self.__fighting = True

    def get_combat_commands(self) -> dict:
        """Returns the combat commands."""
        return self.__combat_commands

    def add_combat_commands(self, commands: dict) -> None:
        """Add a command to the combat commands list."""
        for key, value in commands.items():
            self.__combat_commands[key] = value

    def remove_combat_commands(self, commands: list) -> None:
        """Remove a command from the combat commands list."""
        for key in commands:
            self.__combat_commands.pop(key)

    def combat_loop(self, player, opponent):
        """Represents phase3 of the fight,
        starts a new fighting round, if
        none of the opponents died or
        fled this round."""
        while self.__fighting:
            player_begins = self.phase_1(player.get_speed(), opponent.get_speed())
            self.phase_2(player_begins)

    def phase_1(self, player_speed: int, opponent_speed: int) -> bool:
        """Returns true, if the player begins."""
        random_num = random.randint(0, 100)
        # the beginner_value depends on the speed of the player and the opponent,
        # the greater the distance between these two, the higher gets the
        # probability, that the character with the higher speed starts the fight.
        beginner_value = player_speed - opponent_speed + 50
        return random_num <= beginner_value

    def phase_2(self, player_begins):
        """Handles the actual fighting,
        gets the information, which player
        begins and redirects tasks to
        other methods."""
        if player_begins:
            self.player_attack()
            self.npc_attack()
        else:
            self.npc_attack()
            self.player_attack()

    def npc_attack(self):
        """Handles the attacks of
        NPCs."""

    def player_attack(self, player, opponent):
        pass

    def punch(self, player, opponent):
        pass

    def kick(self, player, opponent):
        pass

    def stab(self, player, opponent, wapon):
        pass

    def cut(self, player, opponent, wapon):
        pass

    def flee(self, player, opponent):
        pass


class DatabaseHandler:
    """Handles the sqlite instances,
    reads and writes to sqlite databases..."""

    def __init__(self, database: str) -> None:
        self.__database: str = database
        self.__connection = sqlite3.connect(database)
        self.__cursor = self.__connection.cursor()

    def get_data(self, table: str, items: list, data_id: str) -> list:
        """Takes the arguments table, items and data_id.
        Returns a list of entrys in the given data table,
        at the given column(data_id)."""
        command: str = "SELECT "
        for i in items:
            command = f"{command} {i}, "
        command = f"{command[:-2]} FROM {table} WHERE id='{data_id.strip()}'"
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
        print(chunk_id)
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

    def set_data(self, table: str, attributes: list) -> None:
        """Insert new column with given attributes
        into the given table of the self.__database"""
        if not self.__database == "content.sqlite":
            command: str = f"INSERT INTO {table} VALUES ("
            for i in attributes:
                command = f"{command} {i},"
            command = f"{command[:-2]})"
            self.__cursor.execute(command)
            self.__connection.commit()
        else:
            print("No gameslot is selected, please make a new game, or load a game.")

    def update_character(self, attributes: dict, character_name: str) -> None:
        """Update the attributes of the given character."""
        if not self.__database == "content.sqlite":
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
            print("No gameslot is selected, please make a new game, or load a game.")

    def update_items(self, items: list, chunk_id: str) -> None:
        "Update the items of a given chunk"
        if not self.__database == "content.sqlite":
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
            print("No gameslot is selected, please make a new game, or load a game.")

    def set_chunk_data(self, chunk_id: str, attributes: list) -> None:
        pass

    def set_database(self, database: str) -> None:
        """Sets the database to the input."""
        self.__database: str = database
        self.__connection = sqlite3.connect(self.__database)
        self.__cursor = self.__connection.cursor()
        print(f"Database was set to {self.__database}")


class InputHandler:
    """The InputHandler is in charge
    of taking in put from the user and
    calling the right funcionts associated
    with the input."""

    def __init__(self, commands_avail=None) -> None:
        self.__commands_std = {
            "go": ["main", "move"],
            "rest": ["main", "rest"],
            "take": ["main", "take"],
            "drop": ["main", "drop"],
            "eat": ["main", "eat"],
            "menu": ["main", "menu"],
            "inventory": ["main", "print_inventory"],
            "equip": ["main", "equip"],
            "unequip": ["main", "unequip"],
            "help": ["main", "print_help"],
            "inspect": ["main", "inspect"],
            "quit": ["main", "quit_game"],
            "clear": ["terminal_handler", "clear"],
        }
        if commands_avail is None:
            self.__commands_avail = self.__commands_std
        else:
            self.__commands_avail = commands_avail

    def input_loop(self) -> None:
        """Waits for user input, when user
        input is coming, it executes the
        correlating command. Error checking
        for validity of the command"""
        inputing = True
        while inputing:
            try:
                commands_input = terminal_handler.new_input("> ").lower().split(" ")
                if commands_input == [""]:
                    error_thrown = True
                    continue
                error_thrown: bool = False
                # outputs the number of parameters the inputed method takes:
                if len(commands_input) > 1:
                    for key, func_list in self.__commands_avail.items():
                        if key.startswith(commands_input[0]):
                            if func_list[0] == "main":
                                func = getattr(main, func_list[1])
                            elif func_list[0] == "terminal_handler":
                                func = getattr(terminal_handler, func_list[1])
                            func(commands_input[1:])
                elif len(commands_input) == 1:
                    for key, func_list in self.__commands_avail.items():
                        if key.startswith(commands_input[0]):
                            if func_list[0] == "main":
                                func = getattr(main, func_list[1])
                            elif func_list[0] == "terminal_handler":
                                func = getattr(terminal_handler, func_list[1])
                            func()
                        else:
                            if not error_thrown:
                                terminal_handler.new_print(
                                    "Please enter a valid command, type 'help' for help."
                                )
                                error_thrown = True
            except RuntimeError:
                break

    def get_commands_avail(self) -> dict:
        """Returns the commands, which
        are available at the moment."""
        return self.__commands_avail

    def add_commands(self, commands: dict) -> None:
        """Add a command to the combat commands list."""
        for key, value in commands.items():
            self.__commands_avail[key] = value

    def remove_commands(self, commands: dict, remove_all=False) -> None:
        """Remove a command from the combat commands list."""
        if remove_all:
            self.__commands_avail = {
                "help": ["main", "print_help"],
                "quit": ["main", "quit_game"],
                "clear": ["terminal_handler", "clear"],
            }
        for key in commands:
            self.__commands_avail.pop(key)

    def reset_commands(self) -> None:
        """Reset the commands to standard."""
        self.__commands_avail = self.__commands_std


class Container:
    """A Container is an element in a Chunk,
    which contains Items or triggers Events,
    when inspected."""

    def __init__(
        self, container_id: str, items: list, events: str, description: str
    ) -> None:
        self.__container_id: str = container_id
        self.__items: list = items
        self.__events: list = events
        self.__description: str = description

    def get_items(self) -> list:
        """Returns a list of the
        ids of the items, which
        are in the Container."""
        return self.__items

    def get_events(self) -> list:
        """Returns a list of event
        ids, of the containers' events."""
        return self.__events

    def get_description(self) -> str:
        """Returns the description
        of the container."""
        return self.__description


class Item:
    """An Item is a small objekt,
    that can be found in atlanctica.
    Items are spwning in Chunks, in
    Containers and when enemys die.
    Examples for an Item would be:
    sword, apple, axe, lantern..."""

    def __init__(
        self,
        item_id: str,
        nutrition: int,
        description: str,
        damage: int,
        crit_damage: int,
    ) -> None:
        self.__item_id: str = item_id
        self.__nutrition: int = nutrition
        self.__description: str = description
        self.__damage: int = damage
        self.__crit_damage: int = crit_damage

    def get_nutrition(self) -> int:
        """Returns the nutrition
        of the current Item."""
        return self.__nutrition


class Chunk:
    """A Chunk is the coordinates
    unit. Every Chunk contains some
    stuff e.g items, characters (can be
    good or evil), or Containers.
    Every Chunk has the data about which
    Chunks are next to it so when the player
    walks, the current Chunk has the information
    about what will be the next Chunk."""

    def __init__(
        self,
        chunk_id: str = None,
        north_chunk_id: str = None,
        east_chunk_id: str = None,
        south_chunk_id: str = None,
        west_chunk_id: str = None,
        description: str = None,
        items: str = None,
        characters: str = None,
        stage: str = None,
        containers: list = None,
        add_commands: str = None,
        rem_commands: str = None,
    ) -> None:
        self.__chunk_id: str = chunk_id
        self.__north_chunk_id: str = north_chunk_id
        self.__east_chunk_id: str = east_chunk_id
        self.__south_chunk_id: str = south_chunk_id
        self.__west_chunk_id: str = west_chunk_id
        self.__description: str = description
        self.__stage: str = stage
        if items:
            self.__items: list = items.split(", ")
        else:
            self.__items: list = []
        if characters:
            self.__characters: list = characters.split(", ")
        else:
            self.__characters: list = []
        self.__add_commands = add_commands
        self.__rem_commands = rem_commands

    def get_chunk_id(self) -> str:
        """Returns the id of the current chunk"""
        return self.__chunk_id

    def get_north_chunk_id(self) -> str:
        """Returns the chunk_id of
        the chunk, which lays NORTH of
        the current chunk."""
        return self.__north_chunk_id

    def get_east_chunk_id(self) -> str:
        """Returns the chunk_id of
        the chunk, which lays EAST of
        the current chunk."""
        return self.__east_chunk_id

    def get_south_chunk_id(self) -> str:
        """Returns the chunk_id of
        the chunk, which lays SOUTH of
        the current chunk."""
        return self.__south_chunk_id

    def get_west_chunk_id(self) -> str:
        """Returns the chunk_id of
        the chunk, which lays WEST of
        the current chunk."""
        return self.__west_chunk_id

    def get_description(self) -> str:
        """Returns the descriptio
        of the current chunk."""
        return self.__description

    def get_items(self) -> list:
        """Returns a list of items,
        that the current chunk
        contains at the moment."""
        return self.__items

    def remove_item(self, item: str) -> None:
        """Removes an Item from a Chunk"""
        self.__items.remove(item)

    def add_item(self, item: str) -> None:
        """Add an Item to a Chunk"""
        self.__items.append(item)

    def get_characters(self) -> list:
        """Returns a list of Characters,
        that the current chunk contains."""
        return self.__characters

    def get_add_commands(self) -> dict:
        """Returns the not standard commands,
        which are possible to be executed
        within the current Chunk."""
        return self.__add_commands

    def get_rem_commands(self) -> dict:
        """Returns the standart commands,
        which can not be used within
        the current Chunk"""
        return self.__rem_commands


class Main:
    """This class contains the methods used,
    when in the 'normal' game mode."""

    def __init__(self, game_start: bool) -> None:
        if game_start:
            self.game_start()
        self.__position = Chunk(
            "000-temple-start", *database_handler.get_chunk_data("000-temple-start")
        )
        print(self.__position.get_description())
        self.__inventory: dict = {}
        self.__position_save_id = None
        self.__name = "test"
        character_data: list = database_handler.get_character_data(self.__name)
        self.__health: int = int(character_data[0])
        self.__saturation: int = int(character_data[1])
        self.__speed: int = int(character_data[2])
        self.__strength: int = int(character_data[3])
        self.__level: int = int(character_data[4])

    def get_character_data(self) -> dict:
        """Returns the character data
        as a dict."""
        return {
            "health": self.__health,
            "saturation": self.__saturation,
            "speed": self.__speed,
            "strength": self.__strength,
            "level": self.__level,
        }

    def load_chunk(self, chunk_id: str) -> Chunk:
        """Loads the Chunk with the given id"""
        try:
            chunk_data = database_handler.get_chunk_data(chunk_id)
            print(chunk_data[4])
        except IndexError:
            terminal_handler.new_print("Where you wanted to go, there is just void.")
            return self.__position
        self.save_chunk()  # save the state of the current chunk.
        input_handler.reset_commands()  # reset commands, so previous chunk has no effecet anymore
        chunk = Chunk(chunk_id, *chunk_data)
        if chunk.get_rem_commands():
            if chunk.get_rem_commands() == "remove_all":
                input_handler.remove_commands({}, True)
            else:
                rem_commands_dict = dict(
                    [
                        [i[0], i[1].split(".")]
                        for i in [
                            i.split(": ") for i in chunk.get_rem_commands().split("; ")
                        ]
                    ]
                )
                input_handler.remove_commands(rem_commands_dict)
        if chunk.get_add_commands():
            add_commands_dict = dict(
                [
                    [i[0], i[1].split(".")]
                    for i in [
                        i.split(": ") for i in chunk.get_add_commands().split("; ")
                    ]
                ]
            )
            input_handler.add_commands(add_commands_dict)
        return chunk

    def print_help(self, args=None) -> None:
        """Outprints all available commands."""
        terminal_handler.new_print("\nAvailable commands:\n")
        for key in input_handler.get_commands_avail():
            terminal_handler.new_print(key)

    def quit_game(self, args=None) -> None:
        """Saves and quits the game."""
        self.save_game()
        exit("Good bye, see you next time in Atlantica!")

    def new_game(self, args=None) -> None:
        """Creates a new game save slot"""
        game_name = terminal_handler.new_input(
            "Please input the name of the gameslot\n> "
        )
        game_file_path = f"saves/gameslot_{game_name}.sqlite"
        if exists(game_file_path):
            overwrite = terminal_handler.new_input(
                "This gameslot is already occupied, do you want to overwrite? [y/N]\n> "
            ).lower()
            if not overwrite == "y" or overwrite == "yes":
                return None
        shutil.copyfile("content.sqlite", game_file_path)
        terminal_handler.new_print(
            f"The gameslot: {game_name} was sucessfully created."
        )
        database_handler.set_database(game_file_path)
        self.quit_menu()
        return None

    def load_game(self, args=None) -> None:
        """Loads the gamestate from
        a given slot."""
        saved_game_files = listdir("saves/")
        if saved_game_files:
            terminal_handler.new_print("Pick your option:")
            for index, file_name in enumerate(saved_game_files):
                terminal_handler.new_print(
                    f"Option {index +1} is {file_name[9:-7]}"
                )  # prints the name of the gamestate, without printing the whole file name
            try:
                option = int(
                    terminal_handler.new_input("Input the number of your option.\n> ")
                )
            except ValueError:
                terminal_handler.new_print(
                    "You have to put in the NUMBER of your gameslot."
                )
                return None
            try:
                database_handler.set_database(f"saves/{saved_game_files[option-1]}")
            except IndexError:
                terminal_handler.new_print("This option is not available.")
                return None
            character_data = database_handler.get_character_data(self.__name)
            self.__health: int = int(character_data[0])
            self.__saturation: int = int(character_data[1])
            self.__speed: int = int(character_data[2])
            self.__strength: int = int(character_data[3])
            self.__level: int = int(character_data[4])
            self.__position_save_id = character_data[6]
            inventory_data_raw: str = character_data[5]
            if inventory_data_raw:
                inventory_list: list = [
                    i.split(":") for i in inventory_data_raw.split(", ")
                ]
            else:
                inventory_list: list = []
            if len(inventory_list) > 1:
                self.__inventory = dict(inventory_list)
            else:
                self.__inventory = {}
            for i in self.__inventory:
                self.__inventory[i] = literal_eval(self.__inventory[i])
            self.quit_menu()
        else:
            terminal_handler.new_print(
                "There are no gameslots available, create one with 'new'."
            )
        return None

    def save_game(self, arguments=None):
        """Saves the game state to
        the current gameslot."""
        self.save_chunk()
        self.save_player()

    def delete_game(self, args=None) -> None:
        """Delete the given Gameslot."""
        saved_game_files = listdir("saves/")
        if saved_game_files:
            terminal_handler.new_print("Pick your option:")
            for index, file_name in enumerate(saved_game_files):
                terminal_handler.new_print(
                    f"Option {index +1} is {file_name[9:-7]}"
                )  # prints the name of the gamestate, without printing the whole file name
            option: str = terminal_handler.new_input(
                "Input the number of your option.\n> "
            )
            try:
                option: int = int(option)
                gameslot: str = f"{saved_game_files[option-1]}"
            except ValueError:
                gameslot = f"gameslot_{option}.sqlite"
                if not gameslot in saved_game_files:
                    terminal_handler.new_print(
                        f"Der Gameslot {gameslot[9:-7]} exisiert nicht."
                    )
                    return None
            consent = terminal_handler.new_input(
                f"Bist du dir sicher, dass du Gameslot {gameslot[9:-7]} löschen möchtest? [y/N]\n> "
            ).lower()
            if consent == "y":
                remove(f"saves/{gameslot}")
                terminal_handler.new_print(f"Gameslot {gameslot[9:-7]} wurde gelöscht.")
            else:
                terminal_handler.new_print("Nichts wurde gelöscht.")

        else:
            terminal_handler.new_print("There are no gameslots.")

    def save_player(self):
        """Saves the player data to
        the current gameslot."""
        inventory: str = ""
        for key, item in self.__inventory.items():
            inventory = f"{inventory}{key}:{item}, "
        inventory = inventory[:-2]
        database_handler.update_character(
            {
                "health": str(self.__health),
                "saturation": str(self.__saturation),
                "speed": str(self.__speed),
                "strength": str(self.__strength),
                "level": str(self.__level),
                "inventory": inventory,
                "position": self.__position.get_chunk_id(),
            },
            self.__name,
        )

    def save_chunk(self) -> None:
        """Saves the current chunk data
        to the current game slot."""
        chunk_id = self.__position.get_chunk_id()
        items = self.__position.get_items()
        database_handler.update_items(items, chunk_id)

    def menu(self, args=None) -> None:
        """Opens the menu, by setting the
        current position to the menu Chunk."""
        self.__position_save_id = self.__position.get_chunk_id()
        self.__position = self.load_chunk("menu")

    def quit_menu(self) -> None:
        """Restores the Chunk, where the
        player was located, before opening
        the menu."""
        terminal_handler.clear()
        self.__position = self.load_chunk(self.__position_save_id)

    def move(self, direction: list = None) -> None:
        """Move the character
        in a given direction."""
        if not direction is None:
            try:
                if len(direction) == 1:
                    direction.append(1)
                else:
                    direction[1] = int(direction[1])
                for i in range(direction[1]):
                    if direction[0] == "north" or direction[0] == "n":
                        self.__position = self.load_chunk(
                            self.__position.get_north_chunk_id()
                        )
                    elif direction[0] == "east" or direction[0] == "e":
                        self.__position = self.load_chunk(
                            self.__position.get_east_chunk_id()
                        )
                    elif direction[0] == "south" or direction[0] == "s":
                        self.__position = self.load_chunk(
                            self.__position.get_south_chunk_id()
                        )
                    elif direction[0] == "west" or direction[0] == "w":
                        self.__position = self.load_chunk(
                            self.__position.get_west_chunk_id()
                        )
                    else:
                        terminal_handler.new_print(
                            "You did not walk, the direction you want to go does not exist."
                        )
            except ValueError:
                terminal_handler.new_print(
                    "\nFirstly, write the direction, you want to go,"
                )
                terminal_handler.new_print(
                    "and secondly, write the number of steps you want to take."
                )
        else:
            terminal_handler.new_print(
                "You did not walk, because you don't know which direction."
            )

    def rest(self, args=None) -> None:
        """Rest, no other actions
        take place. The Player
        gets healed."""
        print("You had a nice rest!")

    def take(self, item: list = None) -> None:
        """Take a given Item from
        the current chunk."""
        if not item is None:
            for i in item:
                found = False
                item_selected = self.item_in_position(i)
                if item_selected:
                    self.__inventory[item_selected] = (
                        False  # Setting equipped parameter to False
                    )
                    self.__position.remove_item(item_selected)
                    terminal_handler.new_print(f"You took {item_selected[5:]}.")
                    found = True

                if not found:
                    terminal_handler.new_print(
                        f"There is no {i} at your current location."
                    )

    def item_in_inventory(self, item: str) -> str:
        """Checks, if the given item, or start
        of items name is in the inventory.
        Returns either the item or False."""
        for item_avail in self.__inventory:
            if item_avail[5:].startswith(item) and not item == "":
                return item_avail
        return False

    def item_in_position(self, item: str) -> str:
        """Checks, if the given item, or start
        of items name is in the current Chunk.
        Returns either the item or False."""
        for item_avail in self.__position.get_items():
            if item_avail[5:].startswith(item) and not item == "":
                return item_avail
        return False

    def drop(self, items: list = None) -> None:
        """Drop a given Item from the
        Inventory to the current chunk."""
        if items is None:
            terminal_handler.new_print("You dropped ... nothing.")
        else:
            for i in items:
                dropped = False
                item_selected = self.item_in_inventory(i)
                if item_selected:
                    self.__inventory.pop(item_selected)
                    self.__position.add_item(item_selected)
                    terminal_handler.new_print(f"You dropped {item_selected[5:]}.")
                    dropped = True
                if not dropped:
                    if not i == "":
                        terminal_handler.new_print(
                            f"You tried to drop {i}, but it was not even in your inventory!"
                        )
                    else:
                        terminal_handler.new_print("You dropped ... nothing.")

    def print_inventory(self, args=None) -> None:
        """ "Outprints the Inventory, mark
        which item is equiped."""
        if self.__inventory:
            terminal_handler.new_print("Your inventory contains:")
            for key, value in self.__inventory.items():
                if value:  # check, if item is eqiupped
                    terminal_handler.new_print(f"{key[5:]} - equipped")
                else:
                    terminal_handler.new_print(key[5:])
        else:
            terminal_handler.new_print("Your inventory is empty.")

    def unequip(self, item: list = None, first_iter: bool = True) -> None:
        """Unequip the Item, which
        is currently equipped."""
        if item is None or not first_iter:
            for inventory_item, equipped in self.__inventory.items():
                if equipped:
                    self.__inventory[inventory_item] = (
                        False  # set the equipped parameter to false
                    )
                    terminal_handler.new_print(f"You unequipped {inventory_item}.")
        else:
            found = False
            for inventory_item, equipped in self.__inventory.items():
                if inventory_item.startswith(item[0]):
                    found = True
                    self.unequip(None, False)
            if not found:
                terminal_handler.new_print(f"{item[0]} was no equipped.")

    def equip(self, item: list = None) -> None:
        """Equip a given Item, that either
        is in the Inventory, or in the
        curren chunk."""
        item_selected_inv = self.item_in_inventory(item[0])
        item_selected_pos = self.item_in_position(item[0])
        if item_selected_inv:
            item_selected = item_selected_inv
        elif item_selected_pos:
            self.__position.remove_item(item_selected_pos)
            item_selected = item_selected_pos
        else:
            terminal_handler.new_print(
                f"There is no {item[0]}, you could equip right now."
            )
            return None
        self.unequip()
        self.__inventory[item_selected] = True  # set the eqiupped parameter to true
        terminal_handler.new_print(f"You equipped {item_selected[5:]}.")
        if item[0] == "":
            terminal_handler.new_print("You wanted to equip. But what?")

    def eat(self, item: list = None):
        """Removes the eaten item
        from the inventory and adds
        the saturation to the hunger
        value of the Player."""
        if item:
            for i in item:
                item_selected = self.item_in_inventory(i)
                if item_selected:
                    nutrition = int(database_handler.get_item_data(item_selected)[0])
                    terminal_handler.new_print(nutrition)
                    print(type(self.__saturation))
                    self.__saturation = int(self.__saturation) + nutrition
                    self.__inventory.pop(item_selected)
                    terminal_handler.new_print(
                        f"You ate {item_selected[5:]}, it was {nutrition} nutritious."
                    )
                    terminal_handler.set_information_left(
                        "saturation", self.__saturation
                    )
                else:
                    terminal_handler.new_print(
                        f"You tried to eat {i}, but you had none left"
                    )
        else:
            terminal_handler.new_print("You did not eat.")

    def inspect(self):
        """Outprints the items,
        which are in the current Chunk."""
        terminal_handler.new_print(f"There are: {self.__position.get_items()}")

    def game_start(self) -> None:
        """The Text, which gets
        displayed at the start
        of the game."""
        print(
            """
        ---------------------------
        Welcome back in Atlantica.
        Enjoy your time around here.
        ----------------------------
        """
        )


database_handler = DatabaseHandler("content.sqlite")
main = Main(True)
terminal_handler = TerminalHandler(main.get_character_data(), {}, {})
combat = Combat()
input_handler = InputHandler()
main.menu()
while True:
    input_handler.input_loop()
