# standart imports:
from os.path import exists  # Checks if given file exists. Used to prevent errors.
from os import listdir  # To list all files of a directory, used in Main.load_game()
from os import remove  # To remove files
from os import system
import shutil  # Used copy the content.sqlite file into a newfrom os import system gameslot
from sys import exit

# handler imports:
from handler import DatabaseHandler
from handler import network_handler
from handler import TerminalHandler


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
        self.__name = "test"

    def join_server(self, server_ip: str="127.0.0.1", server_port:int=27300):
        server_ip="127.0.0.1"
        server_port = 27300
        self.__network_client = network_handler.NetworkClient(server_ip, server_port)
        self.__server_methods = self.__network_client.connect().data
        x = self.__network_client.send(network_handler.NetworkPacket(
            packet_type="hello", data=self.__name
        ))
        self.input_loop("ingame", prompt=f"{self.__name}@{server_ip}>")

    def execute_cmd_client(self, command, args = None):
        if not args:
            args = []
        try:
            func = getattr(self, command)
        except AttributeError:
            print(f"There is no command called {command}")
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
                    print(f"ERROR in Client.execute_cmd_client: {e}")
            elif expected_args_len == 0 and given_args_len != 0:
                return func()
            else: # wrong number of arguments were given
                print(f"Command {command} takes {expected_args_len} arguments, you gave {given_args_len}.")
        else:  # no args where given:
            if expected_args_len == given_args_len:
                # run method:
                try:
                    return func()
                except Exception as e:
                    print(f"ERROR in Client.execute_cmd_client: {e}")
            else: # wrong number of arguments were given
                print(f"Command {command} takes {expected_args_len} arguments, you gave {given_args_len}.")

    def user_input_get_command(self, prompt="input$>"):
        user_in = input(f"{prompt} ").split(" ")
        if len(user_in) > 1:
            return user_in[0], list(user_in[1:])
        # else:
        return user_in[0], []

    def clear(self):
        TerminalHandler.clear()

    def quit_game(self, args=None) -> None:
        """Saves and quits the game."""
        self.execute_cmd_server("save_player")
        exit("Good bye, see you next time in Atlantica!")

    def new_game(self, args=None) -> None:
        """Creates a new game save slot"""
        prompt = "new_game$>"
        game_name = TerminalHandler.new_input(
            f"Please input the name of the gameslot\n{prompt} "
        )
        game_file_path = f"saves/gameslot_{game_name}.sqlite"
        if exists(game_file_path):
            overwrite = TerminalHandler.new_input(
                f"This gameslot is already occupied, do you want to overwrite? [y/N]\n{prompt} "
            ).lower()
            if not overwrite == "y" or overwrite == "yes":
                return None
        shutil.copyfile("data/game_content.sqlite", game_file_path)
        TerminalHandler.new_print(
            f"The gameslot: {game_name} was sucessfully created."
        )
        self.__database_handler.set_database(game_file_path)
        return None

    def start_server(self, server_port = 27300, local:bool=False) -> None:
        saved_game_files = listdir("saves/")
        if saved_game_files:
            TerminalHandler.new_print("Pick your option:")
            for index, file_name in enumerate(saved_game_files):
                TerminalHandler.new_print(
                    f"Option {index +1} is {file_name[9:-7]}"
                )  # prints the name of the gamestate, without printing the whole file name
            try:
                option = int(
                    TerminalHandler.new_input("Input the number of your option.\n> ")
                )
            except ValueError:
                TerminalHandler.new_print(
                    "You have to put in the NUMBER of your gameslot."
                )
                return None
            game_file_path = f"saves/{saved_game_files[option-1]}"
            # start server:
            # NEED TO FIND MEHTOD TO START SERVER, WITHOUT SOTTPING CLIENT!
            system(f"python3 server.py {game_file_path} {local} {server_port} &")
        else:
            TerminalHandler.new_print("There are no gameslots available, create one with 'new'.")

    def load_game(self):
        self.start_server(local=True)

    def set_name(self, name:str=None):
        if name:
            self.__name = name
        else:
            self.__name = TerminalHandler.new_input("set_name$> ")

    def delete_game(self, args=None) -> None:
        """Delete the given Gameslot."""
        saved_game_files = listdir("saves/")
        if saved_game_files:
            TerminalHandler.new_print("Pick your option:")
            for index, file_name in enumerate(saved_game_files):
                TerminalHandler.new_print(
                    f"Option {index +1} is {file_name[9:-7]}"
                )  # prints the name of the gamestate, without printing the whole file name
            option: str = TerminalHandler.new_input(
                "Input the number of your option.\ndel$> "
            )
            try:
                option: int = int(option)
                gameslot: str = f"{saved_game_files[option-1]}"
            except ValueError:
                gameslot = f"gameslot_{option}.sqlite"
                if not gameslot in saved_game_files:
                    TerminalHandler.new_print(
                        f"Der Gameslot {gameslot[9:-7]} exisiert nicht."
                    )
                    return None
            consent = TerminalHandler.new_input(
                f"Bist du dir sicher, dass du Gameslot {gameslot[9:-7]} löschen möchtest? [y/N]\ndel$> "
            ).lower()
            if consent == "y":
                remove(f"saves/{gameslot}")
                TerminalHandler.new_print(f"Gameslot {gameslot[9:-7]} wurde gelöscht.")
            else:
                TerminalHandler.new_print("Nichts wurde gelöscht.")

        else:
            TerminalHandler.new_print("There are no gameslots.")

    def input_loop(self, mode: str, prompt:str = None):
        if not prompt:
            prompt = f"{mode}$>"
        while True:
            user_input = self.user_input_get_command(prompt)
            if user_input[0] in self.__aliases:
                user_input = (self.__aliases[user_input[0]], user_input[1:][0])
            if user_input[0] in self.__local_methods[mode]:
                if user_input[1]:
                    self.execute_cmd_client(user_input[0], user_input[1:][0])
                else:
                    self.execute_cmd_client(user_input[0])
            elif user_input[0] in self.__server_methods:
                if user_input[1]:
                    self.execute_cmd_server(user_input[0], user_input[1:][0])
                else:
                    self.execute_cmd_server(user_input[0])
            else:
                TerminalHandler.new_print(f"There is no command '{user_input[0]}'")

    def execute_cmd_server(self, command, args=None):
        if not args:
            args = []
        back_reply = None
        try:
            # send command and set reply to the answer from the server:
            reply = self.__network_client.send(network_handler.NetworkPacket(
                packet_type="command",
                command_name=command,
                command_attributes=args,
                )
                )
        except Exception as e:
            print(f"ERROR: {e}")
            return None
        run: bool = True
        while run:
            try:
                if back_reply:  # send backreply:
                    reply = self.__network_client.send(network_handler.NetworkPacket(
                        packet_type="reply",
                        data=back_reply,
                        )
                        )
                if reply.packet_type == "command":
                    # set backreply to the return of the command the server send
                    back_reply = self.execute_cmd_client(
                        reply.command_name,
                        [reply.command_attributes]
                        )
                elif reply.packet_type == "reply":
                    # if "end_of_command" packet, end the conservation with server:
                    if reply.data == "end_of_command":
                        return None
                    # else:
                    print(reply.data)
                    return None
            except Exception as e:
                print(f"ERROR: {e}")
                return None

    def load_aliases(self):
        with open(self.__alias_file, "r", encoding="utf-8") as reader:
            lines = reader.readlines()
            aliases = {}
            for line in lines:
                if not line.startswith("#"):  # make comments with '#' in aliases.als
                    line = line.strip("\n").split(" ")
                    aliases[line[0]] = line[1]
        return aliases

    def add_alias(self, alias:str, command:str):
        if alias.startswith("#"):
            TerminalHandler.new_print("Aliases are not allowed to start with '#'")
        else:
            with open(self.__alias_file, "a", encoding="utf-8") as writer:
                writer.write(f"{alias.strip(" ")} {command.strip(" ")}\n")
            self.__aliases = self.load_aliases()


############################
## Terminal handler shit: ##
############################

    def client_print(self, data:str):
        TerminalHandler.new_print(data)
        return "end_of_command"

    def set_information_left(self, key, value):
        TerminalHandler.set_information_left(key, value)

    def set_information_center(self, key, value):
        TerminalHandler.set_information_center(key, value)

    def set_information_right(self, key, value):
        TerminalHandler.set_information_right(key, value)

    def reset_terminal_handler(
        self, information_content_left,
        information_content_center,
        information_content_right
    ):
        TerminalHandler.init(information_content_left,
        information_content_center,
        information_content_right)

if __name__ == "__main__":

    TerminalHandler.init(
        {"": ""},
        {"": ""},
        {"": ""}
    )
    client = Client()
    client.input_loop("menu")
