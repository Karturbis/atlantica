import socket
import logging
import json
import threading

from handler import Parser
from game_state import GameState

# configure logging:
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logging.basicConfig(level=logging.DEBUG, filename="logs/server.log", filemode="w",
                    format="%(asctime)s - %(levelname)s: %(message)s")

class Server():

    def __init__(self):
        # initialize variables:
        self._clients: dict = {}
        self._clients_lock = threading.Lock()
        self._game_state = GameState()
        self._client_executable: dict = {
                                        # user executable:
                                        "help": self.help,
                                        "ping": self.ping,
                                        # admin only:
                                        "/quit_game": self.quit_game,
                                        }
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
        exit(0)

    def _main(self):
        """Accept incoming connections and create new
        threads for them, so they can be used in parallel."""
        while True:
            try:
                connection, address = self._active_socket.accept()
                logger.info("Connecting to client with address %s", address)
                # start a new thread for the connected client:
                t = threading.Thread(target=self.threaded_client, args=[connection])
                t.daemon = True  # daemonize thread so it ends, when main thread ends
                t.start()
            except KeyboardInterrupt:
                self._exit_event.set()

    def execute_command(self, command: list, player_name: str) -> str:
        """Executes the given command and returns the result."""
        # get the command object, so parser stage three can be called.
        command_obj_stage_two = self._parser.stage_two(command)
        # get the method that has to be executed:
        command_obj_final = self._parser.stage_three(command_obj_stage_two, player_name)
        # execute the verb and return the result, which is a string.
        return command_obj_final()

    def receive_message(self, connection) -> list:
        """Return the incoming message as a list"""
        incoming: str = connection.recv(2048)
        if not incoming:  # the client has disconnected
            return None
        # no else required
        return json.loads(incoming)

    def send_data(self, connection, data:list) -> None:
        """Send the given data to the client."""
        connection.sendall(json.dumps(data).encode("utf-8"))

    def client_print(self, connection, message: str) -> None:
        """Send the given message to the client."""
        self.send_data(connection, ["s_print", message])

    def broadcast_print(self, message: str):
        """Sends the given message to all connected clients."""
        logger.info("Sending broadcast message: %s", message)
        with self._clients_lock:
            for connection in self._clients.values():
                self.client_print(connection, message)

    def threaded_client(self, connection) -> None:
        """Game loop for each client"""
        self.client_print(connection, "Connecting to server ...")
        # receive a message, which is a list containing only the client name.
        client_name: str = self.receive_message(connection)[0]
        logger.info("Client %s is connecting", client_name)
        # prevent racing conditions when writing to a class variable:
        with self._clients_lock:
            if client_name in self._clients:
                self.client_print(connection, f"The user {client_name} is already connected.")
                logger.warning("Client %s is already connected.", client_name)
                # quitting the thread:
                connection.close()
                return None
            self._clients[client_name] = connection
        self.client_print(connection, "Successfully connected to the server")
        logger.info("Client %s connected successfully", client_name)
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
                result = self._client_executable[command[0]](client_name, *command[1:])
            else:  # execute the verb the user wants to execute
                result = self.execute_command(command, client_name)
            self.client_print(connection, result)
        connection.close()
        return None
        # thread dies

#############################
# Client executable methods #
#############################

    def help(self, *args) -> str:
        return "Server side help is not implemented jetsecond line test"

    def ping(self, *args) -> str:
        return "pong"

############################
# Admin executable methods #
############################

    def quit_game(self, *args) -> None:
        """Disconnect from all clients and terminate the
        server program"""
        self._exit_event.set()

if __name__ == "__main__":
    srv = Server()
    srv.main()
