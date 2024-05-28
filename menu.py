import sys


def main(options: list) -> int:

    for i, e in enumerate(options):
        print(f"Option {i+1} {e}")
    running: bool = True
    text: str = "Choose your option."
    while running:
        option_str: str = input(f"{text}\n>> ")
        try:
            option: int = int(option_str)
        except ValueError:
            text: str = "Please input the number of the Option you want to pick."
            continue
        running = False
    return option
