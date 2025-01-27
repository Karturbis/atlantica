import socket
import pickle
from _thread import start_new_thread

class Server():

    def __init__(self, thread_data, init_callable, local: bool=True, port = 27300):
        self.__active_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__thread_data = thread_data
        self.__init_callable = init_callable
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
            print(f"Connected to client {addr} as client {connection_counter}:")
            self.__thread_data.callable_methods[connection_counter] = self.__init_callable(conn, connection_counter).main
            start_new_thread(self.threaded_client, (conn, connection_counter))

    def threaded_client(self, connection, connection_id):
        connection.sendall(
            pickle.dumps(NetworkPacket(packet_type="hello", data="hello"))
            )
        callable_method = self.__thread_data.callable_methods[connection_id]
        while True:
            try:
                data = pickle.loads(connection.recv(2048))
            except EOFError as e:
                print(f"Error pickle.loads data: {e}")
                break
            reply = None
            if not data:
                print("Disconnected")
                break
            elif data.packet_type == "command":
                command: str = data.command_name
                reply = callable_method(command, data.command_attributes)
            elif data.packet_type == "reply":
                print(data.data)
                continue
            reply_packaged = NetworkPacket(data=reply, packet_type="reply")
            try:
                connection.sendall(pickle.dumps(reply_packaged))
            except socket.error as e:
                print(f"ERROR: {e}")
                break
        print(f"Lost connection to client {connection_id}")
        self.__thread_data.callable_methods.pop(connection_id)
        connection.close()

    def quit_connection(self, connection):
        connection.close()

    def send_packet(self, packet, connection):
        try:
            connection.sendall(pickle.dumps(packet))
            return pickle.loads(connection.recv(2048))
        except socket.error as e:
            print(f"Error sending packet: {e}")


class Client():

    def __init__(self, callable_method, server_ip = "127.0.0.1", port = 27300):
        self.active_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__callable = callable_method
        self.__server_ip = server_ip
        self.__port = port
        self.__con_info = self.connect()

    def connect(self):
        try:
            self.active_socket.connect((self.__server_ip, self.__port))
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
        get_user_input: bool = True
        back_reply = None
        while True:
            try:
                if get_user_input:
                    command, args = self.__callable("user_input_get_command")
                    reply = self._send(NetworkPacket(
                        packet_type="command",
                        command_name=command,
                        command_attributes=args,
                        )
                        )
                else:
                    get_user_input = True
                    reply = self._send(NetworkPacket(
                        packet_type="reply",
                        data=back_reply,    
                        )
                        )
                if reply.packet_type == "command":
                    back_reply = self.__callable(
                        reply.command_name,
                        reply.command_attributes
                        )
                    get_user_input = False
                elif reply.packet_type == "reply":
                    if reply.data == "end_of_command":
                        print("DEBUG: EOC")
                        continue
                    # else:
                    print(reply.data)

            except socket.error as e:
                print(f"ERROR: {e}")
                break


class ThreadData():

    def __init__(self):
        self.threads = {}
        self.callable_methods = {}


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
