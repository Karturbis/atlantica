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


class Client():

    def __init__(self):
        self.__local_methods: dict = {
            "menu": ["clear", "new_game", "load_game", "delete_game", "quit_game", "join_server"],
            "ingame": ["clear"],
        }
        self.__database_handler = DatabaseHandler()

    def join_server(self, server_ip: str="127.0.0.1", server_port:int=27300):
        server_ip="127.0.0.1"
        server_port = 27300
        network_client = network_handler.NetworkClient(server_ip, server_port)

    def execute_cmd(self, command, args = None):
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
                    print(f"ERROR in Clienmethods.execute_cmd: {e}")
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
                    print(f"ERROR in Clienmethods.excute_cmd: {e}")
            else: # wrong number of arguments were given
                print(f"Command {command} takes {expected_args_len} arguments, you gave {given_args_len}.")

    def user_input_get_command(self, prompt="input$>"):
        user_in = input(f"{prompt} ").split(" ")
        if len(user_in) > 1:
            return user_in[0], user_in[1:]
        # else:
        return user_in[0], []

    def clear(self):
        TerminalHandler.clear()

    def quit_game(self, args=None) -> None:
        """Saves and quits the game."""
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

    def load_game(self, args=None) -> None:
        # can be partially copied from main.py,
        # needs massive rewrite thoug.
        pass

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

    def _input_loop(self, mode: str, prompt:str = None):
        if not prompt:
            prompt = f"{mode}$>"
        while True:
            user_input = self.user_input_get_command(prompt)
            if user_input[0] in self.__local_methods[mode]:
                if user_input[1]:
                    self.execute_cmd(user_input[0], user_input[1:])
                else:
                    self.execute_cmd(user_input[0])
            else:
                TerminalHandler.new_print(f"There is no command '{user_input[0]}'")

##############################################################
######################  MODES:  ##############################
##############################################################

    def ingame(self):
        """main loop of
        the client side"""
        get_user_input: bool = True
        back_reply = None
        while True:
            try:
                if get_user_input:
                    # get userinput from standart console via self.__callable method:
                    command, args = self.__callable("user_input_get_command")
                    # send command and set reply to the answer from the server:
                    reply = self._send(NetworkPacket(
                        packet_type="command",
                        command_name=command,
                        command_attributes=args,
                        )
                        )
                else:  # only send backreply:
                    get_user_input = True  # reset to normal
                    reply = self._send(NetworkPacket(
                        packet_type="reply",
                        data=back_reply,    
                        )
                        )
                if reply.packet_type == "command":
                    # set backreply to the return of the command the server send
                    back_reply = self.__callable(
                        reply.command_name,
                        reply.command_attributes
                        )
                    get_user_input = False  # so next iteration of the loop, just the backreply is send
                elif reply.packet_type == "reply":
                    # if "end_of_command" packet, just go to start of while loop:
                    if reply.data == "end_of_command":
                        continue
                    # else:
                    print(reply.data)

            except socket.error as e:
                print(f"ERROR: {e}")
                break

    def menu(self):
        self._input_loop("menu")

if __name__ == "__main__":

    TerminalHandler.init(
        {"": ""},
        {"": ""},
        {"": ""}
    )

    client = Client()
    client.menu()