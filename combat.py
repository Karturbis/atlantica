import random
from menu import menu

def fight(player, opponent) -> dict:
    opponent_attributes: dict = opponent.get_attributes()
    player_attributes: dict = player.get_fight_attributes()
    player_begins = beginner_selection(player_attributes["speed"], opponent_attributes["speed"])
    fighting = True
    while fighting:
        # Do fighting stuff
        pass

def attack():
    pass

def defend():
    pass

def beginner_selection(player_speed: int, opponent_speed: int) -> bool:
    random_num = random.randint(0, 100)
    # the beginner_value depends on the speed of the player and the opponent,
    # the greater the distance between these two, the greater gets the
    # probability, that the character with the higher speed starts the fight.
    beginner_value = player_speed-opponent_speed+50
    return random_num <= beginner_value
