"""Module, to have stats at the top of the terminal window."""

import curses
import threading

class TerminalHandler:
    """Handles user input and output to the
    screen."""

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
        self._output_window = curses.newwin(row_num-2, col_num, 1, 0)
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
        with self._print_lock:
            self._terminal_content.append(content)
            self._output_window.clear()
            # the 2 accounts for the space occupied by the
            # input field and the seperator:
            out_window_free_space = self._row_num -(2 + len(self._terminal_content))
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
        pass

    def clear_screen(self) -> None:
        pass


# tests:

if __name__ == "__main__":
    th = TerminalHandler()
    while True:
        pass