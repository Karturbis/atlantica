import threading
import json

import game_classes as gc


class GameState():

    # initialisation:

    def __init__(self):
        self._map: dict = self._load_map()
        self._map_lock = threading.Lock()
        self._things: dict = self._load_things()
        self._things_lock = threading.Lock()
        self._players: dict = self._load_players()
        self._players_lock = threading.Lock()

    def _load_map(self) -> dict:
        """Return a dict, where the keys
        are the room IDs of all rooms
        and the values are the room objects."""
        game_map: dict = {}
        # load the map file:
        with open("game_data/map.json", "r", encoding="utf-8") as reader:
            data = json.loads(reader.read())
        # create room objects
        for room_id in data:
            room_data = data[room_id]
            game_map[room_id] = gc.Room(
                room_id, room_data["room_north_id"], room_data["room_east_id"],
                room_data["room_south_id"], room_data["room_wes_id"]
                )
            # add items to room objects
            for item in room_data["content"]:
                game_map[room_data].add_item(item)
        return game_map



    def _load_things(self) -> dict:
        """Return a dict, where the keys
        are the thing Ids of all things
        in the game and the values are
        the thing objects."""
        items: dict = {}
        with open("game_data/items.json", "r", encoding="utf-8") as reader:
            data = json.loads(reader.read())
        for item_id in data:
            item_data = data[item_id]
            items[item_id] = gc.make_thing(item_id, item_data["name"], item_data["article"])
        return items

    def _load_players(self) -> dict:
        """Return a dict, where the keys
        are the player names and the values
        are the player objects."""
        raise NotImplementedError

    # getter:

    def get_room_by_id(self, room_id: str):
        with self._map_lock:
            return self._map[room_id]

    def get_item_by_id(self, item_id: str):
        with self._things_lock:
            return self._things[item_id]

    def get_player_by_name(self, player_name: str):
        with self._players_lock:
            return self._players[player_name]

    # adder:

    def add_player(self, player):
        with self._players_lock:
            self._players[player.get_name()] = player
