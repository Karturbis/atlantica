import socket
import pickle

class NetworkHandler:
    
    def __init__(self):
        self.aktive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _get_ip(self) -> str:
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

    def init_server(self, multiplayer: bool = True, port: int = 27300):
        # set ip adresss:
        if multiplayer:
            server_ip = self._get_ip()
        else:
            server_ip: str = "127.0.0.1"
        # bind socket:
        try:
            self.aktive_socket.bind((server_ip, port))
        except socket.error as e:
            str(e)
        self.aktive_socket.listen()
        print(f"Server started on port {port} with ip {server_ip}")
    
    def init_client(self, server_ip, server_port):
        try:
            addr = (server_ip, server_port)
            self.aktive_socket.connect(addr)
            return pickle.loads(self.aktive_socket.recv(2048))
        except Exception as e:
            print(f"ERROR in NetworkHandler.init_client():\n{e}")
   
    def listen_for_connections(self):
        connection, address = self.aktive_socket.accept()
        print("Connected to:", address)
        return connection

    def send_data(self, data, connection = None):
        if not connection:
            connection = self.aktive_socket
        try:
            connection.sendall(pickle.dumps(data))
            return pickle.loads(connection.recv(2048))
        except socket.error as e:
            print(e)
    
    def receive_data(self, connection):
        # command classfor listen command is not known, NEEDS FIX!!
        return self.send_data(
            NetworkPacket(string_data="LISTEN", packet_class="network_command"),
            connection
            )

    def send_command(
        self,
        connection,
        command_name,
        command_attributes = None,
        ):
        if not command_attributes:
            command_attributes = []
        command_packet = NetworkPacket(
            command_name=command_name,
            command_attributes=command_attributes,
            packet_class="command"
            )
        self.send_data(connection, command_packet)

class NetworkPacket():

    def __init__(
        self,
        string_data:str = None,
        command_name: str = None,
        command_attributes: list = None,
        packet_class:str = None
        ) -> None:
        self.string_data: str = string_data
        self.command_name: str = command_name
        self.command_attributes: list = command_attributes
        self.packet_class: str = packet_class

if __name__ == "__main__":
    nh = NetworkHandler()
    nh.init_client("192.168.178.45", 27300)