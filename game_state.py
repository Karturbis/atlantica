import threading
import json

import game_classes as gc


class GameState():

    # initialisation:

    def __init__(self, game_slot: str):
        self._map: dict = self._load_map(game_slot)
        self._map_lock = threading.Lock()
        self._things: dict = self._load_things()
        self._things_lock = threading.Lock()
        self._players: dict = self._load_players(game_slot)
        self._players_lock = threading.Lock()

    def _load_map(self, game_slot) -> dict:
        """Return a dict, where the keys
        are the room IDs of all rooms
        and the values are the room objects."""
        game_map: dict = {}
        # load the map file:
        with open(f"saves/gameslot_{game_slot}_map.json", "r", encoding="utf-8") as reader:
            data = json.loads(reader.read())
        # create room objects
        for room_id in data:
            room_data = data[room_id]
            game_map[room_id] = gc.Room(
                room_id, room_data["room_north_id"], room_data["room_east_id"],
                room_data["room_south_id"], room_data["room_west_id"]
                )
            # add items to room objects
            for item in room_data["content"]:
                game_map[room_id].add_item(item)
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
            items[item_id] = gc.make_thing(item_id, item_data["name"], item_data["article"], description = item_data["description"])
        return items

    def _load_players(self, game_slot) -> dict:
        """Return a dict, where the keys
        are the player names and the values
        are the player objects. All player positions
        are 'offline' until the corresponding clients
        connect to the server."""
        with open(f"saves/gameslot_{game_slot}_players.json", "r", encoding="utf-8") as reader:
            players_raw = json.loads(reader.read())
        players: dict = {}
        for name, player_data in players_raw.items():
            players[name] = gc.Player(name, "offline", player_data["inventory"])
        return players

    # getter:

    def get_room_by_id(self, room_id: str):
        with self._map_lock:
            try:
                return self._map[room_id]
            except KeyError:
                return False

    def get_item_by_id(self, item_id: str):
        with self._things_lock:
            try:
                return self._things[item_id]
            except KeyError:
                return False

    def get_player_by_name(self, player_name: str):
        with self._players_lock:
            try:
                return self._players[player_name]
            except KeyError:
                return False

    # adder:

    def add_player(self, player):
        with self._players_lock:
            self._players[player.get_name()] = player

    def load_player(self, player_name:str, game_slot):
        """Loads the player. Because the player is already in
        the players dict, the only action necessary is to set the
        players position from 'offline' to the previously saced position"""
        with open(f"saves/gameslot_{game_slot}_players.json", "r", encoding="utf-8") as reader:
            players_raw = json.loads(reader.read())
        position: str = players_raw[player_name]["position"]
        with self._players_lock:
            player = self._players[player_name]
        player.set_position(position)

    # saving:

    def save_game(self, game_slot):
        self.save_players(game_slot)
        self.save_map(game_slot)

    def save_players(self, game_slot):
        player_data: dict = {  # structure:
                            # player_name: {"position": position, "inventory:" inventory}
                            }
        with self._players_lock:
            for name, player in self._players.items():
                player_data[name] = {"position": player.get_position(),
                                    "inventory": player.get_inventory()
                                    }
        # write the saved data to the save file
        with open(f"saves/gameslot_{game_slot}_players.json", "w", encoding="utf-8") as writer:
            writer.write(json.dumps(player_data, indent=4))

    def save_map(self, game_slot):
        "saves the contents of the map"
        map_data: dict = {}
        with self._map_lock:
            for room_id, room in self._map.items():
                map_data[room_id] = {"room_north_id": room.get_north_id(),
                                     "room_east_id": room.get_east_id(),
                                     "room_south_id": room.get_south_id(),
                                     "room_west_id": room.get_west_id(),
                                     "content": room.get_content()
                                     }
        with open(f"saves/gameslot_{game_slot}_map.json", "w", encoding="utf-8") as writer:
            writer.write(json.dumps(map_data, indent=4))

if __name__ == "__main__":
    gs = GameState("tres117p")