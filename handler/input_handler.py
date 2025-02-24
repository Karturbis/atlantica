from handler import TerminalHandlerOld

class InputHandler:
    """The InputHandler is in charge
    of taking input from the user and
    calling the right functions associated
    with the input."""

    def __init__(self, main_method=None, commands_avail: dict = None) -> None:
        self.main = main_method
        self.__commands_std: dict = {
            "go": ["main", "move"],
            "rest": ["main", "rest"],
            "take": ["main", "take"],
            "drop": ["main", "drop"],
            "eat": ["main", "eat"],
            "menu": ["main", "menu"],
            "inventory": ["main", "print_inventory"],
            "equip": ["main", "equip"],
            "unequip": ["main", "unequip"],
            "help": ["main", "print_help"],
            "inspect": ["main", "inspect"],
            "quit": ["main", "quit_game"],
            "clear": ["TerminalHandler", "clear"],
        }
        if commands_avail is None:
            self.__commands_avail = self.__commands_std
        else:
            self.__commands_avail = commands_avail

    def input_loop(self) -> None:
        """Waits for user input, when user
        input is coming, it executes the
        correlating command. Error checking
        for validity of the command"""
        inputing = True
        while inputing:
            try:
                commands_input = TerminalHandlerOld.new_input("> ").lower().split(" ")
                if commands_input == [""]:
                    continue
                command_found: bool = False
                # outputs the number of parameters the inputed method takes:
                if len(commands_input) > 1:
                    for key, func_list in self.__commands_avail.items():
                        if key.startswith(commands_input[0]):
                            command_found = True
                            if func_list[0] == "main":
                                func = getattr(self.main, func_list[1])
                            elif func_list[0] == "TerminalHandler":
                                func = getattr(TerminalHandlerOld, func_list[1])
                            func(commands_input[1:])
                elif len(commands_input) == 1:
                    for key, func_list in self.__commands_avail.items():
                        if key.startswith(commands_input[0]):
                            command_found = True
                            if func_list[0] == "main":
                                func = getattr(self.main, func_list[1])
                            elif func_list[0] == "TerminalHandler":
                                func = getattr(TerminalHandlerOld, func_list[1])
                            func()
                if not command_found:
                    TerminalHandlerOld.new_print("Please enter a valid command, type 'help' for help.")

            except RuntimeError:
                break

    def get_commands_avail(self) -> dict:
        """Returns the commands, which
        are available at the moment."""
        return self.__commands_avail

    def add_commands(self, commands: dict) -> None:
        """Add a command to the combat commands list."""
        for key, value in commands.items():
            self.__commands_avail[key] = value

    def remove_commands(self, commands: dict=None, remove_all=False) -> None:
        """Remove a command from the combat commands list."""
        if remove_all:
            self.__commands_avail = {
                "help": ["main", "print_help"],
                "quit": ["main", "quit_game"],
                "clear": ["TerminalHandler", "clear"],
            }
        else:
            for key in commands:
                self.__commands_avail.pop(key)

    def reset_commands(self) -> None:
        """Reset the commands to standard."""
        self.__commands_avail = self.__commands_std
