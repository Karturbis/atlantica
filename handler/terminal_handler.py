"""Divides the terminal into two parts, one for input and one for output.
Provides methods, to interact with the splitted screen."""

import curses
import threading

class TerminalHandler:
    """Handles user input and output to the
    screen.
    IMPORTANT: Always use quit_terminal_handler(),
    if you quit the terminal handler.
    DO NOT just kill it! Otherwise the shell state
    of the calling shell will be messed up."""

    def __init__(self):
        self._prompt: str = "$>"
        self._terminal_content: list = []
        # initialise threading Locks
        self._print_lock = threading.Lock()
        # init curses:
        self._stdscr = curses.initscr()
        self._stdscr.clear()
        # get terminal dimensions:
        row_num, col_num = self._stdscr.getmaxyx()
        self._row_num = row_num  # needed for new print
        self._output_window = curses.newwin(row_num-2, col_num, 0, 0)
        self._seperator_line = curses.newwin(1, col_num, row_num-2, 0)
        self._input_field = curses.newwin(1, col_num, row_num-1, 0)
        # clear the screens:
        self._output_window.clear()
        self._input_field.clear()
        # fill the seperator line with symbols:
        self._seperator_line.addstr("=" * (col_num-1))
        # refresh the screens, so the changes take effect:
        self._output_window.refresh()
        self._seperator_line.refresh()
        self._input_field.refresh()

    def new_print(self, content: str) -> None:
        """Shifts every line of the output scree
        one up and adds the given content at the
        bottom"""
        # make sure content is a string:
        content = str(content)
        with self._print_lock:
            self._terminal_content.append(content)
            self._output_window.clear()
            height_avail = self._output_window.getmaxyx()[0]
            out_window_free_space = height_avail - len(self._terminal_content)
            # delete the oldest prints, if new prints would not
            # fit on the screen otherwise:
            while out_window_free_space < 0:
                self._terminal_content.pop(0)
                out_window_free_space +=1
            for index, output in enumerate(self._terminal_content):
                if not index:  # first element does not need leading \n
                    self._output_window.addstr(output)
                else:
                    self._output_window.addstr(f"\n{output}")
            self._output_window.refresh()

    def new_input(self, prompt: str) -> str:
        """Blocking method, which returns the input typed
        by the user. Takes @prompt as an argument. This is the
        string, which will be displayed as the prompt."""
        input_str: str = ""
        prompt = f"{prompt} "  # add one space to the end of the prompt
        inputing = True
        in_field = self._input_field
        in_field.addstr(prompt)
        while inputing:
            # get the keyboard input:
            key = in_field.getch()
            # check for special keyboard input:
            if key == 10:  # the enter key
                in_field.clear()
                in_field.refresh()
                inputing = False
            elif key == 127:  # backspace
                in_field.clear()
                input_str = input_str[:-1]  # delete the last character
                in_field.addstr(f"{prompt}{input_str}")
            else:  # the inputed character is appended to the input string
                input_str = f"{input_str}{chr(key)}"
        return input_str

    def quit_terminal_handler(self):
        """Quits the curses window, so the
        shell environment is not messed up"""
        curses.endwin()



    def clear_screen(self) -> None:
        """Clears the output screen"""
        self._terminal_content = []
        self._output_window.clear()
        self._output_window.refresh()


# tests:

if __name__ == "__main__":
    th = TerminalHandler()
    string = ""
    while string != "quit":
        string = th.new_input("test$>")
        th.new_print(string)
