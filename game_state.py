import threading


class GameState():

    # initialisation:

    def __init__(self):
        self.__map: dict = {}# self.load_map()
        self.__things: dict ={}# self.load_things()

    def load_map(self) -> dict:
        """Return a dict, where the keys
        are the room IDs of all rooms
        and the values are the room objects."""
        raise NotImplementedError

    def load_things(self) -> dict:
        """Return a dict, where the keys
        are the thing Ids of all things
        in the game and the values are
        the thing objects."""
        raise NotImplementedError

    # getter:

    def get_room_by_id(self, room_id: str):
        return self.__map[room_id]

    def get_item_by_id(self, item_id: str):
        return self.__things[item_id]
