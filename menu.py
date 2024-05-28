"""This module provides a simple implementation
of a menu, that can be used flexible."""

def main(options: list, caption: str = "", iteration_zero: bool = True) -> int:
    """The main method, which displays the menu."""
    if iteration_zero:
        options.append("Help")

    print(caption)
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
    if option == len(options):
        main(options, caption, False)
    return option
