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

    def longest_dict(self, dicts: list[dict]) -> dict:
        """Returns the longest dict from a list
        of given dicts."""
        longest_dict: dict = {}
        for i in dicts:
            if len(i) > len(longest_dict):
                longest_dict = i
        return longest_dict

    def get_content_parts(self, len_biggest_str: int, content_str: str) -> str:
        """Centers the given string between spaces with the given
        over all length."""
        spaces = int((len_biggest_str - len(content_str)) / 2) * " "
        return f"{spaces}{content_str}{spaces}"

    def gen_information_content_printable(self) -> str:
        """Returns a printeble string of the
        information, which is to be displayed
        at the top of the window."""
        border: str = str(get_terminal_size()[0] * "-")
        information_content_printable: str = f"{border}\n"
        longest_data_dict: dict = self.longest_dict(
            [
                self.__information_content_left,
                self.__information_content_center,
                self.__information_content_right,
            ]
        )
        # Extract dict to list of strings:
        information_content_left_str: list[str] = [
            f"{key}: {value}" for key, value in self.__information_content_left.items()
        ]
        information_content_center_str: list[str] = [
            f"{key}: {value}"
            for key, value in self.__information_content_center.items()
        ]
        information_content_right_str: list[str] = [
            f"{key}: {value}" for key, value in self.__information_content_right.items()
        ]
        len_biggest_str_content_left: int = len(max(information_content_left_str))
        len_biggest_str_content_center: int = len(max(information_content_center_str))
        len_biggest_str_content_right: int = len(max(information_content_right_str))
        for i in range(len(longest_data_dict)):
            if i < len(information_content_left_str):
                information_content_part_left = f"{self.get_content_parts(len_biggest_str_content_left, information_content_left_str[i])}"
            else:
                information_content_part_left = ""
            if i < len(information_content_center_str):
                information_content_part_center = f"{self.get_content_parts(len_biggest_str_content_center, information_content_center_str[i])}"
            else:
                information_content_part_center = ""
            if i < len(information_content_right_str):
                information_content_part_right = f"{self.get_content_parts(len_biggest_str_content_right, information_content_right_str[i])}"
            else:
                information_content_part_right = ""
            spaces: str = (
                int(
                    (
                        get_terminal_size()[0]
                        - (
                            len(information_content_part_left)
                            + len(information_content_part_center)
                            + len(information_content_part_right)
                        )
                    )
                    / 2
                )
                * " "
            )
            information_content_printable = f"{information_content_printable}{information_content_part_left}{spaces}{information_content_part_center}{spaces}{information_content_part_right}\n"
        return information_content_printable

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

    def set_information_left(self, key: str, value: int):
        """Set the information, which is
        displayed at the top of the screen."""
        self.__information_content_left[key] = value
        self.update_terminal()

    def set_information_center(self, key: str, value: int):
        """Set the information, which is
        displayed at the top of the screen."""
        self.__information_content_center[key] = value
        self.update_terminal()

    def set_information_right(self, key: str, value: int):
        """Set the information, which is
        displayed at the top of the screen."""
        self.__information_content_right[key] = value
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
        {"ghgzuoitpoifdg": 2331, "ghb": 2, "cgh": 3},
        {"d": 1, "sdhlf": 2, "fdf": 3},
        {"ser": 1, "fds": 2, "swetsdfgdssd": 3, "dfd": 45},
    )
    th.new_print("Hello Woreld")
