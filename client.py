# standart imports:
from ast import literal_eval  # Used to evaluate a boolean from a string
from os.path import exists  # Checks if given file exists. Used to prevent errors.
from os import listdir  # To list all files of a directory, used in Main.load_game()
from os import remove  # To remove files
import shutil  # Used copy the content.sqlite file into a new gameslot

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
            "menu": ["clear", "newgame", "loadgame", "safegame", "quit"],
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

    def menu(self):
        self.input_loop("menu")

    def quit_game(self, args=None) -> None:
        """Saves and quits the game."""
        self.save_game()
        exit("Good bye, see you next time in Atlantica!")

    def new_game(self, args=None) -> None:
        """Creates a new game save slot"""
        game_name = TerminalHandler.new_input(
            "Please input the name of the gameslot\n> "
        )
        game_file_path = f"saves/gameslot_{game_name}.sqlite"
        if exists(game_file_path):
            overwrite = TerminalHandler.new_input(
                "This gameslot is already occupied, do you want to overwrite? [y/N]\n> "
            ).lower()
            if not overwrite == "y" or overwrite == "yes":
                return None
        shutil.copyfile("data/game_content.sqlite", game_file_path)
        TerminalHandler.new_print(
            f"The gameslot: {game_name} was sucessfully created."
        )
        self.__database_handler.set_database(game_file_path)
        self.quit_menu()
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


TerminalHandler.init(
    {"test": "teste"},
    {"mitte": "mitte"},
    {"ende": "ende"}
)

cliennt = Client()
cliennt.menu()