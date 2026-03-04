"""This is the client of atlantica, this programm
provides the user with an interface to the server, where
the relevant parts of the Game happen."""

# standard imports:
import socket
from threading import Thread
import json

# local imports:
from handler import TerminalHandler

class Client():

    def __init__(self):
        # activate the terminal handler:
        self._terminal_handler = TerminalHandler()
        self._print = self._terminal_handler.new_print
        self._input = self._terminal_handler.new_input
        # load client data:
        self._aliases = self.load_dict("parser/aliases")
        self._name = self.load_string("user_data/name")
        self._user_side_methods: dict = {
                                        "connect": self.connect_to_server,
                                        "set_name": self.set_name,
                                        "clear": self.clear,
                                        "quit": self.quit_game,
                                        "help": self.help,
                                        }
        with open("game_data/help.json", "r", encoding="utf-8") as reader:
            self._help_dict: dict = json.loads(reader.read())
        # network stuff:
        self._active_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # set localhost as standard server:
        self._server_ip: str = "127.0.0.1"
        self._server_port: int = 27300
        self._is_connected_to_server: bool = False

    def main_offline(self):
        """Main method, if not connected to a
        server. Take user input, parse it and
        execute commands."""
        while not self._is_connected_to_server:
            command_stage_one: list = self.get_user_input()
            if command_stage_one[0] in self._user_side_methods:
                if len(command_stage_one) > 1:
                    if command_stage_one[1] == "help" or command_stage_one[1] == "?":
                        self.help(command_stage_one[0])
                else:
                    # call the method in element 0 of the list with other list elements as args:
                    self._user_side_methods[command_stage_one[0]](*command_stage_one[1:])
            else:
                self._print(f"There is no command {command_stage_one[0]}")

    def main_online(self):
        """Main method if connected to a
        server. Take user input, check for
        local executable commands and send the
        rest to the server."""
        prompt = f"{self._name}@{self._server_ip}$>"
        while self._is_connected_to_server:
            command_stage_one: list = self.get_user_input(prompt)
            if command_stage_one[0] in self._user_side_methods:
                # call the method in element 0 of the list with other list elements as args:
                self._user_side_methods[command_stage_one[0]](*command_stage_one[1:])
            else:
                self.send(command_stage_one)

    def get_user_input(self, prompt: str = "$>") -> list:
        """Asks the user for an input, until the user
        enters one. Then returns the input."""
        user_input = None
        while not user_input:
            user_input = self._input(prompt)
        return self.parser_stage_one(user_input)

    def parser_stage_one(self, input_str:str) -> list :
        """Convert the input string into a list of words"""
        # replace aliases with their values:
        for key, value in self._aliases.items():
            input_str = input_str.replace(key, value)
        # convert string into list of lower case words:
        return input_str.lower().split()

    def load_string(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as reader:
            return reader.readline()

    def dump_string(self, file_path: str, data: str) -> None:
        with open(file_path, "w", encoding="utf-8") as writer:
            writer.write(data)

    def load_dict(self, file_path: str) -> dict:
        """Loads the a dict from the given file
        and returning them as a dict."""
        seperator: str = ":"
        start_comment: str = "#"
        with open(file_path, "r", encoding="utf-8") as reader:
            lines: list = reader.readlines()
            return_dict: dict = {}
            for line in lines:
                if not line.startswith(start_comment):
                    line = line.strip("\n").split(seperator)
                    return_dict[line[0]] = line[1]
            return return_dict

####################
# Network methods: #
####################

    def send(self, data: list) -> None:
        """Sending data to the server"""
        self._active_socket.sendall(bytes(data))


############################
# user executable methods: #
############################

    def connect_to_server(self, ip: str = None, port: int = None):
        if not ip:
            ip = self._server_ip
        else:
            self._server_ip = ip
        if not port:
            port = self._server_port
        try:
            # connect to the server:
            self._active_socket.connect((ip, port))
        except socket.error as e:
            self._print(f"Failed to connect to the server: {e}")

    def set_name(self, new_name=None):
        if not new_name:
            self.help("set_name")
            return
        self._name = new_name
        self.dump_string("user_data/name", new_name)
        self._print(f"Changed name to {self._name}.")

    def clear(self):
        self._terminal_handler.clear_screen()

    def quit_game(self):
        if self._is_connected_to_server:
            # TODO implement server quiting
            pass
        self._terminal_handler.quit_terminal_handler()
        exit(0)

    def help(self, func_name = None):
        if not func_name:
            # add all local methods, because they are always available:
            available_methods_help: dict = {key:value for key, value in self._user_side_methods.items()}
            # add help strings to the dict
            for key in available_methods_help:
                available_methods_help[key] = self._help_dict["short"][key]
            # bring dict into alphabetical order
            available_methods_help = dict(sorted(available_methods_help.items()))
            # print the help
            for command, explanation in available_methods_help.items():
                self._print(f"{command} - {explanation}")
            # execute a server side help
            if self._is_connected_to_server:
                self.send([help])
        else:
            try:
                self._print(self._help_dict["long"][func_name])
            except KeyError:
                self._print(f"There is no help entry for {func_name}")


if __name__ == "__main__":

    client = Client()
    client.main_offline()
