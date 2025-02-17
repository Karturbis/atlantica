"""Module, to have stats at the top of the terminal window."""

import curses
from os import system
from os import name
from shutil import get_terminal_size


class TerminalHandler:
    """Handles user input and output to the
    screen."""

    def __init__(
        self, information_content_left: dict = None,
        information_content_center: dict = None,
        information_content_right: dict = None,
        border_symbol = "-",
        ):
        self.__information_content_left: dict = information_content_left
        self.__information_content_center: dict = information_content_center
        self.__information_content_right: dict = information_content_right
        self.__border_symbol_light = border_symbol
        self.__border_symbol_bold = "="
        self.__prompt = "input>"
        self.__terminal_content: list = []
        self.__command_history: list = [""]
        self.__history_index = 1
        self.__input_str = ""
        # init the curses screens and windows
        self.__stdscr = curses.initscr()
        self.__stdscr.clear()
        row_num, col_num = self.__stdscr.getmaxyx()
        self.__row_num = row_num
        self.__col_num = col_num
        self.__screens:dict = {
                # initialize the windows for the information content:
                # use col_num//3, so every informationscreem uses 1/3 of the screen
                "information_left": curses.newwin(2, col_num//3, row_num -3, 0),
                "information_center": curses.newwin(2, col_num//3, row_num -3, col_num//3),
                "information_right": curses.newwin(2, col_num//3, row_num -3, 2*col_num//3),
                # initialize the output window:
                # num_rows-7, cause the other windows use 7 vertical space
                "output_window": curses.newwin(row_num-7, col_num, 1, 0),
                # initialize the user input mask:
                "input_field": curses.newwin(1, col_num, row_num-5, 0),

                # initialize borders:
                # all borders have height 1 and width col_num, because
                # they are reetitions of one symbol over the whole terminal width
                # Border at the top of the terminal:
                "border_top": curses.newwin(1, col_num, 0, 0),

                # border on top of the input field, 6 higher than ground:
                "input_field_border_top": curses.newwin(1, col_num, row_num -6, 0),

                # border dividing input_field and information field, 4 higher than ground:
                "input_field_border_bottom": curses.newwin(1, col_num, row_num-4, 0),

                # border at the bottom of the screen:
                "information_border_bottom": curses.newwin(1, col_num, row_num-1, 0),
        }
        # clear all screens:
        for _, screen in self.__screens.items():
            screen.clear()
        # add information to the information screens:
        self.update_static_information()
        # put data into the borders:
        self.__screens["border_top"].addstr(self.__border_symbol_light * (col_num -1))
        self.__screens["input_field_border_top"].addstr(self.__border_symbol_light * (col_num -1))
        self.__screens["input_field_border_bottom"].addstr(self.__border_symbol_bold * (col_num -1))
        self.__screens["information_border_bottom"].addstr(self.__border_symbol_bold * (col_num -1))
        self.refresh_screens()  # print data to the terminal 

    def curses_wrapper(self, func, /, *args, **kwargs):
        try:
            curses.noecho()
            curses.cbreak()
            self.__screens["input_field"].keypad(True)
            result = func(*args, **kwargs)
        finally:
            self.__stdscr.keypad(False)
            self.__screens["input_field"].keypad(False)
            curses.echo()
            curses.nocbreak()
            curses.endwin()
        return result

    def set_information_left(self, key: str, value:int):
        self.__information_content_left[key] = value
        self.update_static_information()

    def set_information_center(self, key: str, value:int):
        self.__information_content_center[key] = value
        self.update_static_information()

    def set_information_right(self, key: str, value:int):
        self.__information_content_right[key] = value
        self.update_static_information()

    def update_static_information(self):
        for key, value in self.__information_content_left.items():
            self.__screens["information_left"].addstr(f"{key}: {value}")
        for key, value in self.__information_content_center.items():
            self.__screens["information_center"].addstr(f"{key}: {value}")
        for key, value in self.__information_content_right.items():
            self.__screens["information_right"].addstr(f"{key}: {value}")

######################
## wrapper methods: ##
######################

    def new_print(self, content: str):
        return self.curses_wrapper(self._new_print, content)

    def new_input(self, prompt: str):
        return self.curses_wrapper(self._new_input, prompt)

######################
## wrapped methods: ##
######################

    def _new_print(self, content:str):
        self.__terminal_content.append(content)
        out_window = self.__screens["output_window"]
        out_window.clear()
        # 8 accounts for lines occupied by borders, infromation and such
        out_window_free_space = self.__row_num - (7 + len(self.__terminal_content))
        # if terminal overflows, delete the old print statements
        while out_window_free_space < 0:
            self.__terminal_content.pop(0)
            out_window_free_space = self.__row_num - (7 + len(self.__terminal_content))
        out_window.addstr("\n" * out_window_free_space)
        # print terminal content
        for index, output in enumerate(self.__terminal_content):
            if index == 0:
                out_window.addstr(output)
            else:
                out_window.addstr(f"\n{output}")
        out_window.refresh()

    def _new_input(self, prompt: str):
        """new input has to be ran from a loop,
        it returns None as long, as the user has not
        pressed enter, if the user has pressed enter,
        it returns the string from the user."""
        in_field = self.__screens["input_field"]
        in_field.clear()
        in_field.addstr(f"{prompt} {self.__input_str}")
        key = in_field.getch()  # get keyboard input
        # work with keyboard input:
        if key == curses.KEY_BACKSPACE:
            in_field.clear()
            self.__input_str = self.__input_str[:-1] # delete last symbol
            in_field.addstr(f"{prompt} {self.__input_str}")
        elif key == curses.KEY_UP:
            in_field.clear()
            try:
                self.__input_str = self.__command_history[-self.__history_index]
                self.__history_index +=1
            except IndexError:
                self.__history_index = 1
            in_field.addstr(f"{prompt} {self.__input_str}")
        elif key == 10:  # return key
            in_field.clear()
            in_field.addstr(f"{prompt} ")
            self.__history_index = 1
            self.__command_history.append(self.__input_str)
            out_str = self.__input_str
            self.__input_str = ""
            return out_str
        else:
            in_field.addstr(chr(key))
            self.__input_str += chr(key)
        in_field.refresh()
        # return None, if enter was not pressed
        return None

    def clear_output_window(self):
        self.__screens["output_window"].clear()
        self.__stdscr.refresh()
        self.__screens["output_window"].refresh()

    def refresh_screens(self):
        self.__stdscr.refresh()
        for _, screen in self.__screens.items():
            screen.refresh()

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
    th = TerminalHandler(
        information_content_left={"a": 3},
        information_content_center={"b": 123},
        information_content_right={"c": 42}
        )
    while True:
        inp = th.new_input("test>")
        if inp:
            if inp == "quit":
                break
            else:
                th.new_print(f">>> {inp}")
