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
        verbs_to_add: list = [verb for verb in self_verbs if not verb in file_verbs]
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

    def __init__(self, thing_id: str, name: str, article: str):
        super().__init__(name)
        self._id: str = thing_id
        self._article: str = article
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
        with position.lock:
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
        success = False
        with position.lock:
            if position.item_exists(self._id):
                position.remove_item(self._id)
                success = True
        if success:
            player.add_to_inventory(self._id)
            return f"You picked up {self._article} {self._name}."
        return f"There is no {self._name} to pick up."


class Food(Thing):

    def __init__(self, thing_id: str, name: str, article: str):
        super().__init__(thing_id, name, article)

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

    def __init__(self, thing_id: str, name: str, article: str):
        super().__init__(thing_id, name, article)


class Potato(Food):

    def __init__(self, thing_id: str, name: str, article: str):
        super().__init__(thing_id, name, article)


class Weapon(Thing):

    def __init__(self):
        pass


class MeeleWeapon(Weapon):

    def __init__(self):
        pass


class Sword(MeeleWeapon):

    def __init__(self):
        pass


class Axe(MeeleWeapon):

    def __init__(self):
        pass


class RangeWeapon(Weapon):

    def __init__(self):
        pass


class Bow(RangeWeapon):

    def __init__(self):
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
        message: str = "You see:\n"
        for item in to_see:
            # TODO implement pretty printing of the items (with articles)
            message = f"{message}{item} "
        return message

    def v_inventory(self, **_) -> str:
        """Returns the contents of the
        players inventory"""
        message: str = "Your inventory contains:\n"
        with self._inventory_lock:
            if self._inventory:
                for item in self._inventory:
                    message = f"{message}{item} "
            else:
                message = "Your inventory is empty"
        return message

class Room():

    def __init__(
        self, room_id: str, room_north_id: str, room_east_id: str,
        room_south_id: str, room_west_id: str
        ):
        self._id: str = room_id
        self._north_id: str = room_north_id
        self._east_id: str = room_east_id
        self._west_id: str = room_west_id
        self._south_id: str = room_south_id
        self._content: list[str] = []
        self._content_lock = threading.Lock()

    # getter:

    def get_id(self):
        return self._id

    def get_north_id(self):
        return self._north_id

    def get_east_id(self):
        return self._east_id

    def get_south_id(self):
        return self._south_id

    def get_west_id(self):
        return self._west_id

    def get_content(self):
        with self._content_lock:
            return self._content

    def item_exists(self, item_id) -> bool:
        with self._content_lock:
            if item_id in self._content:
                return True
            return False

    # setter:

    def remove_item(self, item_id) -> None:
        with self._content_lock:
            if item_id in self._content:
                self._content.remove(item_id)

    def add_item(self, item_id) -> None:
        with self._content_lock:
            self._content.append(item_id)


def make_thing(thing_id: str, name:str, article:str, *args, **kwargs):
    # strip number of thing id, to get type:
    thing_type = thing_id.strip("0123456789_").lower()
    # big switch case for all types:
    if thing_type == "apple":
        return Apple(thing_id, name, article, *args, **kwargs)
    if thing_type == "potato":
        return Potato(thing_id, name, article, *args, **kwargs)


if __name__ == "__main__":
    apple = Apple("apple_000", "Apple", "The")
