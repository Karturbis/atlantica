import time
import sys
from inspect import signature
from ast import literal_eval  # Used to evaluate a boolean from a string

from handler import network_handler
from handler import DatabaseHandler


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
    Items are spawning in Chunks, in
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
        return self.__nutrition
    
    def get_description(self) -> str:
        return self.__description
    
    def get_damage(self) -> int:
        return self.__damage

    def get_crit_damage(self) -> int:
        return self.__crit_damage


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


class ServerMethods():

    def __init__(self, connection, connection_id, thread_data):
        self.__connection = connection
        self.__connection_id = connection_id
        self.__thread_data = thread_data
        self.__standart_server_methods = [
            "ping", "fanf", "move", "rest",
            "take", "drop", "print_inventory",
            "unequip", "eat", "inspect", "equip",
            "save_player", "shutdown"
            ]
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

    def init_character_data(self, game_file_path):
        self.__name = thread_data.client_names[self.__connection_id]
        self.db_handler = DatabaseHandler(game_file_path[0])
        try:
            self.db_handler.get_character_data(self.__name)
        except IndexError:  # no character data for this name was found
            self.db_handler.new_character(self.__name)
        try:
            self.__position = Chunk(
                "000-temple-start", *self.db_handler.get_chunk_data("000-temple-start")
            )
        except Exception as e:
            print(f"ERROR {e}")
        character_data = self.db_handler.get_character_data(self.__name)
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
        if len(inventory_list) >= 1:
            self.__inventory = dict(inventory_list)
        else:
            self.__inventory = {}
        for i in self.__inventory:
            self.__inventory[i] = literal_eval(self.__inventory[i])

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
        try:
            func = getattr(self, command)
        except AttributeError:
            return f"There is no command called {command}"
        given_args_len = len(args)
        expected_args_len = len(signature(func).parameters)
        if given_args_len >= 1:
            if expected_args_len == given_args_len:
                # run method:
                try:
                    return func(args)
                except Exception as e:
                    return f"ERROR in (1) ServerMethods.excute_cmd: {e}"
            else: # wrong number of arguments were given
                return f"Command {command} takes {expected_args_len} arguments, you gave {given_args_len}."
        else:  # no args where given:
            if expected_args_len == given_args_len:
                # run method:
                try:
                    return func()
                except Exception as e:
                    return f"ERROR in (2) ServerMethods.excute_cmd: {e}"
            else: # wrong number of arguments were given
                return f"Command {command} takes {expected_args_len} arguments, you gave {given_args_len}."

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
        inventory: str = ""
        for key, item in self.__inventory.items():
            inventory = f"{inventory}{key}:{item}, "
        inventory = inventory[:-2]
        self.db_handler.update_character(
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
            network_server.send_print_packet(str(chunk_data[4]), self.__connection)
        except IndexError:
            network_server.send_print_packet("Where you wanted to go, there is just void.", self.__connection)
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
                        network_server.send_print_packet(
                            "You did not walk, the direction you want to go does not exist.",
                            self.__connection
                        )
            except ValueError:
                network_server.send_print_packet(
                    "\nFirstly, write the direction, you want to go,",
                    self.__connection
                )
                network_server.send_print_packet(
                    "and secondly, write the number of steps you want to take.",
                    self.__connection
                )
            return "end_of_command"
        else:
            network_server.send_print_packet(
                "You did not walk, because you don't know which direction.",
                self.__connection
            )

    def rest(self) -> None:
        """Rest, no other actions
        take place. The Player
        gets healed."""
        return "You had a nice rest!"

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
                    network_server.send_print_packet(
                        f"You took {item_selected[5:]}.",
                        self.__connection
                    )
                    self.save_chunk()
                    found = True
                if not found:
                    return f"There is no {i} at your current location."
                else:
                    return "end_of_command"

    def drop(self, items: list = None) -> None:
        """Drop a given Item from the
        Inventory to the current chunk."""
        if items is None:
            return "You dropped ... nothing."
        else:
            for i in items:
                dropped = False
                item_selected = self.item_in_inventory(i)
                if item_selected:
                    self.__inventory.pop(item_selected)
                    self.__position.add_item(item_selected)
                    network_server.send_print_packet(
                        f"You dropped {item_selected[5:]}.",
                        self.__connection)
                    self.save_chunk()
                    dropped = True
                if not dropped:
                    if not i == "":
                        network_server.send_print_packet(
                            f"You tried to drop {i}, but it was not even in your inventory!",
                            self.__connection
                        )
                    else:
                        network_server.send_print_packet(
                            "You dropped ... nothing.",
                            self.__connection
                        )
            return "end_of_command"

    def print_inventory(self) -> None:
        """ "Outprints the Inventory, mark
        which item is equiped."""
        if self.__inventory:
            network_server.send_print_packet(
                "Your inventory contains:",
                self.__connection
            )
            for key, value in self.__inventory.items():
                if value:  # check, if item is eqiupped
                    network_server.send_print_packet(
                        f"{key[5:]} - equipped",
                        self.__connection
                    )
                else:
                    network_server.send_print_packet(
                        key[5:], self.__connection
                    )
            return "end_of_command"
        else:
            return "Your inventory is empty."

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
            return f"There is no {item[0]}, you could equip right now."
        self.unequip()
        self.__inventory[item_selected] = True  # set the eqiupped parameter to true
        if item[0] == "":
            return "You wanted to equip. But what?"
        # else:
        return f"You equipped {item_selected[5:]}."

    def unequip(self, item: list = None, first_iter: bool = True) -> None:
        """Unequip the Item, which
        is currently equipped."""
        if item is None or not first_iter:
            for inventory_item, equipped in self.__inventory.items():
                if equipped:
                    self.__inventory[inventory_item] = (
                        False  # set the equipped parameter to false
                    )
                    network_server.send_print_packet(
                        f"You unequipped {inventory_item}.",
                        self.__connection
                    )
            return "end_of_command"
        else:
            found = False
            for inventory_item, equipped in self.__inventory.items():
                if inventory_item.startswith(item[0]):
                    found = True
                    self.unequip(None, False)
            if not found:
                return f"{item[0]} was no equipped."

    def eat(self, item: list = None):
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
                        network_server.send_print_packet(
                        f"You ate {item_selected[5:]}, it was {nutrition} nutritious.",
                        self.__connection
                        )
                        # update player info:
                        network_server.send_packet(network_handler.NetworkPacket(
                            packet_type="command",
                            command_name="set_information_left",
                            command_attributes=["saturation", self.__saturation]
                        ),
                        self.__connection
                        )
                    else:
                        self.__health = int(self.__health) +  nutrition
                        network_server.send_print_packet(
                        f"You ate {item_selected[5:]}, it hurt you {abs(nutrition)} health.",
                        self.__connection
                        )
                        # update player info:
                        network_server.send_packet(network_handler.NetworkPacket(
                            packet_type="command",
                            command_name="set_information_left",
                            command_attributes=["health", self.__health]
                        ),
                        self.__connection
                        )
                    return "end_of_command"
                else:
                    network_server.send_print_packet(
                        f"You tried to eat {i}, but you had none left",
                        self.__connection
                    )
        else:
            return "You did not eat."

    def inspect(self):
        """Outprints the items,
        which are in the current Chunk."""
        self.__position = self.load_chunk(self.__position.get_chunk_id())
        return f"There are: {self.__position.get_items()}"

    def fanf(self):
        packet = network_handler.NetworkPacket(
            packet_type="command",
            command_name="new_print",
            command_attributes=["DATA"]
        )
        network_server.send_packet(packet, self.__connection)
        return "end_of_command"

    def ping(self):
        return f"Time:{time.time_ns()}"

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
    server_port = cmd_line_args[3]
except IndexError:
    server_port = 27300

#  for custom gameslot uncomment following 2 lines
GAMESLOT = "qwed"
game_file_path = f"saves/gameslot_{GAMESLOT}.sqlite"

thread_data = network_handler.ThreadData()
network_server = network_handler.NetworkServer(
    thread_data, ServerMethods, game_file_path,
    local=local, port=server_port
    )

if __name__ == "__main__":
    network_server.main()
