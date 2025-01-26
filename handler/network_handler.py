import socket
import pickle

class NetworkHandler:
    connections: list = []
    server_key = "SERVERKEY:qwerty"

    @classmethod
    def _get_ip(cls) -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # doesn't even have to be reachable
            s.connect(('10.254.254.254', 1))
            ip_adress = s.getsockname()[0]
        except Exception:
            ip_adress = '127.0.0.1'
        finally:
            s.close()
        return ip_adress

    @classmethod
    def init_server(cls, multiplayer: bool = False, port: int = 27300):

        # set ip adresss:
        if multiplayer:
            server = NetworkHandler._get_ip()
        else:
            server: str = "127.0.0.1"
        # initialize socket:
        cls.aktive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind socket:
        try:
            cls.aktive_socket.bind((server, port))
        except socket.error as e:
            str(e)
        cls.aktive_socket.listen()
        print(f"Server started on port {port}!")

    @classmethod
    def listen_for_connections(cls):
        connection, address = cls.aktive_socket.accept()
        print("Connected to:", address)
        return connection

    @classmethod
    def send_data(cls, connection, data):
        try:
            connection.sendall(pickle.dumps(data))
            return pickle.loads(connection.recv(2048))
        except socket.error as e:
            print(e)

    @classmethod
    def receive_data(cls, connection):
        # command classfor listen command is not known, NEEDS FIX!!
        return NetworkHandler.send_data(connection, CommandPacket("LISTEN", []))

    @classmethod
    def send_command(cls, connection, command_name, command_attributes = None, command_class = None):
        if not command_attributes:
            command_attributes = []
        command_packet = CommandPacket(command_name, command_attributes, command_class)
        NetworkHandler.send_data(connection, command_packet)

class CommandPacket():

    def __init__(self, command_name: str, command_attributes: list,  command_class:str = None) -> None:
        self.command_class: str = command_class
        self.command_name: str = command_name
        self.command_attributes: list = command_attributes