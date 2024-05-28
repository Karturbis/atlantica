"""This is the main file of the text adventure game framework
'atlantica' for more information see readme.md"""
import sys
from datetime import datetime
from os.path import exists
from os import walk
import pickle
import pansi
from menu import menu
import fight


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
        print(f"The game was saved as {main.save_game()}.")

    def load_game(self) -> None:
        game_save_files: list = main.list_game_save_files()
        choosed: int = menu.main([i.replace(".save", "") for i in game_save_files], "Load Game Menu")
        main.load_game(game_save_files[choosed])


class Oponent:
    """Class for normal Oponents, Bosses and Minibosses"""
    species: str = ""
    health: int = None
    name: str = ""
    strength: int = None
    speed: int = None
    krit_rate: int = None
    miss_rate: int = None
    attacks: dict = {}  # Attack name is key, value is the attack damage
    items: dict = {}  # Item name is key, value is list of item properties

    def __init__(self, health) -> None:
        self.health = health
    
    def get_attributes(self) -> dict:
        attributes: dict = {
            "species": self.species,
            "health": self.health,
            "name": self.name,
            "strength": self.strength,
            "speed": self.speed,
            "krit_rate": self.krit_rate,
            "miss_rate": self.miss_rate,
            "attacks": self.attacks,
            "items": self.items
            }
        return attributes



class GameState:
    """The state of the whole world, not
    depending on the character state"""
    time:int = None


class Player:

    name: str = ""
    surname: str = ""
    species: str = ""
    weight: int = None
    height: int = None
    health: int = None
    hunger: int = None
    experience_points: int = None
    ability_points: int = None
    reputation: dict = {}  # Key is region, value is the reputation in this region
    known_characters: dict = {}  # Key is characters id, value is dict of characters attributes
    known_items: dict = {}  # 
    speed: int = None
    strength: int = None
    inventory: dict = {}
    coordinates: list[int] = []

    def __init__(self, coordinates) -> None:
        self.coordinates = coordinates

    def get_fight_attributes(self) -> dict:
        fight_attributes: dict = {
            "species": self.species,
            "weight": self.weight,
            "height": self.height,
            "name": self.name,
            "health": self.health,
            "hunger": self.hunger,
            "known_items": self.known_items,
            "speed": self.speed,
            "strength": self.strength,
            "inventory": self.inventory,

        }


class Main:

    def __init__(self) -> None:
        pass

    def save_game(self) -> str:
        file:str = str(datetime.now()).replace("-", "_").replace(" ", "-")[:16]
        i = 0
        while exists(file + ".save"):
            file = f"{file[:16]}-{i}"
            i += 1

        with open(f"{file}.save", "wb") as writer:
            #pickle.dump([player, level], writer)
            pass

        return file

    def load_game(self, file:str) -> (GameState):
        with open(f"{file}.save", "rb") as reader:
            player, level = pickle.load(reader)
            return (player, level)

    def list_game_save_files(self) -> list:
        game_save_files: list = next(walk("saves"), (None, None, []))[2]
        return game_save_files

menu([
    "New game",
    "Load game",
    "Character",
    "Save",
    "Exit"
    ])

main = Main()
