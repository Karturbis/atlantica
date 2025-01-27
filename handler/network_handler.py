import socket
import pickle
from _thread import start_new_thread

class Server():

    def __init__(self, callable_method, local: bool=True, port = 27300):
        self.__active_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__callable = callable_method
        if local:
            ip = "127.0.0.1"
        else:
            ip = NetworkHandler.get_ip()
        try:
            self.__active_socket.bind((ip, port))
        except socket.error as e:
            print(f"ERROR: {e}")
        self.__active_socket.listen()
        print(f"Server Started with ip {ip} on port {port}\nwaiting for connections...")

    def main(self):
        connection_counter = 0
        while True:
            connection_counter += 1
            conn, addr = self.__active_socket.accept()
            print("Connected to:", addr)
            start_new_thread(self.threaded_client, (conn, connection_counter))

    def threaded_client(self, connection, connection_id):
        connection.sendall(
            pickle.dumps(NetworkPacket(packet_type="hello", data="hello"))
            )
        while True:
            try:
                data = pickle.loads(connection.recv(2048))
                reply = None
                if not data:
                    print("Disconnected")
                    break
                elif data.packet_type == "command":
                    command: str = data.command_name
                    reply = self.__callable(command)
                elif data.packet_type == "print":
                    print(data.data)
                reply_packaged = NetworkPacket(data=reply, packet_type="reply")
                connection.sendall(pickle.dumps(reply_packaged))
            except Exception as e:
                print(f"ERROR: {e}")
                break
        print("Lost connection")
        connection.close()


class Client():

    def __init__(self, server_ip = "127.0.0.1", port = 27300):
        self.active_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = server_ip
        self.port = port
        self.con_info = self.connect()

    def connect(self):
        try:
            self.active_socket.connect((self.server_ip, self.port))
            return type(pickle.loads(self.active_socket.recv(2048)))
        except socket.error as e:
            print(f"ERROR: {e}")

    def _send(self, data):
        try:
            self.active_socket.send(pickle.dumps(data))
            return pickle.loads(self.active_socket.recv(2048))
        except socket.error as e:
            print(f"ERROR: {e}")
    
    def main(self):
        


class NetworkHandler():

    @classmethod
    def get_ip(cls) -> str:
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

    def __init__(
        self,
        data:str = None,
        command_name: str = None,
        command_attributes: list = None,
        packet_type:str = None
        ) -> None:
        self.data: str = data
        self.command_name: str = command_name
        self.command_attributes: list = command_attributes
        self.packet_type: str = packet_type
        if packet_type == "command" and not command_attributes:
            self.command_attributes = []
