"""This is the parser, it converts the user
input into a command, that can be used by the
game."""

def stage_one(input_str:str, aliases: dict) -> list :
    """Convert the input string into a list of words"""
    # replace aliases with their values:
    for key, value in aliases.items():
        input_str = input_str.replace(key, value)
    # convert string into list of lower case words:
    return input_str.lower().split()

def stage_two(input_command: list):
    

def stage_three():
    pass