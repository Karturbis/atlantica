"""Module, to have stats at the top of the terminal window."""

from os import system
from os import name
from os import get_terminal_size


class TerminalHandler:
    """Contains all methods needed
    to display stats at the top of the
    terminal window."""

    def __init__(
        self,
        information_content_left: dict = None,
        information_content_center: dict = None,
        information_content_right: dict = None,
    ):
        self.__information_content_left: dict = information_content_left
        self.__information_content_center: dict = information_content_center
        self.__information_content_right: dict = information_content_right
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
        border: str = str(get_terminal_size()[0] * "-")
        information_content_printable: str = border
        longest_data_dict: dict = self.__information_content_left
        if len(longest_data_dict) < len(self.__information_content_center):
            longest_data_dict = self.__information_content_center
        if len(longest_data_dict) < len(self.__information_content_right):
            longest_data_dict = self.__information_content_right
        for i in range(len(longest_data_dict)):
            information_content_left: str = str(
                self.__information_content_left[
                    list(self.__information_content_left.keys())[i]
                ]
            )
            information_content_center: str = str(
                self.__information_content_center[
                    list(self.__information_content_center.keys())[i]
                ]
            )
            information_content_right: str = str(
                self.__information_content_right[
                    list(self.__information_content_right.keys())[i]
                ]
            )
            spaces: int = int(
                (
                    get_terminal_size()[0]
                    - (
                        len(information_content_left)
                        + len(information_content_center)
                        + len(information_content_right)
                        + len(list(self.__information_content_left.keys())[i])
                        + len(list(self.__information_content_center.keys())[i])
                        + len(list(self.__information_content_right.keys())[i])
                        + 6  # To account for the three colons and spaces that will be printed.
                    )
                )
                / 2
            )
            information_content_printable = f"{information_content_printable}\n{list(self.__information_content_left.keys())[i]}: {information_content_left}{spaces*" "}{list(self.__information_content_center.keys())[i]}: {information_content_center}{spaces*" "}{list(self.__information_content_right.keys())[i]}: {information_content_right}"
        return f"{information_content_printable}\n{border}"

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

    def set_information(self, key: str, value: int):
        """Set the information, which is
        displayed at the top of the screen."""
        self.__information_content[key] = value
        self.update_terminal()

    def check_terminal_overflow(self):
        """Checks, if the terminal has
        enough columns for the content,
        if not, the oldest entries in the
        terminal history get deleted."""
        if get_terminal_size()[1] <= (
            len(self.__information_content_left) + len(self.__terminal_content) + 3
        ):  # The 3 accounts for the two lines, which are printed for design reasons
            self.__terminal_content.pop(0)
            self.update_terminal()

# Tests:
if __name__ == "__main__":
    th = TerminalHandler(
        {"ghfdg": 2331, "ghb": 2, "cgh": 3}, {"d": 1, "sdf": 2, "fdf": 3}, {"ser": 1, "fds": 2, "ssd": 3}
    )
    th.new_print("Hello Woreld")
