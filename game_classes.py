"""All classes for game participants, such as
items and players."""

import threading
import logging

# configure logging:
logger = logging.getLogger(__name__)

class VerbHolder():
    """Parent class for all classes that can hold verbs."""
    # initialisation:

    def __init__(self, name: str):
        self.export_verbs()
        self._name: str = name

    def export_verbs(self) -> None:
        """create a list of verbs in the current class
        all verbs are methods, which start with v_.
        add the verbs to the verbs file."""
        self_verbs: list = [f"{i}\n" for i in self.get_verb_names()]
        with open("parser/verbs_en", "r", encoding="utf-8") as reader:
            file_verbs: list = reader.readlines()
        # add only verbs to file, wich it does not contain yet
        verbs_to_add: list = [
            verb for verb in self_verbs if not verb in file_verbs
            ]
        if verbs_to_add:
            with open("parser/verbs_en", "a", encoding="utf-8") as writer:
                writer.writelines(verbs_to_add)

    # getter and setter:

    def get_name(self):
        return self._name

    def get_verb_names(self) -> list:
        """returns all verbnames of the current item.
        a verb is a method, which is user executable.
        verb methods always start with 'v_'. this method
        strips the 'v_' from the verb name."""
        return [method[2:] for method in dir(self) if
                callable(getattr(self, method))
                and method.startswith("v_")
                ]

    def get_verb_by_name(self, verb_name: str):
        """returns the verb, which corresponds to
        the given name. the name must not include
        the prefix 'v_'."""
        func_name = f"v_{verb_name}"
        if hasattr(self, func_name):
            return getattr(self, func_name)
        return lambda *_, **__: f"You can not {verb_name} {self._name}"


class Thing(VerbHolder):

    # initialisation:

    def __init__(
            self, thing_id: str, name: str,
            article: str, adjectives: list = None,
            description: str = "a thing"
            ):
        super().__init__(name)
        self._id: str = thing_id
        self._article: str = article
        if adjectives:
            self._adjectives = adjectives
        else:
            self._adjectives = [""]
        self._description = description
        self.lock = threading.Lock()

    # getter and setter:

    def get_id(self) -> str:
        return self._id

    def get_adjectives(self) -> list:
        return self._adjectives

class Food(Thing):
    pass

class Apple(Food):
    pass


class Potato(Food):
    pass


class Bread(Food):
    pass


class Weapon(Thing):
    pass


class MeeleWeapon(Weapon):
    pass


class Sword(MeeleWeapon):
    pass


class Axe(MeeleWeapon):
    pass


class RangeWeapon(Weapon):
    pass


class Bow(RangeWeapon):
    pass


class Player(VerbHolder):

    def __init__(self, name: str, position: str, inventory: list[str] = None):
        super().__init__(name)
        if inventory:
            self._inventory: list[str] = inventory
        else:
            self._inventory: list[str] = []
        self._inventory_lock = threading.Lock()
        self._position: str = position
        self._position_lock = threading.Lock()

    def remove_from_inventory(self, item_id: str):
        with self._inventory_lock:
            self._inventory.remove(item_id)

    def add_to_inventory(self, item_id: str):
        with self._inventory_lock:
            self._inventory.append(item_id)

    def _get_direct_object_id(self, items_list: list, direct_noun: str, direct_adjective: str) -> str:
        for item in items_list:
            if item.get_name() == direct_noun:
                if direct_adjective in item.get_adjectives():
                    return item.get_id()
        return None

    def execute_command(self, command, game_state) -> dict:
        """Take the output from stage two and the
        game state. Get the method that has to be executet
        and executes that method. Returns the result as a
        dict, this is the message the user will see"""
        # initialize variables:
        # TODO: find better way and place for defining directions
        directions: list = ["north", "east", "west", "south"]
        direct_noun = command.direct_object["noun"]
        direct_adjective = command.direct_object["adjective"]
        func = self.get_verb_by_name(command.verb)
        room = game_state.get_room_by_id(self._position)
        # get the game object corresponding to the
        # direct_object from the command
        if not direct_noun:
            return func(game_state)
        inventory_item_ids = self.get_inventory()
        room_item_ids = room.get_content()
        room_player_names = room.get_players()
        inventory_items= [game_state.get_item_by_id(id) for id in inventory_item_ids]
        direct_object_id = self._get_direct_object_id(inventory_items, direct_noun, direct_adjective)
        if direct_object_id:
            return func(game_state, direct_object_id)
        room_items = [game_state.get_item_by_id(id) for id in room_item_ids]
        logger.debug(f"room items: {room_items}")
        direct_object_id = self._get_direct_object_id(room_items, direct_noun, direct_adjective)
        if direct_object_id:
            return func(game_state, direct_object_id)
        for player_name in room_player_names:
            if player_name == direct_noun:
                return func(game_state, player_name)
        if direct_noun in directions:
            return func(game_state, direct_noun)
        return {"client_print": f"there is no {direct_noun} in your vicinity"}


    # getter:

    def get_position(self) -> str:
        with self._position_lock:
            return self._position

    def get_inventory(self) -> list:
        with self._inventory_lock:
            return list(self._inventory)

    def item_exists(self, item_id):
        with self._inventory_lock:
            if item_id in self._inventory:
                return True
            return False


    # setter:

    def set_position(self, position: str):
        with self._position_lock:
            self._position = position

    # verbs:

    def v_look(self, game_state, *_, **__) -> dict:
        """Returns, what the player sees in the
        curren room."""
        with self._position_lock:
            room = game_state.get_room_by_id(self._position)
        items_to_see: list[str] = room.get_content()
        players_to_see: list[str] = list(room.get_players())
        players_to_see.remove(self._name)
        message: str = "You see:\n"
        if items_to_see:
            for item_id in items_to_see:
                item = game_state.get_item_by_id(item_id)
                message = f"{message}{item.get_name()}\n"
        if players_to_see:
            for player_name in players_to_see:
                message = f"{message}{player_name}\n"
        if message == "You see:\n":
            return {"client_print" : "There is nothing to see"}
        return {"client_print" : message[:-1]}  # remove last \n

    def v_inventory(self, game_state, *_, **__) -> dict:
        """Returns the contents of the
        players inventory"""
        message: str = "Your inventory contains:\n"
        with self._inventory_lock:
            if self._inventory:
                for item_id in self._inventory:
                    message = f"{message}{game_state.get_item_by_id(item_id).get_name()} "
            else:
                message = "Your inventory is empty"
        return {"client_print" : message}

    def v_backflip(self, *_, **__) -> dict:
        return {"client_print" : "you did a backflip", "room_print": "did a backflip"}

    def v_ping(self, *_, **__) -> dict:
        return {"client_print" : "pong"}

    def v_shout(self, *_, **__) -> dict:
        return {"client_print": "you shouted", "room_print": "shouted loud"}

    def v_position(self, *_, **__) -> dict:
        return {"client_print" : f"You are at {self._position}"}

    # verbs with objects as arguments:

    def v_inspect(self, game_state, item_id, **__) -> dict:
        """Gives specific information about the
        inspected thing"""
        item = game_state.get_item_by_id(item_id)
        return {"client_print" : item._description}

    def v_eat(self, game_state, item_id, **__) -> dict:
        item = game_state.get_item_by_id(item_id)
        if self.item_exists(item_id):
            self.remove_from_inventory(item_id)
            return {"client_print" : f"You have eaten {item._article} {item._name}"}
        return {"client_print" : f"You have to pickup {item._article} {item._name} first."}

    def v_move(self, game_state, direction, **__) -> dict:
        """Moves the player on the map."""
        old_room = game_state.get_room_by_id(self.get_position())
        directions = old_room.get_directions()
        if direction in directions:  # check if the direction exists
            if directions[direction]:  # check if the direction is walkable
                room_to_id = directions[direction]
                logger.debug(f"room to id: {room_to_id}")
                if old_room.remove_player(self._name):
                    game_state.get_room_by_id(room_to_id).add_player(self._name)
                    self.set_position(room_to_id)
                    return  {"client_print" : f"You moved {direction}wards", "room_print": "entered the room"}
                return {"client_print" : f"You could not leave your current position ({self.get_position()})"}
            return {"client_print" : f"You can not move {direction}wards, the way is blocked"}
        return {"client_print": f"There is no direction '{direction}'"}

    def v_drop(self, game_state, item_id, **_) -> dict:
        """Drops the item from the players inventory"""
        position = game_state.get_room_by_id(self.get_position())
        self.remove_from_inventory(item_id)
        position.add_item(item_id)
        item = game_state.get_item_by_id(item_id)
        return {
            "client_print" : f"You dropped {item._article} {item._name}.",
            "room_print": f"dropped {item._article} {item._name}"
            }

    def v_pick_up(self, game_state, item_id, **_) -> dict:
        """Adds an item from somewhere to the players inventory
        @param player: game_classes.Player,
        @param position: game_classes.Room
        """
        position = game_state.get_room_by_id(self.get_position())
        success: bool = position.remove_item(item_id)
        item = game_state.get_item_by_id(item_id)
        if success:
            self.add_to_inventory(item_id)
            return {
                "client_print": f"You picked up {item._article} {item._name}.",
                "room_print": f"took {item._article} {item._name}"
                }
        return {"client_print" : f"There is no {item._name} to pick up."}

class Room():

    def __init__(
        self, room_id: str, directions: dict):
        self._id: str = room_id
        self._directions: dict = directions
        self._players: list[str] = []
        self._players_lock = threading.Lock()
        self._content: list[str] = []
        self._content_lock = threading.Lock()

    # getter:

    def get_id(self) -> str:
        return self._id

    def get_directions(self) -> dict:
        return self._directions

    def get_content(self) -> list[str]:
        with self._content_lock:
            return self._content

    def get_players(self) -> list[str]:
        with self._players_lock:
            return self._players

    def item_exists(self, item_id) -> bool:
        with self._content_lock:
            if item_id in self._content:
                return True
            return False

    # setter:

    def remove_item(self, item_id) -> bool:
        with self._content_lock:
            if item_id in self._content:
                self._content.remove(item_id)
                return True
            return False

    def add_item(self, item_id) -> None:
        with self._content_lock:
            self._content.append(item_id)

    def remove_player(self, player_name: str) -> bool:
        with self._players_lock:
            if player_name in self._players:
                self._players.remove(player_name)
                return True
            return False

    def add_player(self, player_name: str) -> None:
        with self._players_lock:
            self._players.append(player_name)

things: dict = {
    "apple": Apple,
    "potato": Potato,
    "sword": Sword,
    "axe": Axe,
    "bow": Bow
}

def make_thing(thing_id: str, name:str, article:str, *args, **kwargs):
    # strip number of thing id, to get type:
    thing_type = thing_id.strip("0123456789_").lower()
    return things[thing_type](thing_id, name, article, *args, **kwargs)

if __name__ == "__main__":
    apple = Apple("apple_000", "Apple", "The")
