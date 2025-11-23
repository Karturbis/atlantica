"""All classes for game participants, such as
items and players."""

import threading

from game_state import GameState

class Thing():

    # initialisation:

    def __init__(self, thing_id: str, name: str, article: str, game_state):
        self.export_verbs()
        self._id: str = thing_id
        self._name: str = name
        self._article: str = article
        self.lock = threading.Lock()
        self.game_state = game_state

    def export_verbs(self) -> None:
        """create a list of verbs in the current class
        all verbs are methods, which start with v_.
        add the verbs to the verbs file."""
        self_verbs: list = [f"{method[2:]}\n" for method in dir(self) if
                callable(getattr(self, method))
                and method.startswith("v_")
                ]
        with open("parser/verbs", "r", encoding="utf-8") as reader:
            file_verbs: list = reader.readlines()
        # add only verbs to file, wich it does not contain yet
        verbs_to_add: list = [verb for verb in self_verbs if not verb in file_verbs]
        with open("parser/verbs", "a", encoding="utf-8") as writer:
            writer.writelines(verbs_to_add)

    # getter and setter:

    def get_id(self):
        return self._id

    # verbs:

    def v_drop(self, player, room_id: str) -> str:
        position = self.game_state.get_room_by_id(room_id)
        player.remove_from_inventory(self._id)
        with position.lock:
            position.add_item(self._id)
        return f"You dropped {self._article} {self._name}."

    def v_pick_up(self, player, room_id: str) -> str:
        position = self.game_state.get_room_by_id(room_id)
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

    def __init__(self, thing_id: str, name: str, article: str, game_state):
        super().__init__(thing_id, name, article, game_state)

    # verbs:

    def v_eat(self, player):
        player.remove_from_inventory(self._id)
        return f"You have eaten {self._article} {self._name}"

class Apple(Food):

    def __init__(self, thing_id: str, name: str, article: str, game_state):
        super().__init__(thing_id, name, article, game_state)
    


class Potato(Food):

    def __init__(self):
        pass


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


class Player():

    def __init__(self, name: int, position: int):
        self.__name: str = name
        self.__inventory: list[int] = []
        self.__position: int = position

    def remove_from_inventory(self, item_id: str):
        self.__inventory.remove(item_id)

    def add_to_inventory(self, item_id: str):
        self.__inventory.append(item_id)
    
    def get_position(self):
        return self.__position


class Room():

    def __init__(
        self, room_id: str, room_north_id: str, room_east_id: str,
        room_south_id: str, room_west_id: str
        ):
        self.__id: str = room_id
        self.__north_id: str = room_north_id
        self.__east_id: str = room_east_id
        self.__west_id: str = room_west_id
        self.__south_id: str = room_south_id
        self.__content: list[str] = []
        self.lock = threading.Lock()

    # getter:

    def get_id(self):
        return self.__id

    def get_north_id(self):
        return self.__north_id

    def get_east_id(self):
        return self.__east_id

    def get_south_id(self):
        return self.__south_id

    def get_west_id(self):
        return self.__west_id

    def get_content(self):
        return self.__content
    
    def item_exists(self, item_id) -> bool:
        if item_id in self.__content:
            return True
        # no else needed
        return False

    # setter:

    def remove_item(self, item_id) -> None:
        if item_id in self.__content:
            self.__content.remove(item_id)

    def add_item(self, item_id) -> None:
        self.__content.append(item_id)



if __name__ == "__main__":
    gs = GameState()
    apple = Apple("apple_000", "Apple", "The", gs)