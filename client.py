from handler import TerminalHandler
from handler import NetworkHandler
from handler import InputHandler

class Client():

    def __init__(self):
        self.__name = "NONE"

    def connect_to_server(self):
        server_adress = input("Input the Server you want to join: ").split(":")
        if len(server_adress) > 1:
            server_port = int(server_adress[1])
        else:
            server_port = 27300
        server_ip = server_adress[0]
        connection = network_handler.init_client(server_ip, server_port)



    def start_server(self):
        pass

    def single_player(self):
        pass

    def set_name(self, name=None):
        if not name:
            print("You need to input a name")
        else:
            self.__name = name

    def print_help(self, args=None) -> None:
        """Outprints all available commands."""
        print("Available commands:\n")
        for key in input_handler.get_commands_avail():
            print(key)
        print()

client = Client()
network_handler = NetworkHandler()
input_handler = InputHandler(
    client,
    {
        "clear": ["TerminalHandler", "clear"],
        "singleplayer": ["main", "single_player"],
        "startserver": ["main", "start_server"],
        "joinserver": ["main", "connect_to_server"],
        "help": ["main", "print_help"],
        "setname": ["main", "set_name"],
    })

input_handler.input_loop()
