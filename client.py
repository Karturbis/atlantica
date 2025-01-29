# standart imports:
from ast import literal_eval  # Used to evaluate a boolean from a string
from os.path import exists  # Checks if given file exists. Used to prevent errors.
from os import listdir  # To list all files of a directory, used in Main.load_game()
from os import remove  # To remove files
import shutil  # Used copy the content.sqlite file into a newfrom os import system gameslot

# handler imports:
from handler import DatabaseHandler
from handler import network_handler
from handler import TerminalHandler

# local imports:
import client_methods


class Client():

    def __init__(self):
        self.__client_methods = client_methods.Client_Methods()
        self.__local_methods: dict = {
            "menu": ["clear", "new_game", "load_game", "delete_game", "quit"],
            "ingame": ["clear"],
        }
        self.__database_handler = DatabaseHandler()

    def connect_to_server(self, server_ip: str, server_port:int=27300):
        client = network_handler.NetworkClient(self.__client_methods.execute_cmd, server_ip, server_port)
        client.main()

    def input_loop(self, mode: str, prompt:str = None):
        if not prompt:
            prompt = f"{mode}$>"
        while True:
            user_input = self.__client_methods.user_input_get_command(prompt)
            if user_input[0] in self.__local_methods[mode]:
                self.__client_methods.execute_cmd(user_input[0], user_input[1:])
            else:
                TerminalHandler.new_print(f"There is no command '{user_input[0]}'")

    def menu(self):
        self.input_loop("menu")


TerminalHandler.init(
    {"": ""},
    {"": ""},
    {"": ""}
)

cliennt = Client()
cliennt.menu()