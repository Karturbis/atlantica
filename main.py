"""The main module of the text adventure atlantica.
This module contains all the methods used in the main
game mode of atlantica.
At the moment all methods are in this file, this is
only for developing purposes and will change."""

import random
import sqlite3

class Combat:
    """The Combat class contains all
    code, that is used when in combat."""
    def __init__(self):
        self.__combat_commands = {
            "punch": self.punch,
            "kick": self.kick,
            "stab": self.stab,
            "cut": self.cut,
            "flee": self.flee
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

    def phase_1(self, player_speed:int, opponent_speed:int) -> bool:
        """Returns true, if the player begins."""
        random_num = random.randint(0, 100)
        # the beginner_value depends on the speed of the player and the opponent,
        # the greater the distance between these two, the higher gets the
        # probability, that the character with the higher speed starts the fight.
        beginner_value = player_speed-opponent_speed+50
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

    def __init__(self, database) -> None:
        self.__connection = sqlite3.connect(database)
        self.__cursor = self.__connection.cursor()

    def get_data(self, table: str, items: list, data_id: str) -> list:
        """Takes the arguments table, items and data_id.
        Returns a list of entrys in the given data table,
        at the given column(data_id)."""
        command: str =  "SELECT "
        for i in items:
            if not i == items[-1]:
                command = f"{command} {i}, "
            else:
                command = f"{command} {i}"
        command = f"{command} FROM {table} WHERE id='{data_id.strip()}'"
        data = self.__cursor.execute(command)
        fetched_data: list = data.fetchall()
        return list(fetched_data[0])

    def get_item_data(self, item_id: str) -> list:
        """Calls the get_data method with
        predesigned parameters."""
        return self.get_data("items", ["wapon", "description"], item_id)

    def get_chunk_data(self, chunk_id: str) -> list:
        """Calls the get_data method with
        predesigned parameters."""
        return self.get_data(
            "chunks", ["north_id", "east_id",
            "south_id", "west_id", "description",
            "items", "stage", "characters",
            "containers", "add_commands",
            "rem_commands"
            ], chunk_id
            )


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
            "menu": ["main", "menu"],
            "inventory": ["main", "print_inventory"],
            "equip": ["main", "equip"],
            "unequip": ["main", "unequip"],
            "help": ["main", "print_help"],
            "quit": ["main", "quit_game"]
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
                commands_input = input("> ").lower().split(" ")
                if commands_input == ['']:
                    print("FIRSDT")
                    error_thrown = True
                    continue
                error_thrown: bool = False
                # outputs the number of parameters the inputed method takes:
                if len(commands_input) > 1:
                    for key, func_list in self.__commands_avail.items():
                        if key.startswith(commands_input[0]):
                            if func_list[0] == "main":
                                func = getattr(main, func_list[1])
                            elif func_list[0] == "combat":
                                func = getattr(combat, func_list[1])
                            func(commands_input[1:])
                elif len(commands_input) == 1:
                    for key, func_list in self.__commands_avail.items():
                        if key.startswith(commands_input[0]):
                            if func_list[0] == "main":
                                func = getattr(main, func_list[1])
                            elif func_list[0] == "combat":
                                func = getattr(combat, func_list[1])
                            func()
                        else:
                            if not error_thrown:
                                print("Please enter a valid command, type 'help' for help.")
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

    def remove_commands(self, commands: dict, remove_all = False) -> None:
        """Remove a command from the combat commands list."""
        if remove_all:
            self.__commands_avail = {
                "help": ["main", "print_help"],
                "quit": ["main", "quit_game"]
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
        self, container_id: str, items: list,
        events: str, description: str
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
        self, item_id: str, wapon:bool,
        description: str, saturation: int
        ) -> None:
        self.__item_id = item_id
        self.__wapon = wapon
        self.__description = description
        self.__saturation = saturation


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
        self, chunk_id: str = None, north_chunk_id: str = None,
        east_chunk_id: str = None, south_chunk_id: str = None,
        west_chunk_id: str = None, description: str = None,
        items: str = None, characters: str = None, stage: str = None,
        containers: list = None, add_commands: str = None, rem_commands: str = None
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
        if characters:
            self.__characters: list = characters.split(", ")
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
            "000-temple-start",
            *database_handler.get_chunk_data("000-temple-start")
            )
        print(self.__position.get_description())
        self.__inventory: dict = {}
        self.__position_save_id = None

    def load_chunk(self, chunk_id: str) -> Chunk:
        """Loads the Chunk with the given id"""
        try:
            chunk_data = database_handler.get_chunk_data(chunk_id)
            print(chunk_data[4])
        except IndexError:
            print("Where you wanted to go, there is just void.")
            return self.__position
        input_handler.reset_commands()  # reset commands, so previous chunk has no effecet anymore
        chunk = Chunk(chunk_id, *chunk_data)
        if chunk.get_rem_commands():
            if chunk.get_rem_commands() == "remove_all":
                input_handler.remove_commands({}, True)
            else:
                rem_commands_dict = dict(
                    [[i[0], i[1].split(".")] for i in
                        [i.split(": ") for i in
                            chunk.get_rem_commands().split("; ")
                        ]
                    ]
                    )
                input_handler.remove_commands(rem_commands_dict)
        if chunk.get_add_commands():
            add_commands_dict = dict(
                [[i[0], i[1].split(".")] for i in
                    [i.split(": ") for i in
                        chunk.get_add_commands().split("; ")]]
                )
            input_handler.add_commands(add_commands_dict)
        return chunk

    def print_help(self, args = None) -> None:
        """Outprints all available commands."""
        print("\nAvailable commands:\n")
        for key in input_handler.get_commands_avail():
            print(key)

    def quit_game(self, args = None) -> None:
        """Saves and quits the game."""
        self.save_game()
        exit("Good bye, see you next time in Atlantica!")

    def new_game(self, args = None) -> None:
        """Creates a new game save slot"""
        print("NEWGAME")

    def load_game(self, args = None) -> None:
        """Loads the gamestate from
        a given slot."""

    def save_game(self, args = None) -> None:
        """Saves the current gamestate"""

    def menu(self) -> None:
        """Opens the menu, by setting the
        current position to the menu Chunk."""
        self.__position_save_id = self.__position.get_chunk_id()
        self.__position = self.load_chunk("menu")

    def quit_menu(self) -> None:
        """Restores the Chunk, where the
        player was located, before opening
        the menu."""
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
                        self.__position = self.load_chunk(self.__position.get_north_chunk_id())
                    elif direction[0] == "east" or direction[0] == "e":
                        self.__position = self.load_chunk(self.__position.get_east_chunk_id())
                    elif direction[0] == "south" or direction[0] == "s":
                        self.__position = self.load_chunk(self.__position.get_south_chunk_id())
                    elif direction[0] == "west" or direction[0] == "w":
                        self.__position = self.load_chunk(self.__position.get_west_chunk_id())
                    else:
                        print("You did not walk, the direction you want to go does not exist.")
            except ValueError:
                print("\nFirstly, write the direction, you want to go,")
                print("and secondly, write the number of steps you want to take.")
        else:
            print("You did not walk, because you don't know which direction.")

    def rest(self, args = None) -> None:
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
                for item_avail in self.__position.get_items():
                    if item_avail.startswith(i):
                        self.__inventory[item_avail] = False  # Setting equipped parameter to False
                        self.__position.remove_item(item_avail)
                        print(f"You took {item_avail}.")
                        found = True
                        break
                if not found:
                    print(f"There is no {i} at your current location.")

    def drop(self, item: list = None) -> None:
        """Drop a given Item from the
        Inventory to the current chunk."""
        if item is None:
            print("You dropped ... nothing.")
        else:
            for i in item:
                dropped = False
                for item_avail in self.__inventory:
                    if item_avail.startswith(i):
                        self.__inventory.pop(item_avail)
                        self.__position.add_item(item_avail)
                        print(f"You dropped {item_avail}.")
                        dropped = True
                        break
                if not dropped:
                    print(f"You tried to drop {i}, but it was not even in your inventory!")

    def print_inventory(self, args = None) -> None:
        """"Outprints the Inventory, mark
        which item is equiped."""
        if self.__inventory:
            print("Your inventory contains:")
            for key, value in self.__inventory.items():
                if value:  # check, if item is eqiupped
                    print(f"{key} - equipped")
                else:
                    print(key)
        else:
            print("Your inventory is empty.")

    def unequip(self, item: list = None, first_iter: bool = True) -> None:
        """Unequip the Item, which
        is currently equipped."""
        if item is None or not first_iter:
            for inventory_item, equipped in self.__inventory.items():
                if equipped:
                    self.__inventory[inventory_item] = False  # set the equipped parameter to false
                    print(f"You unequipped {inventory_item}.")
        else:
            found = False
            for inventory_item, equipped in self.__inventory.items():
                if inventory_item.startswith(item[0]):
                    found = True
                    self.unequip(None, False)
            if not found:
                print(f"{item[0]} was no equipped.")

    def equip(self, item: list = None) -> None:
        """Equip a given Item, that either
        is in the Inventory, or in the 
        curren chunk."""
        items_avail: list = self.__position.get_items() + list(self.__inventory.keys())
        if not item is None:
            found = False
            for i in items_avail:
                if i.startswith(item[0]):
                    self.unequip()
                    self.__inventory[i] = True  # set the eqiupped parameter to true
                    if i in self.__position.get_items():
                        self.__position.remove_item(i)
                    print(f"You equipped {i}.")
                    found = True
                    break
            if not found:
                print(f"There is no {item[0]}, you could equip right now.")
        else:
            print("You wanted to equip. But what?")

    def inspect(self):
        pass

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
""")


database_handler = DatabaseHandler("content.sqlite")
main = Main(True)
combat = Combat()
input_handler = InputHandler()
while True:
    input_handler.input_loop()
