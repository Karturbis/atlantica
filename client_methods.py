# standart imports:
from os.path import exists  # Checks if given file exists. Used to prevent errors.
from os import listdir  # To list all files of a directory, used in Main.load_game()
from os import remove  # To remove files
import shutil  # Used copy the content.sqlite file into a new gameslot

from inspect import signature

from handler import TerminalHandler
from handler import DatabaseHandler

class Client_Methods():

    def __init__(self):
        self.__local_methods: dict = {
            "menu": ["clear", "new_game", "load_game", "delete_game", "quit"],
            "ingame": ["clear"],
        }
        self.__database_handler = DatabaseHandler()


    def execute_cmd(self, command, args = None):
        if not args:
            args = []
        try:
            func = getattr(self, command)
        except AttributeError:
            return f"There is no command called {command}"
        given_args_len = len(args)
        expected_args_len = len(signature(func).parameters)
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
                return f"Command {command} takes {expected_args_len} arguments, you gave {given_args_len}."
        else:  # no args where given:
            if expected_args_len == given_args_len:
                # run method:
                try:
                    return func()
                except Exception as e:
                    return f"ERROR in Clienmethods.excute_cmd: {e}"
            else: # wrong number of arguments were given
                return f"Command {command} takes {expected_args_len} arguments, you gave {given_args_len}."

    def user_input_get_command(self, prompt="input$>"):
        user_in = input(f"{prompt} ").split(" ")
        if len(user_in) > 1:
            return user_in[0], user_in[1:]
        # else:
        return user_in[0], []

    def func1(self):
        print("func!1")

    def new_print(self, data):
        system("clear")
        print(data)

    def clear(self):
        TerminalHandler.clear()
    
    def quit_game(self, args=None) -> None:
        """Saves and quits the game."""
        self.save_game()
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
