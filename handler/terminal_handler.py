"""Module, to have stats at the top of the terminal window."""

from os import system
from os import name
from shutil import get_terminal_size



class TerminalHandler:
    """Contains all methods needed
    to display stats at the top of the
    terminal window."""

    __information_content_left: dict = {}
    __information_content_center: dict = {}
    __information_content_right: dict = {}
    __terminal_content: list = []

    @classmethod
    def init(cls,information_content_left: dict = None,information_content_center: dict = None,information_content_right: dict = None,):
        cls.__information_content_left: dict = information_content_left
        cls.__information_content_center: dict = information_content_center
        cls.__information_content_right: dict = information_content_right
        cls.__terminal_content: list = []
        system("cls" if name == "nt" else "clear")
        print(cls.gen_information_content_printable())

    @classmethod
    def new_print(cls, print_content: str) -> None:
        """Prints the input and additionaly
        logs it into the terminal_content variable."""
        cls.__terminal_content.append(print_content)
        print(print_content)
        cls.check_terminal_overflow()

    @classmethod
    def new_input(cls, print_content: str = "") -> str:
        """Input method, which logs its output to
        the terminal_content variable."""
        terminal_input = input(print_content)
        cls.__terminal_content.append(f"{print_content}{terminal_input}")
        cls.check_terminal_overflow()
        return terminal_input

    @classmethod
    def clear(cls) -> None:
        """Clears the screen."""
        information_content_printable = cls.gen_information_content_printable()
        system("cls" if name == "nt" else "clear")
        cls.__terminal_content = []
        print(information_content_printable)

    @classmethod
    def longest_dict(cls, dicts: list[dict]) -> dict:
        """Returns the longest dict from a list
        of given dicts."""
        longest_dict: dict = {}
        for i in dicts:
            if len(i) > len(longest_dict):
                longest_dict = i
        return longest_dict

    @classmethod
    def get_content_parts(cls, len_biggest_str: int, content_str: str) -> str:
        """Centers the given string between spaces with the given
        over all length."""
        spaces = int((len_biggest_str - len(content_str)) / 2) * " "
        return f"{spaces}{content_str}{spaces}"

    @classmethod
    def gen_information_content_printable(cls) -> str:
        """Returns a printeble string of the
        information, which is to be displayed
        at the top of the window."""
        border: str = str(get_terminal_size()[0] * "-")
        information_content_printable: str = f"{border}\n"
        longest_data_dict: dict = cls.longest_dict(
            [
                cls.__information_content_left,
                cls.__information_content_center,
                cls.__information_content_right,
            ]
        )
        # Extract dict to list of strings:
        information_content_left_str: list[str] = [
            f"{key}: {value}" for key, value in cls.__information_content_left.items()
        ]
        information_content_center_str: list[str] = [
            f"{key}: {value}"
            for key, value in cls.__information_content_center.items()
        ]
        information_content_right_str: list[str] = [
            f"{key}: {value}" for key, value in cls.__information_content_right.items()
        ]
        len_biggest_str_content_left: int = len(max(information_content_left_str))
        len_biggest_str_content_center: int = len(max(information_content_center_str))
        len_biggest_str_content_right: int = len(max(information_content_right_str))
        for i in range(len(longest_data_dict)):
            if i < len(information_content_left_str):
                information_content_part_left: str = cls.get_content_parts(
                    len_biggest_str_content_left, information_content_left_str[i]
                )
            else:
                information_content_part_left: str = ""
            if i < len(information_content_center_str):
                information_content_part_center: str = cls.get_content_parts(
                    len_biggest_str_content_center, information_content_center_str[i]
                )
            else:
                information_content_part_center: str = ""
            if i < len(information_content_right_str):
                information_content_part_right: str = cls.get_content_parts(
                    len_biggest_str_content_right, information_content_right_str[i]
                )
            else:
                information_content_part_right: str = "  "
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
        return f"{information_content_printable}{border}"

    @classmethod
    def get_terminal_content_printable(cls) -> str:
        """Returns a printable string of the
        terminal history."""
        terminal_content_printable: str = ""
        for i in cls.__terminal_content:
            terminal_content_printable = f"{terminal_content_printable}\n{i}"
        return terminal_content_printable

    @classmethod
    def update_terminal(cls):
        """Updates the data, which is
        displayed at the top of the screen."""
        information_content_printable = cls.gen_information_content_printable()
        terminal_content_printable = cls.get_terminal_content_printable()
        system("cls" if name == "nt" else "clear")
        print(f"{information_content_printable}{terminal_content_printable}")

    @classmethod
    def set_information_left(cls, key: str, value: int):
        """Set the information, which is
        displayed at the top of the screen."""
        cls.__information_content_left[key] = value
        cls.update_terminal()

    @classmethod
    def set_information_center(cls, key: str, value: int):
        """Set the information, which is
        displayed at the top of the screen."""
        cls.__information_content_center[key] = value
        cls.update_terminal()

    @classmethod
    def set_information_right(cls, key: str, value: int):
        """Set the information, which is
        displayed at the top of the screen."""
        cls.__information_content_right[key] = value
        cls.update_terminal()

    @classmethod
    def check_terminal_overflow(cls):
        """Checks, if the terminal has
        enough columns for the content,
        if not, the oldest entries in the
        terminal history get deleted."""
        if get_terminal_size()[1] <= (
            len(cls.__information_content_left) + len(cls.__terminal_content) + 3
        ):  # The 3 accounts for the two lines, which are printed for design reasons
            cls.__terminal_content.pop(0)
            cls.update_terminal()


class TerminalHandlerOld:
    """Contains all methods needed
    to display stats at the top of the
    terminal window."""

    __information_content_left: dict = {}
    __information_content_center: dict = {}
    __information_content_right: dict = {}
    __terminal_content: list = []

    @classmethod
    def init(cls,information_content_left: dict = None,information_content_center: dict = None,information_content_right: dict = None,):
        cls.__information_content_left: dict = information_content_left
        cls.__information_content_center: dict = information_content_center
        cls.__information_content_right: dict = information_content_right
        cls.__terminal_content: list = []
        system("cls" if name == "nt" else "clear")
        print(cls.gen_information_content_printable())

    @classmethod
    def new_print(cls, print_content: str) -> None:
        """Prints the input and additionaly
        logs it into the terminal_content variable."""
        cls.__terminal_content.append(print_content)
        print(print_content)
        cls.check_terminal_overflow()

    @classmethod
    def new_input(cls, print_content: str = "") -> str:
        """Input method, which logs its output to
        the terminal_content variable."""
        terminal_input = input(print_content)
        cls.__terminal_content.append(f"{print_content}{terminal_input}")
        cls.check_terminal_overflow()
        return terminal_input

    @classmethod
    def clear(cls) -> None:
        """Clears the screen."""
        information_content_printable = cls.gen_information_content_printable()
        system("cls" if name == "nt" else "clear")
        cls.__terminal_content = []
        print(information_content_printable)

    @classmethod
    def longest_dict(cls, dicts: list[dict]) -> dict:
        """Returns the longest dict from a list
        of given dicts."""
        longest_dict: dict = {}
        for i in dicts:
            if len(i) > len(longest_dict):
                longest_dict = i
        return longest_dict

    @classmethod
    def get_content_parts(cls, len_biggest_str: int, content_str: str) -> str:
        """Centers the given string between spaces with the given
        over all length."""
        spaces = int((len_biggest_str - len(content_str)) / 2) * " "
        return f"{spaces}{content_str}{spaces}"

    @classmethod
    def gen_information_content_printable(cls) -> str:
        """Returns a printeble string of the
        information, which is to be displayed
        at the top of the window."""
        border: str = str(get_terminal_size()[0] * "-")
        information_content_printable: str = f"{border}\n"
        longest_data_dict: dict = cls.longest_dict(
            [
                cls.__information_content_left,
                cls.__information_content_center,
                cls.__information_content_right,
            ]
        )
        # Extract dict to list of strings:
        information_content_left_str: list[str] = [
            f"{key}: {value}" for key, value in cls.__information_content_left.items()
        ]
        information_content_center_str: list[str] = [
            f"{key}: {value}"
            for key, value in cls.__information_content_center.items()
        ]
        information_content_right_str: list[str] = [
            f"{key}: {value}" for key, value in cls.__information_content_right.items()
        ]
        len_biggest_str_content_left: int = len(max(information_content_left_str))
        len_biggest_str_content_center: int = len(max(information_content_center_str))
        len_biggest_str_content_right: int = len(max(information_content_right_str))
        for i in range(len(longest_data_dict)):
            if i < len(information_content_left_str):
                information_content_part_left: str = cls.get_content_parts(
                    len_biggest_str_content_left, information_content_left_str[i]
                )
            else:
                information_content_part_left: str = ""
            if i < len(information_content_center_str):
                information_content_part_center: str = cls.get_content_parts(
                    len_biggest_str_content_center, information_content_center_str[i]
                )
            else:
                information_content_part_center: str = ""
            if i < len(information_content_right_str):
                information_content_part_right: str = cls.get_content_parts(
                    len_biggest_str_content_right, information_content_right_str[i]
                )
            else:
                information_content_part_right: str = "  "
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
        return f"{information_content_printable}{border}"

    @classmethod
    def get_terminal_content_printable(cls) -> str:
        """Returns a printable string of the
        terminal history."""
        terminal_content_printable: str = ""
        for i in cls.__terminal_content:
            terminal_content_printable = f"{terminal_content_printable}\n{i}"
        return terminal_content_printable

    @classmethod
    def update_terminal(cls):
        """Updates the data, which is
        displayed at the top of the screen."""
        information_content_printable = cls.gen_information_content_printable()
        terminal_content_printable = cls.get_terminal_content_printable()
        system("cls" if name == "nt" else "clear")
        print(f"{information_content_printable}{terminal_content_printable}")

    @classmethod
    def set_information_left(cls, key: str, value: int):
        """Set the information, which is
        displayed at the top of the screen."""
        cls.__information_content_left[key] = value
        cls.update_terminal()

    @classmethod
    def set_information_center(cls, key: str, value: int):
        """Set the information, which is
        displayed at the top of the screen."""
        cls.__information_content_center[key] = value
        cls.update_terminal()

    @classmethod
    def set_information_right(cls, key: str, value: int):
        """Set the information, which is
        displayed at the top of the screen."""
        cls.__information_content_right[key] = value
        cls.update_terminal()

    @classmethod
    def check_terminal_overflow(cls):
        """Checks, if the terminal has
        enough columns for the content,
        if not, the oldest entries in the
        terminal history get deleted."""
        if get_terminal_size()[1] <= (
            len(cls.__information_content_left) + len(cls.__terminal_content) + 3
        ):  # The 3 accounts for the two lines, which are printed for design reasons
            cls.__terminal_content.pop(0)
            cls.update_terminal()

# Tests:
if __name__ == "__main__":
    TerminalHandlerOld.new_print("Hello Woreld")
