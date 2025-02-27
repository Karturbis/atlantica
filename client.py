# standart imports:
from os.path import exists  # Checks if given file exists. Used to prevent errors.
from os import listdir  # To list all files of a directory, used in Main.load_game()
from os import remove  # To remove files
from os import system
import shutil  # Used copy the content.sqlite file into a newfrom os import system gameslot
from sys import exit
from threading import Thread
from pygame.base import quit as pg_quit

# handler imports:
from handler import DatabaseHandler
from handler import network_handler
from handler import GuiHandler


class Client():

    def __init__(self, gui_handler):
        self.__gui_handler = gui_handler
        self.__local_methods: dict = {
            "menu": [
                "clear", "new_game", "load_game", "delete_game",
                "quit_game", "join_server", "set_name", "start_server",
                "add_alias", "print_help", "print_alias"
                ],
            "ingame": ["clear", "quit_game", "print_help",],
        }
        self.__server_methods: dict = {}
        self.__alias_file: str = "client.alias"
        self.__aliases: dict = self.load_aliases()
        self.__database_handler = DatabaseHandler()
        self.__network_client = None
        self.__network_client_thread = None
        self.name: str = "test"
        self.__prompt: str = "input$>"
        self.__mode: str = "menu"
        self.__help_data: dict[dict] = {
            "menu": {
                "clear": "clears the screen",
                "new_game": "creates a new gameslot",
                "load_game": "loads a gameslot",
                "delete_game": "deletes a gameslot",
                "quit_game": "save and quit the game",
                "join_server": "join a server",
                "set_name": "set the character name",
                "start_server": "start a server",
                "add_alias": "add a new alias for a command",
                "print_alias": "print all aliases",
                "print_help": "print all available commands",
                },
            "ingame": {}
        }

    def user_input_loop(self, mode: str = None, prompt:str = None) -> None:
        """takes input from user and executes the
        corresponding commands"""
        if prompt:
            self.__prompt = prompt
        else:
            self.__prompt = f"{mode}$>"
        if mode:
            self.__mode = mode
        while True:
            user_input: list = self.__gui_handler.new_input(self.__prompt).strip(" ").split(" ")
            if user_input[0] in self.__aliases:
                try:
                    user_input = [self.__aliases[user_input[0]], user_input[1:]]
                except IndexError:
                    user_input = [self.__aliases[user_input[0]], []]
            else:
                user_input = [user_input[0], user_input[1:]]
            if user_input[0] in self.__local_methods[self.__mode]:
                if user_input[1:] != []:  # check if list has at least one item
                    self.execute_cmd_client(user_input[0], user_input[1])
                else:
                    self.execute_cmd_client(user_input[0])
            elif user_input[0] in self.__server_methods:
                if user_input[1:] != []:  # check if list has at least one item
                    self.execute_cmd_server(user_input[0], user_input[1])
                else:
                    self.execute_cmd_server(user_input[0])
            else:
                self.__gui_handler.new_print(f"There is no command '{user_input[0]}'")

    def threaded_server_listen_loop(self) -> None:
        while self.__mode == "ingame":
            data = self.__network_client.listen()
            self.send_ack_packet(data)
            if data.packet_type == "command":
                self.execute_cmd_client(data.command_name, data.command_attributes)
            elif data.packet_type == "reply":
                self.__gui_handler.new_print(data.data)

    def execute_cmd_server(self, command: str, args: list=None) -> None:
        print(f"start executing command {command}")
        print(f"with args {args}")
        if not args:
            args: list = []
        try:
            # send command:
            self.__network_client.send(network_handler.NetworkPacket(
                packet_type="command",
                command_name=command,
                command_attributes=args,
                )
                )
        except Exception as e:
            self.__gui_handler.new_print(f"ERROR: {e}")

    def execute_cmd_client(self, command: str, args: list=None):
        """Takes a command, and arguments. Executes the command
        with the given arguments, if possible."""
        print(f"cmd: {command} args:{args}")
        if not args:
            args = []
        try:
            func = getattr(self, command)
        except AttributeError:
            self.__gui_handler.new_print(f"There is no command called {command}")
        given_args_len = len(args)
        # get number of keyword args:
        if func.__defaults__:
            kwargs = len(func.__defaults__)
        else:
            kwargs = 0
        # subtract kwargs from all args to get positional args
        expected_args_len = func.__code__.co_argcount - kwargs -1  # -1 otherwise self counts as an arg
        if given_args_len >= 1:
            if expected_args_len == given_args_len or expected_args_len + kwargs >= given_args_len:
                # run method:
                try:
                    return func(*args)
                except Exception as e:
                    self.__gui_handler.new_print(f"ERROR in Client.execute_cmd_client: {e}")
            elif expected_args_len == 0 and given_args_len != 0:
                return func()
            else: # wrong number of arguments were given
                self.__gui_handler.new_print(f"Command {command} takes {expected_args_len} arguments, you gave {given_args_len}.")
        else:  # no args where given:
            if expected_args_len == given_args_len:
                # run method:
                try:
                    return func()
                except Exception as e:
                    self.__gui_handler.new_print(f"ERROR in Client.execute_cmd_client: {e}")
            else: # wrong number of arguments were given
                self.__gui_handler.new_print(f"Command {command} takes {expected_args_len} arguments, you gave {given_args_len}.")

    def send_ack_packet(self, packet) -> None:
        print(f"sending ack: {packet.packet_type}")
        self.__network_client.send(network_handler.NetworkPacket(
            packet_type="ack", data=packet.packet_type
        )
        )

    def load_aliases(self) -> dict:
        """Load aliases from File"""
        with open(self.__alias_file, "r", encoding="utf-8") as reader:
            lines = reader.readlines()
            aliases = {}
            for line in lines:
                if not line.startswith("#"):  # make comments with '#' in aliases.als
                    line = line.strip("\n").split(" ")
                    aliases[line[0]] = line[1]
        return aliases

    def server_side_quit(self, message:str) -> None:
        self.client_print(message)
        self.client_print("The server quit the connection.")
        self.__mode = "menu"
        self.__prompt = "menu$>"

##############################
## user executable commands ##
##############################

    def join_server(self, server_ip: str="127.0.0.1", server_port:int=27300) -> None:
        """Connect to the given server."""
        server_port = 27300
        self.__network_client_thread = Thread(target=self.threaded_server_listen_loop, daemon=True)
        self.__network_client = network_handler.NetworkClient(server_ip, server_port)
        self.__server_methods = self.__network_client.connect().data
        self.__network_client.send(network_handler.NetworkPacket(
            packet_type="hello", data=self.name
        ))
        self.__prompt = f"{self.name}@{server_ip}$>"
        self.__mode = "ingame"
        self.__network_client_thread.start()

    def clear(self) -> None:
        self.__gui_handler.clear()

    def quit_game(self, args=None) -> None:
        """Saves and quits the game."""
        self.execute_cmd_server("save_player")
        pg_quit()  # quit pygame
        exit("Good bye, see you next time in Atlantica!")

    def new_game(self, args=None) -> None:
        """Creates a new game save slot"""
        prompt = "new_game$>"
        game_name = self.__gui_handler.new_input( f"Please input the name of the gameslot {prompt}")
        game_file_path = f"saves/gameslot_{game_name}.sqlite"
        if exists(game_file_path):
            overwrite = self.__gui_handler.new_input(
                f"This gameslot is already occupied, do you want to overwrite? [y/N] {prompt}"
            ).lower()
            if not (overwrite == "y" or overwrite == "yes"):
                return None
        shutil.copyfile("data/game_content.sqlite", game_file_path)
        self.__gui_handler.new_print(
            f"The gameslot: {game_name} was sucessfully created."
        )
        self.__database_handler.set_database(game_file_path)
        return None

    def start_server(self, server_port = 27300, local:bool=False) -> None:
        """Starts a server for the client to connect to."""
        saved_game_files = listdir("saves/")
        if saved_game_files:
            self.__gui_handler.new_print("Pick your option:")
            for index, file_name in enumerate(saved_game_files):
                self.__gui_handler.new_print(
                    f"Option {index +1} is {file_name[9:-7]}"
                )  # prints the name of the gamestate, without printing the whole file name
            try:
                option = int(
                    self.__gui_handler.new_input("Input the number of your option $> ")
                )
            except ValueError:
                self.__gui_handler.new_print(
                    "You have to put in the NUMBER of your gameslot."
                )
                return None
            game_file_path = f"saves/{saved_game_files[option-1]}"
            # start server:
            # NEED TO FIND MEHTOD TO START SERVER, WITHOUT SOTTPING CLIENT!
            system(f"python3 server.py {game_file_path} {local} {server_port} &")
        else:
            self.__gui_handler.new_print("There are no gameslots available, create one with 'new'.")

    def load_game(self):
        self.start_server(local=True)

    def set_name(self, name:str=None):
        if name:
            self.name = name
        else:
            self.name = self.__gui_handler.new_input("set_name$>")
        self.__gui_handler.new_print(f"Name was set to {self.name}.")

    def delete_game(self, args=None) -> None:
        """Delete the given Gameslot."""
        saved_game_files = listdir("saves/")
        if saved_game_files:
            self.__gui_handler.new_print("Pick your option:")
            for index, file_name in enumerate(saved_game_files):
                self.__gui_handler.new_print(
                    f"Option {index +1} is {file_name[9:-7]}"
                )  # prints the name of the gamestate, without printing the whole file name
            option: str = self.__gui_handler.new_input(
                "Input the number of your option. del$>"
            )
            try:
                option: int = int(option)
                gameslot: str = f"{saved_game_files[option-1]}"
            except ValueError:
                gameslot = f"gameslot_{option}.sqlite"
                if not gameslot in saved_game_files:
                    self.__gui_handler.new_print(
                        f"Der Gameslot {gameslot[9:-7]} exisiert nicht."
                    )
                    return None
            consent = self.__gui_handler.new_input(
                f"Bist du dir sicher, dass du Gameslot {gameslot[9:-7]} löschen möchtest? [y/N] del$> "
            ).lower()
            if consent == "y":
                remove(f"saves/{gameslot}")
                self.__gui_handler.new_print(f"Gameslot {gameslot[9:-7]} wurde gelöscht.")
            else:
                self.__gui_handler.new_print("Nichts wurde gelöscht.")

        else:
            self.__gui_handler.new_print("There are no gameslots.")

    def add_alias(self, alias:str, command:str) -> None:
        """add alias to the aliases File"""
        if alias.startswith("#"):
            self.__gui_handler.new_print("Aliases are not allowed to start with '#'")
        else:
            with open(self.__alias_file, "a", encoding="utf-8") as writer:
                writer.write(f"{alias.strip(' ')} {command.strip(' ')}\n")
            self.__aliases = self.load_aliases()

    def print_alias(self) -> None:
        self.client_print("Aliases:")
        for alias, command in self.__aliases.items():
            self.client_print(f"'{alias}' for command '{command}'")

    def print_help(self) -> None:
        self.client_print("Available commands:")
        for command, explanation in self.__help_data[self.__mode].items():
            self.client_print(f"{command}: {explanation}")


########################
## Gui handler stuff: ##
########################

    def client_print(self, data:str):
        self.__gui_handler.new_print(data)

    def set_information_left(self, key, value):
        self.__gui_handler.set_information_left(key, value)

    def set_information_center(self, key, value):
        self.__gui_handler.set_information_center(key, value)

    def set_information_right(self, key, value):
        self.__gui_handler.set_information_right(key, value)

    def reset_terminal_handler(
        self, information_content_left,
        information_content_center,
        information_content_right
    ):
        self.__gui_handler.reset_information()
        for key, value in information_content_left.items():
            self.__gui_handler.set_information_left(key, value)
        for key, value in information_content_center.items():
            self.__gui_handler.set_information_center(key, value)
        for key, value in information_content_right.items():
            self.__gui_handler.set_information_right(key, value)

if __name__ == "__main__":
    gui_handler = GuiHandler()  # init gui handler
    client = Client(gui_handler)  # init client
    # main loop
    client.user_input_loop("menu")

