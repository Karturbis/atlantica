import socket
import logging
import threading

import parser

# configure logging:
logging.basicConfig(level=logging.DEBUG, filename="logs/server.log",
                    filemode="w", format="%(asctime)s - %(levelname)s in %(threadname)s: %(message)s")

class Server():

    def __init__(self):
        # initialize variables:
        self.__clients: list[str] = []
        self.__clients_lock = threading.Lock()
        # network configuration
        ip = "0.0.0.0"
        port = "27300"
        # socket initialization
        self.__active_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.__active_socket.bind((ip, port))
        except socket.error:
            logging.exception(f"failed binding socket")
            try:
                logging.info("Trying another port")
                port +=1
                self.__active_socket.bind((ip, port))
            except socket.error:
                logging.exception(f"failed binding socket")
                exit("Server could not start correctly")
        # start the server
        self.__active_socket.listen()
        print(f"LOG: Server started on port {port}")

    def main(self):
        """Accept incoming connections and create new
        threads for them, so they can be used in parallel."""
        while True:
            connection, address = self.__active_socket.accept()
            logging.info(f"Connecting to client with address {address}")
            # start a new thread for the connected client:
            t = threading.Thread(target=self.threaded_client, args=connection)
            t.daemon = True  # daemonize thread so it ends, when main thread ends
            t.start()

    def execute_command(self, command: list) -> str:
        parser.stage_two(command)

    def receive_message(self, connection) -> list:
        """Return the incoming message as a list"""
        incoming: str = connection.receive(2048)
        if not incoming:  # the client has disconnected
            return None
        # no else rewuired
        return incoming.split(":")

    def send_message(self, connection, message) -> None:
        """Send the given message to the client."""
        connection.sendall(message)


    def threaded_client(self, connection) -> None:
        self.send_message(connection, "Connected to server.")
        # receive a message, which is a list containing only the client name.
        client_name: str = self.receive_message(connection)[0]
        if client_name in self.__clients:
            self.send_message(connection, f"The user {client_name} is already connected.")
            logging.info(f"Client {client_name} is already connected.")
            # quitting the thread:
            return None
        # no else required
        # prevent racing conditions when writing to a class variable:
        with self.__clients_lock:
            self.__clients.append(client_name)
        while True:
            command: list = self.receive_message(connection)
            if not command:  # client disconnected
                logging.info(f"Client {client_name} disconnected")
                break
            # no else required
            # execute the command and send the output to the client:
            self.send_message(connection, self.execute_command(command))
        connection.close()
        # thread dies
