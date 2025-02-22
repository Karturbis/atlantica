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

    def __init__(self):
        self.__local_methods: dict = {
            "menu": [
                "clear", "new_game", "load_game", "delete_game",
                "quit_game", "join_server", "set_name", "start_server",
                "load_game", "add_alias"
                ],
            "ingame": ["clear", "quit_game"],
        }
        self.__server_methods: dict = {}
        self.__alias_file = "client.alias"
        self.__aliases = self.load_aliases()
        self.__database_handler = DatabaseHandler()
        self.__network_client = None
        self.__network_client_thread = None
        self.name = "test"
        self.__prompt = "input$>"
        self.__mode = "menu"

    def user_input_loop(self, mode: str = None, prompt:str = None):
        """takes input from user and executes the
        corresponding commands"""
        if not prompt:
            self.__prompt = f"{mode}$>"
        else:
            self.__prompt = prompt
        if mode:
            self.__mode = mode
        while True:
            print("uil_start")
            gui_handler.refresh()
            user_input = gui_handler.new_input(self.__prompt).strip(" ").split(" ")
            print("uil_got_input")
            if user_input[0] in self.__aliases:
                user_input = (self.__aliases[user_input[0]], user_input[1:])
            if user_input[0] in self.__local_methods[self.__mode]:
                if user_input[1:] != []:  # check if list has more than one item
                    self.execute_cmd_client(user_input[0], user_input[1:])
                else:
                    self.execute_cmd_client(user_input[0])
            elif user_input[0] in self.__server_methods:
                if user_input[1:] != []:  # check if list has more than one item
                    self.execute_cmd_server(user_input[0], user_input[1:])
                else:
                    self.execute_cmd_server(user_input[0])
            else:
                gui_handler.new_print(f"There is no command '{user_input[0]}'")

    def threaded_server_listen_loop(self):
        gui_handler.new_print("Started threaded server listen loop")
        while True:
            print("tsll_start")
            data = self.__network_client.listen()
            if data.packet_type == "command":
                self.execute_cmd_client(data.command_name, data.command_attributes)
            elif data.packet_type == "reply":
                if not data.data == "end_of_command":
                    print(data)
                    print(data.data)
                    print(type(data.data))
                    gui_handler.new_print(data.data)

    def execute_cmd_server(self, command, args=None):
        if not args:
            args = []
        back_reply = None
        try:
            # send command
            self.__network_client.send(network_handler.NetworkPacket(
                packet_type="command",
                command_name=command,
                command_attributes=args,
                )
                )
        except Exception as e:
            gui_handler.new_print(f"ERROR: {e}")
            return None
        run: bool = True
        while run:
            try:
                if back_reply:  # send backreply:
                    self.__network_client.send(network_handler.NetworkPacket(
                        packet_type="reply",
                        data=back_reply,
                        )
                        )
            except Exception as e:
                gui_handler.new_print(f"ERROR: {e}")
                return None

    def execute_cmd_client(self, command: str, args = None):
        """Takes a command, and arguments. Executes the command
        with the given arguments, if possible."""
        print(f"{command}||SEP||{args}")
        if not args:
            args = ([],)
        try:
            func = getattr(self, command)
        except AttributeError:
            gui_handler.new_print(f"There is no command called {command}")
        given_args_len = len(args)
        # get number of keyword args:
        if func.__defaults__:
            kwargs = len(func.__defaults__)
        else:
            kwargs = 0
        # subtract kwargs from all args to get positional args
        expected_args_len = func.__code__.co_argcount - kwargs -1  # -1 otherwise self counts as an arg 
        if given_args_len >= 1:
            if expected_args_len == given_args_len:
                # run method:
                try:
                    return func(*args)
                except Exception as e:
                    gui_handler.new_print(f"ERROR in Client.execute_cmd_client: {e}")
            elif expected_args_len == 0 and given_args_len != 0:
                return func()
            else: # wrong number of arguments were given
                gui_handler.new_print(f"Command {command} takes {expected_args_len} arguments, you gave {given_args_len}.")
        else:  # no args where given:
            if expected_args_len == given_args_len:
                # run method:
                try:
                    return func()
                except Exception as e:
                    gui_handler.new_print(f"ERROR in Client.execute_cmd_client: {e}")
            else: # wrong number of arguments were given
                gui_handler.new_print(f"Command {command} takes {expected_args_len} arguments, you gave {given_args_len}.")

    def load_aliases(self):
        """Load aliases from File"""
        with open(self.__alias_file, "r", encoding="utf-8") as reader:
            lines = reader.readlines()
            aliases = {}
            for line in lines:
                if not line.startswith("#"):  # make comments with '#' in aliases.als
                    line = line.strip("\n").split(" ")
                    aliases[line[0]] = line[1]
        return aliases

    def user_input_get_command(self, prompt="input$>"):
        """Returns a command and the arguments for this
        command, the user typed in."""
        user_in = gui_handler.new_input(prompt).split(" ")
        if len(user_in) > 1:
            return user_in[0], list(user_in[1:])
        # else:
        return user_in[0], []

##############################
## user executable commands ##
##############################

    def join_server(self, server_ip: str="127.0.0.1", server_port:int=27300):
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
        gui_handler.new_print(f"Successfully connected to {server_ip}.")

    def clear(self):
        gui_handler.clear()

    def quit_game(self, args=None) -> None:
        """Saves and quits the game."""
        self.execute_cmd_server("save_player")
        pg_quit()  # quit pygame
        exit("Good bye, see you next time in Atlantica!")

    def new_game(self, args=None) -> None:
        """Creates a new game save slot"""
        prompt = "new_game$>"
        game_name = gui_handler.new_input( f"Please input the name of the gameslot {prompt}")
        game_file_path = f"saves/gameslot_{game_name}.sqlite"
        if exists(game_file_path):
            overwrite = gui_handler.new_input(
                f"This gameslot is already occupied, do you want to overwrite? [y/N] {prompt}"
            ).lower()
            if not (overwrite == "y" or overwrite == "yes"):
                return None
        shutil.copyfile("data/game_content.sqlite", game_file_path)
        gui_handler.new_print(
            f"The gameslot: {game_name} was sucessfully created."
        )
        self.__database_handler.set_database(game_file_path)
        return None

    def start_server(self, server_port = 27300, local:bool=False) -> None:
        """Starts a server for the client to connect to."""
        saved_game_files = listdir("saves/")
        if saved_game_files:
            gui_handler.new_print("Pick your option:")
            for index, file_name in enumerate(saved_game_files):
                gui_handler.new_print(
                    f"Option {index +1} is {file_name[9:-7]}"
                )  # prints the name of the gamestate, without printing the whole file name
            try:
                option = int(
                    gui_handler.new_input("Input the number of your option $> ")
                )
            except ValueError:
                gui_handler.new_print(
                    "You have to put in the NUMBER of your gameslot."
                )
                return None
            game_file_path = f"saves/{saved_game_files[option-1]}"
            # start server:
            # NEED TO FIND MEHTOD TO START SERVER, WITHOUT SOTTPING CLIENT!
            system(f"python3 server.py {game_file_path} {local} {server_port} &")
        else:
            gui_handler.new_print("There are no gameslots available, create one with 'new'.")

    def load_game(self):
        self.start_server(local=True)

    def set_name(self, name:str=None):
        if name:
            self.name = name
        else:
            self.name = gui_handler.new_input("set_name$>")
        gui_handler.new_print(f"Name was set to {self.name}.")

    def delete_game(self, args=None) -> None:
        """Delete the given Gameslot."""
        saved_game_files = listdir("saves/")
        if saved_game_files:
            gui_handler.new_print("Pick your option:")
            for index, file_name in enumerate(saved_game_files):
                gui_handler.new_print(
                    f"Option {index +1} is {file_name[9:-7]}"
                )  # prints the name of the gamestate, without printing the whole file name
            option: str = gui_handler.new_input(
                "Input the number of your option. del$>"
            )
            try:
                option: int = int(option)
                gameslot: str = f"{saved_game_files[option-1]}"
            except ValueError:
                gameslot = f"gameslot_{option}.sqlite"
                if not gameslot in saved_game_files:
                    gui_handler.new_print(
                        f"Der Gameslot {gameslot[9:-7]} exisiert nicht."
                    )
                    return None
            consent = gui_handler.new_input(
                f"Bist du dir sicher, dass du Gameslot {gameslot[9:-7]} löschen möchtest? [y/N] del$> "
            ).lower()
            if consent == "y":
                remove(f"saves/{gameslot}")
                gui_handler.new_print(f"Gameslot {gameslot[9:-7]} wurde gelöscht.")
            else:
                gui_handler.new_print("Nichts wurde gelöscht.")

        else:
            gui_handler.new_print("There are no gameslots.")

    def add_alias(self, alias:str, command:str):
        """add alias to the aliases File"""
        if alias.startswith("#"):
            gui_handler.new_print("Aliases are not allowed to start with '#'")
        else:
            with open(self.__alias_file, "a", encoding="utf-8") as writer:
                writer.write(f"{alias.strip(" ")} {command.strip(" ")}\n")
            self.__aliases = self.load_aliases()

########################
## Gui handler stuff: ##
########################

    def client_print(self, data:str):
        gui_handler.new_print(data)
        return "end_of_command"

######################################
## Not yet Implement in gui handler ##
######################################

    def set_information_left(self, key, value):
        terminal_handler.set_information_left(key, value)

    def set_information_center(self, key, value):
        terminal_handler.set_information_center(key, value)

    def set_information_right(self, key, value):
        terminal_handler.set_information_right(key, value)

    def reset_terminal_handler(
        self, information_content_left,
        information_content_center,
        information_content_right
    ):
        terminal_handler.reset_information()
        for key, value in information_content_left.items():
            terminal_handler.set_information_left(key, value)
        for key, value in information_content_center.items():
            terminal_handler.set_information_center(key, value)
        for key, value in information_content_right.items():
            terminal_handler.set_information_right(key, value)

if __name__ == "__main__":
    client = Client()  # init client
    gui_handler = GuiHandler()  # init gui handler
    # main loop
    client.user_input_loop("menu")
