import socket
import logging
import json
import threading
from pathlib import Path

from handler import Parser
from game_state import GameState
from game_classes import Player

# configure logging:
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logging.basicConfig(
    level=logging.DEBUG, filename="logs/server.log", filemode="w",
    format="%(asctime)s [%(filename)s:%(levelname)s] > %(message)s")

class Server():

    def __init__(self, game_slot:str):
        # initialize variables:
        self._clients: dict = {}
        self._clients_lock = threading.Lock()
        self._game_slot = game_slot
        self._game_state = GameState(self._game_slot)
        self._client_executable: dict = {
                                        # user executable:
                                        "help": self.help,
                                        # admin only:
                                        "/quit_game": self.quit_game,
                                        "/save_game": self.save_game,
                                        "/list_saves": self.list_saves,
                                        "/save_to_new_slot": self.save_to_new_slot,
                                        "/new_slot": self.new_slot,
                                        "/remove_slot": self.remove_slot,
                                        }
        self._verb_executable: dict = {
                                    "client_print": self.client_print,
                                    "room_print": self.room_print,
                                    "broadcast_print": self.broadcast_print,      }
        self._exit_event = threading.Event()
        # initialize parser:
        self._parser = Parser(self._game_state)
        # network configuration
        ip: str = "0.0.0.0"
        port: int = 27300
        # socket initialization
        self._active_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._active_socket.bind((ip, port))
        except socket.error:
            logger.exception("Failed binding socket")
            try:
                logger.info("Trying another port")
                port +=1
                self._active_socket.bind((ip, port))
            except socket.error:
                logger.exception("failed binding socket")
                exit("Server could not start correctly")
        # start the server
        self._active_socket.listen()
        logger.info("Server started on port %u", port)

    def main(self):
        """wrapper for the main method, so that
        terminating the program is possible"""
        main_thread = threading.Thread(target=self._main)
        main_thread.daemon = True
        main_thread.start()
        # quitting the server if exit event is omitted
        self._exit_event.wait()
        self.broadcast_print("The server is shutting down")
        self.broadcast_print(self.save_game()["client_print"])
        exit(0)

    def _main(self):
        """Accept incoming connections and create new
        threads for them, so they can be used in parallel."""
        while True:
            try:
                connection, address = self._active_socket.accept()
                logger.info("Connecting to client with address %s", address)
                # start a new thread for the connected client:
                t = threading.Thread(
                    target=self.threaded_client, args=[connection]
                    )
                t.daemon = True  # daemonize thread so it ends, when main thread ends
                t.start()
            except KeyboardInterrupt:
                self._exit_event.set()

    def execute_command(self, command: list, player_name: str) -> str:
        """Executes the given command and returns the result."""
        player = self._game_state.get_player_by_name(player_name)
        # get the command object, so parser stage three can be called.
        command_obj_stage_two = self._parser.stage_two(command)
        # execute the command in the player class.
        result = player.execute_command(command_obj_stage_two, self._game_state)
        logger.debug(f"result from verb execution: {result}")
        return result

    def receive_message(self, connection) -> list:
        """Return the incoming message as a list"""
        incoming: str = connection.recv(2048)
        if not incoming:  # the client has disconnected
            return None
        return json.loads(incoming)

    def send_data(self, connection, data:list) -> None:
        """Send the given data to the client."""
        connection.sendall(json.dumps(data).encode("utf-8"))

    def client_print(self, message:str, **kwargs) -> None:
        """Send the given message to the client."""
        connection = kwargs["connection"]
        self.send_data(connection, ["s_print", message])

    def broadcast_print(self, message:str, **kwargs) -> None:
        """Sends the given message to all connected clients."""
        client_connection = kwargs.get("connection")
        logger.info("Sending broadcast message: %s", message)
        with self._clients_lock:
            for connection in self._clients.values():
                if not connection == client_connection:
                    self.client_print(message, connection = connection)

    def room_print(self, message:str, **kwargs) -> None:
        """Sends the given message to all clients, that
        are in the room"""
        client_connection = kwargs["connection"]
        room_id = kwargs["room_id"]
        sender_name = kwargs["sender_name"]
        logger.info(
                    "Sending room broadcast: %s%s in room %s",
                    message, sender_name, room_id
                    )
        player_names: list[str] = self._game_state.get_room_by_id(room_id).get_players()
        with self._clients_lock:
            for player_name, connection in self._clients.items():
                if player_name in player_names:
                    if not connection == client_connection:
                        self.client_print(f"{sender_name} {message}", connection = connection)

    def threaded_client(self, connection) -> None:
        """Game loop for each client"""
        self.client_print("Connecting to server ...", connection = connection)
        # receive a message, which is a list containing only the client name.
        client_name: str = self.receive_message(connection)[0]
        logger.info("Client %s is connecting", client_name)
        # prevent racing conditions when writing to a class variable:
        with self._clients_lock:
            if client_name in self._clients:
                self.client_print(
                    f"The user {client_name} is already connected.",
                    connection = connection
                )
                logger.warning("Client %s is already connected.", client_name)
                # quitting the thread:
                connection.close()
                return None
            self._clients[client_name] = connection
        if not self._game_state.get_player_by_name(client_name):
            # creating the player object for the new player:
            player = Player(client_name, "start")
            self._game_state.add_player(player)
            logger.info("Created new Player for %s", client_name)
        else:
            self._game_state.load_player(client_name, self._game_slot)
            logger.info("Loaded existing Player object %s", client_name)
        logger.info("Client %s connected successfully", client_name)
        self.broadcast_print(f"{client_name} joined the game", connection = connection)
        self.client_print("Successfully connected to server", connection = connection)
        self.room_print(
                "spawned in the room", connection = connection,
                room_id = self._game_state.get_player_by_name(client_name).get_position(),
                sender_name = client_name
                )
        while True:
            command: list = self.receive_message(connection)
            if not command:  # client disconnected
                with self._clients_lock:
                    self._clients.pop(client_name)
                logger.info("Client %s disconnected", client_name)
                break
            # execute the command and send the output to the client:
            if command[0] in self._client_executable:
                # the user command is not ingame, execute the command
                result: dict = self._client_executable[command[0]](
                    client_name, *command[1:]
                    )
            else:  # execute the verb the user wants to execute
                result: dict = self.execute_command(command, client_name)
            for method, message in result.items():
                self._verb_executable[method](
                    message, connection=connection,
                    room_id = self._game_state.get_player_by_name(client_name).get_position(),
                    sender_name = client_name
                    )
        connection.close()
        return None
        # thread dies

#############################
# Client executable methods #
#############################

    def help(self, *_) -> dict:
        return {"client_print": "Server side help is not implemented jetsecond line test"}

############################
# Admin executable methods #
############################

    def quit_game(self, *_) -> None:
        """Disconnect from all clients and terminate the
        server program"""
        self._exit_event.set()

    def save_game(self, *_) -> dict:
        self._game_state.save_game(self._game_slot)
        with open("saves/current", "w", encoding="utf-8") as writer:
            writer.write(self._game_slot)
        return {"client_print": "the game was saved"}

    def save_to_new_slot(self, player_name, slot_name:str = "", *_) -> dict:
        if not slot_name:
            return {"client_print": "you have to specify a slot name"}
        self._game_slot = slot_name
        self.save_game()
        return {"client_print": f"the game was saved to slot {slot_name}"}

    def new_slot(self, player_name, slot_name:str = "", *_) -> dict:
        if not slot_name:
            return {"client_print": "you have to specify a slot name"}
        self._game_slot = slot_name
        players: dict = self._game_state.get_players()
        self._game_state = GameState(self._game_slot)
        for player_name in players:
            self._game_state.add_player(Player(player_name, "start"))
        self.save_game()
        return {"client_print": f"the game slot {slot_name} has been created"}

    def remove_slot(self, player_name, slot_name:str = "", *_) -> dict:
        if not slot_name:
            return {"client_print": "you have to specify a slot name"}
        if slot_name == self._game_slot:
            return {
                "client_print":
                f"the game slot {slot_name} has not been removed, because it is currently in use"
            }
        path = Path(f"saves/{slot_name}")
        if not path.is_dir():
            return {"client_print": f"there is no game slot {slot_name}"}
        for file in path.iterdir():
            file.unlink()
        path.rmdir()
        logger.info("deleted game slot %s", slot_name)
        return {"client_print": f"deleted the game slot {slot_name}"}

    def list_saves(self, *_) -> dict:
        slots: dict = self._game_state.get_game_slots_with_time()
        result: str = "Game slots:"
        for slot, time in slots.items():
            if self._game_state.is_game_slot_usable(slot):
                if slot == self._game_slot:
                    result = f"{result}\n{slot} - {time} <-"
                else:
                    result = f"{result}\n{slot} - {time}"
            else:
                result = f"{result}\n{slot} - {time} - INVALID"
        return {"client_print": result}

if __name__ == "__main__":
    game_slot:str = ""
    with open("saves/current", "r", encoding="utf-8") as reader:
        game_slot = reader.read().strip("\n\r")
    if not game_slot:
        game_slot = "test"
    logger.info("Starting server with slot %s", game_slot)
    srv = Server(game_slot)
    srv.main()
