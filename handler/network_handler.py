import socket
from queue import Queue
import pickle
from threading import Thread

class NetworkServer():
    """Used to create the server side of
    the client-server model in atlantica."""

    def __init__(
        self, thread_data, init_callable, game_file_path: str,
        local: bool=True, port = 27300
        ):
        self.__game_file_path = game_file_path
        # for thread handling:
        self.__thread_data = thread_data
        self.__init_callable = init_callable
        # initialize socket:
        self.__active_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if local:
            self.__ip = "127.0.0.1"
        else:
            self.__ip = NetworkHandler.get_ip()
        try:
            self.__active_socket.bind((self.__ip, port))
        except socket.error as e:
            print(f"ERROR: {e}")
        # start server:
        self.__active_socket.listen()
        print(f"Server Started with ip {self.__ip} on port {port}\nwaiting for connections...")

    def main(self):
        """Main loop of the Server,
        accepts all incoming connections
        and create a thread for each of them."""
        connection_counter = 0
        while True:
            connection_counter += 1
            conn, addr = self.__active_socket.accept()  # accept connection
            print(f"Connected to client {addr} as client {connection_counter}:")
            # start new client thread for the just established connection:
            self.__thread_data.callable_methods[connection_counter] = self.__init_callable(
                conn, connection_counter, self.__thread_data
                ).execute_cmd
            t = Thread(target=self.threaded_client, args=(conn, connection_counter))
            t.daemon = True  # daemonize thread so it ends, when main thread ends
            t.start()

    def threaded_client(self, connection, connection_id):
        """Main loop for the threads. Each thread handles one
        connection."""
        # init the send queue:
        queue = Queue()
        self.__thread_data.send_queues[connection_id] = queue
        # set the callable_method, to be able to execute commands on the server:
        callable_method = self.__thread_data.callable_methods[connection_id]
        # send initial hello:
        server_methods = callable_method("get_server_methods", [])
        npacket = NetworkPacket(packet_type="hello", data=server_methods)
        connection.sendall(pickle.dumps(npacket))
        client_name = pickle.loads(
            connection.recv(2048)
            ).data
        print(client_name)
        print(self.__thread_data.client_names)
        if client_name in self.__thread_data.client_names.values():
            print(f"Client '{client_name}' already joined")
            already_connected_message = f"'{client_name}' is already connected to the server, please use another name."
            quit_packet = NetworkPacket(
                packet_type="command", command_name="server_side_quit",
                command_attributes=[already_connected_message]
            )
            self.send_packet(quit_packet, connection_id)
            connection.close()
            self.__thread_data.callable_methods.pop(connection_id)
            return None
        else:
            self.__thread_data.client_names[connection_id] = client_name
            self.send_print_packet(f"Successfully connected to '{self.__ip}'", connection_id)
        print(
            f"Client name is: {client_name}"
            )
        callable_method("init_character_data", [self.__game_file_path])
        # initialize client side TerminalHandler:
        character_data = callable_method("get_character_data")
        connection.sendall(pickle.dumps(NetworkPacket(
            packet_type="command",
            command_name="reset_terminal_handler",
            command_attributes=[
                {k: character_data[k] for k in ["health", "saturation"]},
                {k: character_data[k] for k in ["speed", "strength"]},
                {"level": character_data["level"]}
                ]
            )))
        acknowledged: bool = True
        ack_data: str = None
        while client_name == self.__thread_data.client_names[connection_id] or not queue.empty():  # main loop
            # if the send queue is not empty, send the packets:
            try:
                if acknowledged:
                    if not queue.empty():
                        packet = queue.get()
                        ack_data = packet.packet_type
                        acknowledged = False
                        connection.sendall(pickle.dumps(packet))  # send packet
            except socket.error as e:
                print(f"Error sending packet: {e}")
            try:
                data = pickle.loads(connection.recv(2048))  # receive data
            except EOFError as e:
                print(f"Error pickle.loads data: {e}")
                break
            if not data:  # client has disconnected
                print("Disconnected")
                break
            elif data.packet_type == "command":
                command: str = data.command_name
                # execute the received command:
                callable_method(command, data.command_attributes)
            elif data.packet_type == "reply":
                print(data.data)
            elif data.packet_type == "ack":
                if data.data == ack_data:
                    acknowledged = True
        connection.close()
        # cleanup data of the thread which does not automatically dies with the thread:
        if self.__thread_data.client_names[connection_id] == "disconnected":
            print(f"Client '{client_name}' with connection id '{connection_id}' disconnected.")
        else:
            print(f"Lost connection to client {connection_id}")
            self.__thread_data.client_names[connection_id] = "disconnected"
        self.__thread_data.callable_methods.pop(connection_id)
        # thread dies

    def quit_connection(self, connection):
        """close given connection"""
        connection.close()

    def send_packet(self, packet, connection_id):
        """Put given packet into the queue"""
        self.__thread_data.send_queues[connection_id].put(packet)

    def send_print_packet(self, data:str, connection_id):
        packet = NetworkPacket(
            packet_type="command", command_name="client_print",
            command_attributes=[str(data)]
            )
        self.send_packet(packet, connection_id)


class NetworkClient():
    """Used to create the client side of
    the client-server model in atlantica."""

    def __init__(self, server_ip:str="127.0.0.1", port:int=27300):
        # initialize socket:
        self.active_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # server information:
        self.__server_ip = server_ip
        self.__port = port

    def connect(self):
        """connect to server"""
        try:
            self.active_socket.connect((self.__server_ip, self.__port))  # connect to server
            return pickle.loads(self.active_socket.recv(2048))  # return the server hello
        except socket.error as e:
            print(f"ERROR: {e}")

    def send(self, data):
        """send data to the
        server"""
        try:
            self.active_socket.send(pickle.dumps(data))  # send data
        except socket.error as e:
            print(f"ERROR: {e}")

    def listen(self):
        try:
            data = self.active_socket.recv(2048)
            return pickle.loads(data)
        except socket.error as e:
            print(f"Socket ERROR: {e}")


class ThreadData():
    """Dataclass used to store data,
    which is needed for threads,
    but can not be stored inside
    of them."""

    def __init__(self):
        self.threads = {}
        self.callable_methods = {}
        self.client_names = {}
        self.send_queues = {}


class NetworkHandler():
    """Contains network
    related methods"""

    @classmethod
    def get_ip(cls) -> str:
        """Return the current IP
        adress of the computer."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # doesn't even have to be reachable
            s.connect(('10.254.254.254', 1))
            ip_adress = s.getsockname()[0]
        except socket.error:
            ip_adress = '127.0.0.1'
        finally:
            s.close()
        return ip_adress


class NetworkPacket():
    """Dataclass for packets, which are
    send between client and server."""

    def __init__(
        self,
        data = None,
        command_name: str = None,
        command_attributes: list = None,
        packet_type:str = None
        ) -> None:
        self.data = data
        self.command_name: str = command_name
        self.command_attributes: list = command_attributes
        self.packet_type: str = packet_type
        if packet_type == "command" and not command_attributes:
            self.command_attributes = []
