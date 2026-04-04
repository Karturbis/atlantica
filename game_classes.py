"""All classes for game participants, such as
items and players."""

import threading

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
        return lambda **_: f"You can not {verb_name} {self._name}"


class Thing(VerbHolder):

    # initialisation:

    def __init__(
            self, thing_id: str, name: str,
            article: str, description: str = "a thing"
            ):
        super().__init__(name)
        self._id: str = thing_id
        self._article: str = article
        self._description = description
        self.lock = threading.Lock()

    # getter and setter:

    def get_id(self):
        return self._id

    # verbs:

    def v_drop(self, **kwargs) -> str:
        """Drops the item from the players inventory
        @param player: game_classes.Player,
        @param position: game_classes.Room
        """
        game_state = kwargs["game_state"]
        player_name = kwargs["player_name"]
        player = game_state.get_player_by_name(player_name)
        position = game_state.get_room_by_id(player.get_position())
        player.remove_from_inventory(self._id)
        position.add_item(self._id)
        return f"You dropped {self._article} {self._name}."

    def v_pick_up(self, **kwargs) -> str:
        """Adds an item from somewhere to the players inventory
        @param player: game_classes.Player,
        @param position: game_classes.Room
        """
        game_state = kwargs["game_state"]
        player_name = kwargs["player_name"]
        player = game_state.get_player_by_name(player_name)
        position = game_state.get_room_by_id(player.get_position())
        success: bool = position.remove_item(self._id)
        if success:
            player.add_to_inventory(self._id)
            return f"You picked up {self._article} {self._name}."
        return f"There is no {self._name} to pick up."

    def v_inspect(self, **_) -> str:
        """Gives specific information about the
        inspected thing"""
        return self._description


class Food(Thing):

    # verbs:

    def v_eat(self, **kwargs):
        game_state = kwargs["game_state"]
        player_name = kwargs["player_name"]
        player = game_state.get_player_by_name(player_name)
        if player.item_exists(self._id):
            player.remove_from_inventory(self._id)
            return f"You have eaten {self._article} {self._name}"
        return f"You have to pickup {self._article} {self._name} first."

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


class Direction(VerbHolder):

    def __init__(self, room_to_id: str, room_id: str):
        super().__init__(room_id)
        self._room_to_id: str = room_to_id
        self._direction = ""

    # getter:

    def get_room_to_id(self) -> str:
        return self._room_to_id

    # verbs

    def v_move(self, **kwargs) -> str:
        """Moves the player on the map."""
        game_state = kwargs["game_state"]
        player_name = kwargs["player_name"]
        player = game_state.get_player_by_name(player_name)
        old_room = game_state.get_room_by_id(self._name)
        if self._room_to_id:
            if old_room.remove_item(f"p_{player_name}"):
                game_state.get_room_by_id(
                    self._room_to_id).add_item(f"p_{player_name}")
                player.set_position(self._room_to_id)
                return f"You moved {self._direction}"
            return f"You could not move {self._direction}"
        return f"You can not move {self._direction}wards, the way is blocked"


class North(Direction):

    def __init__(self, room_to_id: str, room_id: str):
        super().__init__(room_to_id, room_id)
        self._direction = "north"


class East(Direction):

    def __init__(self, room_to_id: str, room_id: str):
        super().__init__(room_to_id, room_id)
        self._direction = "east"


class South(Direction):
    def __init__(self, room_to_id: str, room_id: str):
        super().__init__(room_to_id, room_id)
        self._direction = "south"


class West(Direction):
    def __init__(self, room_to_id: str, room_id: str):
        super().__init__(room_to_id, room_id)
        self._direction = "west"


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

    # getter:

    def get_position(self):
        with self._position_lock:
            return self._position

    def get_name(self):
        return self._name

    def get_inventory(self):
        with self._inventory_lock:
            return self._inventory

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

    def v_look(self, **kwargs) -> str:
        """Returns, what the player sees in the
        curren room."""
        game_state = kwargs["game_state"]
        with self._position_lock:
            room = game_state.get_room_by_id(self._position)
        to_see: list[str] = room.get_content()
        if to_see:
            message: str = "You see:\n"
            for item_id in to_see:
                item = game_state.get_item_by_id(item_id)
                if item:
                    message = f"{message}{item.get_name()}\n"
                else: # could not fetch item object, name belongs to a player
                    message = f"{message}{item_id[2:]}\n"  # strip the p_ from the start of the player name
            return message[:-1] # remove last \n
        return "There is nothing to see"

    def v_inventory(self, **kwargs) -> str:
        """Returns the contents of the
        players inventory"""
        game_state = kwargs["game_state"]
        message: str = "Your inventory contains:\n"
        with self._inventory_lock:
            if self._inventory:
                for item_id in self._inventory:
                    message = f"{message}{game_state.get_item_by_id(item_id).get_name()} "
            else:
                message = "Your inventory is empty"
        return message

    def v_backflip(self, **_) -> str:
        return "you did a backflip"

    def v_ping(self, **_) -> str:
        return "pong"


class Room():

    def __init__(
        self, room_id: str, directions: dict):
        self._id: str = room_id
        self._directions: dict = directions
        self._content: list[str] = []
        self._content_lock = threading.Lock()

    # getter:

    def get_id(self):
        return self._id

    def get_directions(self):
        return self._directions

    def get_content(self):
        with self._content_lock:
            return self._content

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
