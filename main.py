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
        choosed: int = menu([i.replace(".save", "") for i in game_save_files], "Load Game Menu")
        main.load_game(game_save_files[choosed])


class Character:

    species: str = ""
    health: int = None
    name: str = ""
    strength: int = None
    speed: int = None
    crit_rate: int = None
    accuracy: int = None
    attacks: dict = {}  # Attack name is key, value is the attack damage
    inventory: dict = {}  # Item name is key, value is list of item properties

    def __init__(
        self, species: str, health: int,
        name: str, strength: int, speed: int,
        crit_rate: int, accuracy: int,
        attacks: dict, inventory: dict,
        experience_points: int
        ) -> None:

        self.species = species
        self.health = health
        self.name = name
        self.strength = strength
        self.speed = speed
        self.crit_rate = crit_rate
        self.accuracy = accuracy
        self.attacks = attacks
        self.inventory = inventory
        self.experience_points = experience_points

    def get_attributes(self) -> dict:
        attributes: dict = {
            "species": self.species,
            "health": self.health,
            "name": self.name,
            "strength": self.strength,
            "speed": self.speed,
            "crit_rate": self.crit_rate,
            "accuracy": self.accuracy,
            "attacks": self.attacks,
            "inventory": self.inventory
            }
        return attributes


class Oponent(Character):
    """Class for normal Oponents, Bosses and Minibosses"""
    def __init__(self, species: str, health: int,
        name: str, strength: int, speed: int,
        crit_rate: int, accuracy: int,
        attacks: dict, inventory: dict,
        experience_points: int
        ) -> None:
        super().__init__(
            species, health, name, strength,
            speed, crit_rate, accuracy, attacks,
            inventory, experience_points
            )


class Player(Character):

    surname: str = ""
    weight: int = None
    height: int = None
    hunger: int = None
    ability_points: int = None
    reputation: dict = {}  # Key is region, value is the reputation in this region
    known_characters: dict = {}  # Key is characters id, value is dict of characters attributes
    experience_points: int = None
    coordinates: list[int] = []

    def __init__(
        self, species: str, health: int,
        name: str, surname: str,
        strength: int, speed: int,
        crit_rate: int, accuracy: int,
        attacks: dict, inventory: dict,
        weight: int, height: int, hunger: int,
        experience_points: int, reputation: dict,
        ability_points: int, coordinates: list[int],
        known_characters: dict
        ) -> None:
        super().__init__(
            species, health, name, strength,
            speed, crit_rate, accuracy, attacks,
            inventory, experience_points
            )
        self.surname = surname
        self.weight = weight
        self.height = height
        self.hunger = hunger
        self.ability_points = ability_points
        self.reputation = reputation
        self.known_characters = known_characters
        self.coordinates = coordinates

    def get_fight_attributes(self) -> dict:
        fight_attributes: dict = {
            "species": self.species,
            "weight": self.weight,
            "height": self.height,
            "name": self.name,
            "health": self.health,
            "hunger": self.hunger,
            "speed": self.speed,
            "strength": self.strength,
            "inventory": self.inventory,
        }
        return fight_attributes


class GameState:
    """The state of the whole game"""
    time:int = None


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
