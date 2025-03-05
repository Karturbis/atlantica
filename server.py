import time
import sys
from ast import literal_eval  # Used to evaluate a boolean from a string
import random
from handler import network_handler
from handler import DatabaseHandler
#from data_classes import Container
#from data_classes import Item
from data_classes import Chunk


class ServerMethods():

    def __init__(self, connection, connection_id, thread_data):
        self.__connection = connection
        self.__connection_id = connection_id
        self.__thread_data = thread_data
        self.__standart_server_methods = [
            "ping", "move", "rest",
            "take", "drop", "print_inventory",
            "unequip", "eat", "inspect", "equip",
            "save_player", "backflip",
            "disconnect", "start_fight"
            ]
        self.__server_help_data = {
            "ping": "prints the time of the ping in nano seconds",
            "move": "move in the given direction",
            "rest": "take a rest",
            "take": "take an item from your surroundings",
            "drop": "drop an item from inventory",
            "print_inventory": "display the inventory",
            "equip": "equip an item",
            "unequip": "unequip an item",
            "eat": "eat an item",
            "inspect": "scheck your surroundings for items",
            "save_player": "save the game",
            "disconnect": "disconnect from server",
        }
        self.__server_methods_minimum = ["ping"]
        self.__server_methods = self.__standart_server_methods
        self.__inventory = {}
        self.__position_save_id = {}
        self.__health = {}
        self.__saturation = {}
        self.__speed = {}
        self.__strength = {}
        self.__level = {}
        self.__position = None
        self.__name = None
        self.db_handler = None
        self.__backflip_counter = 0

    def init_character_data(self, game_file_path):
        self.send_cmd_packet("add_server_help_entries", [self.__server_help_data])
        self.__name = thread_data.client_names[self.__connection_id]
        self.db_handler = DatabaseHandler(game_file_path[0])
        try:
            self.db_handler.get_player_data(self.__name)
        except IndexError:  # no character data for this name was found
            self.db_handler.new_player(self.__name)
        character_data = self.db_handler.get_player_data(self.__name)
        self.__health: int = int(character_data[0])
        self.__saturation: int = int(character_data[1])
        self.__speed: int = int(character_data[2])
        self.__strength: int = int(character_data[3])
        self.__level: int = int(character_data[4])
        self.__position_save_id = character_data[6]
        self.__position = Chunk(
            self.__position_save_id, *self.db_handler.get_chunk_data(self.__position_save_id)
        )
        # load inventory from database:
        inventory_data_raw: str = character_data[5]
        if inventory_data_raw:
            inventory_list: list = [
                i.split(":") for i in inventory_data_raw.split(", ")
            ]
        else:
            inventory_list: list = []
        if len(inventory_list) >= 1:
            self.__inventory = dict(inventory_list)
        else:
            self.__inventory = {}
        for i in self.__inventory:
            self.__inventory[i] = literal_eval(self.__inventory[i])
        self.db_handler.update_characters(
            self.__position.get_chunk_id(),
            self.__name,
            remove=False
        )

    def send_cmd_packet(self, command: str, args:list = None) -> None:
        network_server.send_packet(network_handler.NetworkPacket(
            packet_type="command",
            command_name=command,
            command_attributes=args,
            ),
            self.__connection_id
        )

    def new_print(self, data):
        if data:
            network_server.send_print_packet(data, self.__connection_id)

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

    def get_server_methods(self):
        return self.__server_methods

    def execute_cmd(self, command, args=None):
        if not args:
            args = []
        print(f"args: {args}")
        try:
            func = getattr(self, command)
        except AttributeError:
            self.new_print(f"There is no command called {command}")
        given_args_len = len(args)
        # get number of keyword args:
        if func.__defaults__:
            kwargs = len(func.__defaults__)
        else:
            kwargs = 0
        # subtract kwargs from all args to get positional args
        expected_args_len = func.__code__.co_argcount - kwargs -1  # -1 otherwise self counts as an arg
        if given_args_len >= 1:
            if expected_args_len == given_args_len or expected_args_len + kwargs >= given_args_len:
                # run method:
                try:
                    return func(args)
                except Exception as e:
                    self.new_print(f"ERROR in (1) ServerMethods.excute_cmd: {e}")
            else: # wrong number of arguments were given
                self.new_print(f"Command {command} takes {expected_args_len} arguments, you gave {given_args_len}.")
        else:  # no args where given:
            if expected_args_len == given_args_len:
                # run method:
                try:
                    return func()
                except Exception as e:
                    self.new_print(f"ERROR in (2) ServerMethods.excute_cmd: {e}")
            else: # wrong number of arguments were given
                self.new_print(f"Command {command} takes {expected_args_len} arguments, you gave {given_args_len}.")

    def reset_commands(self):
        self.__server_methods = self.__standart_server_methods

    def remove_commands(self, commands: list=None, remove_all=False) -> None:
        """Remove a command from the combat commands list."""
        if remove_all:
            self.__server_methods = self.__server_methods_minimum
        else:
            self.__server_methods = [i for i in self.__server_methods if not i in commands]

    def add_commands(self, commands: dict):
        for key, _ in commands.items():
            self.__server_methods.add(key)

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

    def save_player(self):
        """Saves the player data to
        the current gameslot."""
        self.__position_save_id = self.__position.get_chunk_id()
        inventory: str = ""
        for key, item in self.__inventory.items():
            inventory = f"{inventory}{key}:{item}, "
        inventory = inventory[:-2]
        self.db_handler.update_player(
            {
                "health": str(self.__health),
                "saturation": str(self.__saturation),
                "speed": str(self.__speed),
                "strength": str(self.__strength),
                "level": str(self.__level),
                "inventory": inventory,
                "position": self.__position_save_id,
            },
            self.__name,
        )

    def save_chunk(self, position=None) -> None:
        """Saves the current chunk data
        to the current game slot."""
        if not position:
            chunk_id = self.__position.get_chunk_id()
            items = self.__position.get_items()
        else:
            chunk_id = position.get_chunk_id()
            items = position.get_items()
        self.db_handler.update_items(items, chunk_id)

    def load_chunk(self, chunk_id: str) -> Chunk:
        """Loads the Chunk with the given id"""
        try:
            chunk_data = self.db_handler.get_chunk_data(chunk_id)
        except IndexError:
            self.new_print("Where you wanted to go, there is just void.")
            return self.__position
        self.save_chunk()  # save the state of the current chunk.
        self.reset_commands()  # reset commands, so previous chunk has no effecet anymore
        chunk = Chunk(chunk_id, *chunk_data)
        if chunk.get_rem_commands():
            if chunk.get_rem_commands() == "remove_all":
                self.remove_commands({}, True)
            else:
                rem_commands_dict = dict(
                    [
                        [i[0], i[1].split(".")]
                        for i in [
                            i.split(": ") for i in chunk.get_rem_commands().split("; ")
                        ]
                    ]
                )
                self.remove_commands(rem_commands_dict)
        if chunk.get_add_commands():
            add_commands_dict = dict(
                [
                    [i[0], i[1].split(".")]
                    for i in [
                        i.split(": ") for i in chunk.get_add_commands().split("; ")
                    ]
                ]
            )
            self.add_commands(add_commands_dict)
        return chunk

################################
## Player executable methods: ##
################################

    def shutdown(self):
        self.save_player()
        self.save_chunk()
        exit("Shutting down...")

    def move(self, direction: list=None, steps: str="1") -> None:
        """Move the character
        in a given direction."""
        if not direction is None:
            try:
                steps = int(direction[1])
            except IndexError:
                steps = 1
            try:
                for _ in range(steps):
                    try:
                        # remove character from current position:
                        self.db_handler.update_characters(
                        self.__position.get_chunk_id(),
                        self.__name, remove=True
                        )
                    except Exception as e:
                        print(f"ERROR in removeing character from chunk: {e}")
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
                        self.new_print(
                            "You did not walk, the direction you want to go does not exist.")
                try:
                    # add character to new position:
                    self.db_handler.update_characters(
                        self.__position.get_chunk_id(),
                        self.__name, remove=False
                        )
                    self.new_print(self.__position.get_description())
                except Exception as e:
                    print(f"ERROR while writing character to chunk: {e}")
            except ValueError:
                self.new_print("Firstly, write the direction, you want to go,")
                self.new_print("and secondly, write the number of steps you want to take.")
        else:
            self.new_print("You did not walk, because you don't know which direction.")

    def rest(self) -> None:
        """Rest, no other actions
        take place. The Player
        gets healed."""
        self.new_print("You had a nice rest!")

    def take(self, item: list = None) -> None:
        """Take a given Item from
        the current chunk."""
        if not item is None:
            self.__position = self.load_chunk(self.__position.get_chunk_id())
            for i in item:
                found = False
                item_selected = self.item_in_position(i)
                if item_selected:
                    self.__inventory[item_selected] = (
                        False  # Setting equipped parameter to False
                    )
                    self.__position.remove_item(item_selected)
                    self.new_print(f"You took {item_selected[5:]}.")
                    self.save_chunk()
                    found = True
                if not found:
                    self.new_print(f"There is no {i} at your current location.")

    def drop(self, items: list = None) -> None:
        """Drop a given Item from the
        Inventory to the current chunk."""
        if items is None:
            self.new_print("You dropped ... nothing.")
        else:
            for i in items:
                dropped = False
                item_selected = self.item_in_inventory(i)
                if item_selected:
                    self.__inventory.pop(item_selected)
                    self.__position.add_item(item_selected)
                    self.new_print(f"You dropped {item_selected[5:]}.")
                    self.save_chunk()
                    dropped = True
                if not dropped:
                    if not i == "":
                        self.new_print(
                            f"You tried to drop {i}, but it was not even in your inventory!")
                    else:
                        self.new_print("You dropped ... nothing.")

    def print_inventory(self) -> None:
        """ "Outprints the Inventory, mark
        which item is equiped."""
        if self.__inventory:
            self.new_print("Your inventory contains:")
            for key, value in self.__inventory.items():
                if value:  # check, if item is eqiupped
                    self.new_print(f"{key[5:]} - equipped")
                else:
                    self.new_print(key[5:])
        else:
            self.new_print("Your inventory is empty.")

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
            self.save_chunk()
            item_selected = item_selected_pos
        else:
            self.new_print(f"There is no {item[0]}, you could equip right now.")
        self.unequip()
        self.__inventory[item_selected] = True  # set the eqiupped parameter to true
        if item[0] == "":
            self.new_print("You wanted to equip. But what?")
        # else:
        self.new_print(f"You equipped {item_selected[5:]}.")

    def unequip(self, item: list = None, first_iter: bool = True) -> None:
        """Unequip the Item, which
        is currently equipped."""
        if item is None or not first_iter:
            for inventory_item, equipped in self.__inventory.items():
                if equipped:
                    self.__inventory[inventory_item] = (
                        False  # set the equipped parameter to false
                    )
                    self.new_print(f"You unequipped {inventory_item}.")
        else:
            found = False
            for inventory_item, equipped in self.__inventory.items():
                if inventory_item.startswith(item[0]):
                    found = True
                    self.unequip(None, False)
            if not found:
                self.new_print(f"{item[0]} was no equipped.")

    def eat(self, item: list = None) -> None:
        """Removes the eaten item
        from the inventory and adds
        the saturation to the hunger
        value of the Player."""
        if item:
            for i in item:
                item_selected = self.item_in_inventory(i)
                if item_selected:
                    nutrition = int(self.db_handler.get_item_data(item_selected)[0])
                    self.__inventory.pop(item_selected)
                    #check if item is safely eatable:
                    if nutrition > 1:
                        self.__saturation = int(self.__saturation) + nutrition
                        self.new_print(
                        f"You ate {item_selected[5:]}, it was {nutrition} nutritious."
                        )
                        # update player info:
                        self.send_cmd_packet("set_information_left", ["saturation", self.__saturation])
                    else:
                        self.__health = int(self.__health) +  nutrition
                        self.new_print(
                        f"You ate {item_selected[5:]}, it hurt you {abs(nutrition)} health."
                        )
                        # update player info:
                        self.send_cmd_packet("set_information_left", ["health", self.__health])
                else:
                    self.new_print(f"You tried to eat {i}, but you had none left")
        else:
            self.new_print("You did not eat.")

    def inspect(self) -> None:
        """Outprints the items,
        which are in the current Chunk."""
        self.__position = self.load_chunk(self.__position.get_chunk_id())
        self.new_print(f"There are: {self.__position.get_items()}")
        characters = self.__position.get_characters()
        characters.remove(self.__name)
        self.new_print(f"You see {characters}")
        self.new_print(f"There are also {self.__position.get_containers()}")

    def backflip(self) -> None:
        if self.__backflip_counter < 42:
            self.new_print("You did a backflip.")
            self.__backflip_counter +=1
        else:
            self.new_print("Why the fuck are you backflipping all the time??")
            self.__backflip_counter = 0

    def disconnect(self) -> None:
        self.save_player()
        self.db_handler.update_characters(self.__position.get_chunk_id(), self.__name, remove=True)
        self.send_cmd_packet("server_side_quit", ["Good bye, see you next time"])
        thread_data.client_names[self.__connection_id] = "disconnected"

    def ping(self):
        time_now = time.time_ns()
        print(f"pinged at Time: {time_now}")
        self.new_print(f"Time:{time_now}")

#############################
## combat system user side ##
#############################

    def attack(self):
        self.send_cmd_packet(command="add_server_ingame_entries", ["attack"])
        #attack
        self.send_cmd_packet(command="delete_server_ingame_entries", ["attack"])

    def defend(self):
        self.send_cmd_packet(command="add_server_ingame_entries", ["block"])
        # defend
        self.send_cmd_packet(command="delete_server_ingame_entries", ["block"])

#####################################
## combat system internal methods: ##
#####################################

    def enter_attack_mode(self):
        self.send_cmd_packet(command="add_server_ingame_entries", ["attack"])

    def leave_attack_mode(self):
        self.send_cmd_packet(command="delete_server_ingame_entries", ["attack"])

    def enter_defend_mode(self):
        self.send_cmd_packet(command="add_server_ingame_entries", ["block"])

    def leave_defend_mode(self):
        self.send_cmd_packet(command="delete_server_ingame_entries", ["block"])

    def start_fight(self, opponnent) -> None:
        opponnents: list = self.__position.get_characters()
        if opponnent in opponnents:
            self.send_cmd_packet(command="delete_server_ingame_entries", args=["save_player", "move", "rest", "inspect"])
            
        else:
            self.new_print(f"You can not attack {opponnent}, because {opponnent} is not here right now.")
    def end_fight(self, opponnents: list) -> None:
        self.send_cmd_packet(command="add_server_ingame_entries", args=["save_player", "move", "rest", "inspect"])
        

cmd_line_args = sys.argv
try:
    game_file_path = cmd_line_args[1]
except IndexError:
    game_file_path = ""
try:
    local = cmd_line_args[2]
    if local.lower() == "false":
        local = False
    else:
        local = True
except IndexError:
    local = True
try:
    server_port = int(cmd_line_args[3])
except IndexError:
    server_port = 27300

#  for custom gameslot uncomment following 2 lines
#GAMESLOT = "gilbert"
#game_file_path = f"saves/gameslot_{GAMESLOT}.sqlite"

thread_data = network_handler.ThreadData()
network_server = network_handler.NetworkServer(
    thread_data, ServerMethods, game_file_path,
    local=local, port=server_port
    )

if __name__ == "__main__":
    network_server.main()
