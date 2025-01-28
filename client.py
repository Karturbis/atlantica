from handler import network_handler
from handler import TerminalHandler

import client_methods


class Client():

    def __init__(self):
        self.__client_methods = client_methods.Client_Methods()
        self.__local_methods: dict = {
            "menu": ["clear", "newgame", "loadgame", "safegame", "quit"],
            "ingame": ["clear"],
        }

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

    def menu(self):
        self.input_loop("menu")

TerminalHandler.init(
    {"test": "teste"},
    {"mitte": "mitte"},
    {"ende": "ende"}
)

cliennt = Client()
cliennt.menu()