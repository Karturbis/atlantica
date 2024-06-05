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
        pass

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

    def __init__(self, database):
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
        command = f"{command} FROM {table} WHERE id='{data_id}'"
        print(command)
        data = self.__cursor.execute(command)
        return data.fetchall()

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
            "stage", "items", "characters"
            ], chunk_id
            )


class InputHandler:
    """The InputHandler is in charge
    of taking in put from the user and
    calling the right funcionts associated
    with the input."""
    def __init__(self, commands_avail=None):
        self.__commands_std = {
            "newgame": main.new_game,
            "loadgame": main.load_game,
            "savegame": main.save_game,
            "go":main.move,
            "rest": main.rest,
            "take": main.take,
            "drop": main.drop,
            "inventory": main.print_inventory,
            "equip": main.equip,
            "unequip": main.unequip,
            "help": self.print_help,
            "quit": main.quit_game
            }
        if commands_avail is None:
            self.__commands_avail = self.__commands_std
        else:
            self.__commands_avail = commands_avail

    def input_loop(self):
        """Waits for user input, when user
        input is coming, it executes the
        correlating command. Error checking
        for validity of the command"""
        inputing = True
        while inputing:
            commands_input = input("> ").lower().split(" ")
            error_thrown: bool = False
            if len(commands_input) > 1:  # outputs the number of parameters the inputed method takes
                for key, func in self.__commands_avail.items():
                    if key.startswith(commands_input[0]):
                        func(commands_input[1:])
                    else:
                        if not error_thrown:
                            print("Please enter a valid command, type 'help' for help.")
                            error_thrown = True
            if len(commands_input) == 1:
                for key, func in self.__commands_avail.items():
                    if key.startswith(commands_input[0]):
                        func()
                    else:
                        if not error_thrown:
                            print("Please enter a valid command, type 'help' for help.")
                            error_thrown = True

    def print_help(self, args = None):
        """Outprints all available commands."""
        print("\nAvailable commands:\n")
        for key in self.__commands_avail.keys():
            print(key)

    def add_commands(self, commands: dict) -> None:
        """Add a command to the combat commands list."""
        for key, value in commands.items():
            self.__commands_avail[key] = value

    def remove_commands(self, commands: dict) -> None:
        """Remove a command from the combat commands list."""
        for key in commands:
            self.__commands_avail.pop(key)

    def reset_commands(self) -> None:
        self.__commands_avail = self.__commands_std


class Container:
    """A Container is an element in a Chunk,
    which contains Items or triggers Events,
    when inspected."""

    def __init__(
        self, container_id: str, items: list,
        events: str, description: str
        ):
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
        ):
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
        west_chunk_id: str = None, description: str = None, stage: str = None,
        items: list = None, characters: list = None, add_commands: dict = None,
        rem_commands: dict = None
        ):
        self.__chunk_id: str = chunk_id
        self.__north_chunk_id: str = north_chunk_id
        self.__east_chunk_id: str = east_chunk_id
        self.__south_chunk_id: str = south_chunk_id
        self.__west_chunk_id: str = west_chunk_id
        self.__description: str = description
        self.__stage: str = stage
        self.__items: list = items
        self.__characters: list = characters
        self.__add_commands = add_commands
        self.__rem_commands = rem_commands

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

    def get_characters(self) -> list:
        """Returns a list of Characters,
        that the current chunk contains."""
        return self.__characters

    def get_add_commands(self) -> dict:
        return self.__add_commands

    def get_rem_commands(self) -> dict:
        return self.__rem_commands


class Main:
    """This class contains the methods used,
    when in the 'normal' game mode."""

    def __init__(self):
        start = Chunk("0", "1", "2", "3", "4", "You are at the start of the Game", "start")
        self.position: Chunk = start
        self.inventory: dict = {}
        self.in_hand: str = ""

    def load_chunk(self, chunk_id):
        input_handler.reset_commands()  # reset commands, so previous chunk has no effecet anymore
        chunk_data = database_handler.get_chunk_data(chunk_id)
        chunk = Chunk(chunk_id, *chunk_data)
        input_handler.remove_commands(chunk.get_rem_commands())
        input_handler.add_commands(chunk.get_add_commands())
        return chunk

    def quit_game(self, args = None):
        """Saves and quits the game."""
        self.save_game()
        exit("Good bye, see you next time in Atlantica!")

    def new_game(self, args = None):
        """Creates a new game save slot"""
        print("NEWGAME")

    def load_game(self, args = None):
        """Loads the gamestate from
        a given slot."""
        pass

    def save_game(self, args = None):
        """Saves the current gamestate"""
        pass

    def move(self, direction: list = None):
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
                        self.position = self.load_chunk(self.position.get_north_chunk_id())
                        print("You went North")
                    elif direction[0] == "east" or direction[0] == "e":
                        self.position = self.load_chunk(self.position.get_east_chunk_id())
                    elif direction[0] == "south" or direction[0] == "s":
                        self.position = self.load_chunk(self.position.get_south_chunk_id())
                    elif direction[0] == "west" or direction[0] == "w":
                        self.position = self.load_chunk(self.position.get_west_chunk_id())
                    else:
                        print("You did not walk, the direction you want to go does not exist.")
            except ValueError:
                print("\nFirstly, write the direction, you want to go,")
                print("and secondly, write the number of steps you want to take.")
        else:
            print("You did not walk, because you don't know which direction.")

    def rest(self, args = None):
        """Rest, no other actions
        take place. The Player
        gets healed."""
        print("You had a nice rest!")

    def take(self, item: list = None):
        """Take a given Item from
        the current chunk."""
        if not item is None:
            for i in item:
                self.inventory[i] = False  # The Flase stands for the equipped parameter
                print(f"You took {i}.")
            # ADD CHECK, IF ITEM IS IN CURRENT CHUNK!!!

    def drop(self, item: list = None):
        """Drop a given Item from the
        Inventory to the current chunk."""
        if item is None:
            print("You dropped ... nothing.")
        else:
            for i in item:
                try:
                    self.inventory.pop(i)
                    print(f"You dropped {i}.")
                except KeyError:
                    print(f"You tried to drop {i}, but it was not even in your inventory!")

    def print_inventory(self, args = None):
        """"Outprints the Inventory, mark
        which item is equiped."""
        if self.inventory:
            print("Your inventory contains:")
            for key, value in self.inventory.items():
                if value:  # check, if item is eqiupped
                    print(f"{key} - equipped")
                else:
                    print(key)
        else:
            print("Your inventory is empty.")

    def unequip(self, item: list = None):
        """Unequip the Item, which
        is currently equipped."""
        if item is None:
            for inventory_item, equipped in self.inventory.items():
                if equipped:
                    self.inventory[inventory_item] = False  # set the equipped parameter to false
                    print(f"You unequipped {inventory_item}.")
        else:
            if self.inventory[item[0]]:
                self.unequip()
            else:
                print(f"{item[0]} was no equipped.")

    def equip(self, item: list = None):
        """Equip a given Item, that either
        is in the Inventory, or in the 
        curren chunk."""
        # ADD CHECK; IF ITEM EXISTS IN CHUNK, OR INVENTORY!!!!!
        if not item is None:
            self.unequip()
            self.inventory[item[0]] = True  # set the eqiupped parameter to true
            print(f"You equipped {item[0]}.")
        else:
            print("You wanted to equip. But what?")

    def game_start(self):
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



main = Main()
combat = Combat()
input_handler = InputHandler()
database_handler = DatabaseHandler("./rewrite/content.sqlite")
main.game_start()
input_handler.input_loop()
