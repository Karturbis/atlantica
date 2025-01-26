import socket

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
    def send_data(cls, connection, data:str):
        try:
            connection.sendall(str.encode(data))
            return connection.recv(2048).decode()
        except socket.error as e:
            print(e)


    @classmethod
    def receive_data(cls, connection):
        try:
            return connection.recv(2048).decode()
        except socket.error as e:
            print(e)


