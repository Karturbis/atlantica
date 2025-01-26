from handler import TerminalHandler
from handler import NetworkHandler
from handler import InputHandler

class Client():

    def __init__(self):
        self.__name = "NONE"

    def connect_to_server(self):
        print("cts")
    def start_server(self):
        pass
    def single_player(self):
        pass
    
    def set_name(self, name):
        self.__name = name

    def print_help(self, args=None) -> None:
        """Outprints all available commands."""
        print("Available commands:\n")
        for key in input_handler.get_commands_avail():
            print(key)
        print()

client = Client()
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