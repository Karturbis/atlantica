"""This is the main file of the text adventure game 'atlantica' for
more information see readme.md"""
import sys
from datetime import datetime
from os.path import exists
from os import walk
import pickle
import pansi
import menu

class Options:

    OPTIONS:list = [
        "New game",
        "Load game",
        "Character",
        "Save",
        "Exit"
        ]

    def new_game(self) -> None:
        pass


    def character_menu(self) -> None:
        pass

    def save_game(self) -> None:
        main.save_game()

    def load_game(self) -> None:
        game_save_files: list = main.list_game_save_files()
        choosed: int = menu.main([i.replace(".save", "") for i in game_save_files])
        main.load_game(game_save_files[choosed])

class Oponent:
    """Class for normal Oponents, Bosses and Minibosses"""
    health: int = None

    def __init__(self, health) -> None:
        self.health = health


class WorldState:
    """The state of the whole world, not
    depending on the character state"""
    bosses: dict[Oponent] = {}


class Characterstate:
    """"""
    coordinates: list[int] = []
    health: int = None

    def __init__(self, coordinates) -> None:
        self.coordinates = coordinates

class Main:

    def __init__(self) -> None:
        pass

    def save_game(self) -> None:
        file:str = str(datetime.now()).replace("-", "_").replace(" ", "-")[:16]
        i = 0
        while exists(file + ".save"):
            file = f"{file[:16]}-{i}"
            i += 1

        with open(f"{file}.save", "wb") as writer:
            #pickle.dump([player, level], writer)
            pass

    def load_game(self, file:str) -> (WorldState, Characterstate):
        with open(f"{file}.save", "rb") as reader:
            player, level = pickle.load(reader)
            return (player, level)

    def list_game_save_files(self) -> list:
        game_save_files: list = next(walk("saves"), (None, None, []))[2]
        return game_save_files

menu.main([
    "New game",
    "Load game",
    "Character",
    "Save",
    "Exit"
    ])

main = Main()
