"""Module, to have stats at the top of the terminal window."""

from os import system
from os import name
from os import get_terminal_size


class TerminalHandler:
    """Contains all methods needed,
    to display stats at the top of the
    terminal window."""

    def __init__(self, information_content: dict = None):
        self.__information_content: dict = information_content
        self.__terminal_content: list = []
        print(self.gen_information_content_printable())

    def new_print(self, print_content: str) -> None:
        """Prints the input and additionaly
        logs it into the terminal_content variable."""
        self.__terminal_content.append(print_content)
        print(print_content)
        self.check_terminal_overflow()

    def new_input(self, print_content: str = "") -> str:
        """Input method, which logs its output to
        the terminal_content variable."""
        terminal_input = input(print_content)
        self.__terminal_content.append(f"{print_content}{terminal_input}")
        self.check_terminal_overflow()
        return terminal_input

    def clear(self) -> None:
        """Clears the screen."""
        information_content_printable = self.gen_information_content_printable()
        system("cls" if name == "nt" else "clear")
        self.__terminal_content = []
        print(information_content_printable)

    def gen_information_content_printable(self) -> str:
        """Returns a printeble string of the
        information, which is to be displayed
        at the top of the window."""
        information_content_printable: str = "-------------"
        for key, item in self.__information_content.items():
            information_content_printable = f"{information_content_printable}\n{key}: {item}"
        return f"{information_content_printable}\n-------------"

    def get_terminal_content_printable(self) -> str:
        """Returns a printable string of the
        terminal history."""
        terminal_content_printable: str = ""
        for i in self.__terminal_content:
            terminal_content_printable = f"{terminal_content_printable}\n{i}"
        return terminal_content_printable

    def update_terminal(self):
        """Updates the data, which is
        displayed at the top of the screen."""
        information_content_printable = self.gen_information_content_printable()
        terminal_content_printable = self.get_terminal_content_printable()
        system("cls" if name == "nt" else "clear")
        print(f"{information_content_printable}{terminal_content_printable}")

    def set_information(self, name: str, value: int):
        """Set the information, which is
        displayed at the top of the screen."""
        self.__information_content[name] = value
        self.update_terminal()

    def check_terminal_overflow(self):
        """Checks, if the terminal has
        enough columns for the content,
        if not, the oldest entries in the
        terminal history get deleted."""
        if get_terminal_size()[1] <= (
            len(self.__information_content) + len(self.__terminal_content) + 3
        ):  # The two account for the two lines, whoch are printed for design reasons
            self.__terminal_content.pop(0)
            self.update_terminal()
