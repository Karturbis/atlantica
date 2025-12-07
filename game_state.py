
class GameState():

    # initialisation:

    def __init__(self):
        self._map: dict = {}  # self.load_map()
        self._things: dict ={}  # self.load_things()

    def _load_map(self) -> dict:
        """Return a dict, where the keys
        are the room IDs of all rooms
        and the values are the room objects."""
        raise NotImplementedError

    def _load_things(self) -> dict:
        """Return a dict, where the keys
        are the thing Ids of all things
        in the game and the values are
        the thing objects."""
        raise NotImplementedError

    # getter:

    def get_room_by_id(self, room_id: str):
        return self._map[room_id]

    def get_item_by_id(self, item_id: str):
        return self._things[item_id]
