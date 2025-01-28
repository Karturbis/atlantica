from os import system
from inspect import signature

from handler import TerminalHandler

class Client_Methods():

    def __init__(self):
        pass

    def execute_cmd(self, command, args = None):
        if not args:
            args = []
        try:
            func = getattr(self, command)
        except AttributeError:
            return f"There is no command called {command}"
        given_args_len = len(args)
        expected_args_len = len(signature(func).parameters)
        if given_args_len >= 1:
            if expected_args_len == given_args_len:
                # run method:
                try:
                    return func(*args)
                except Exception as e:
                    print(f"ERROR in Clienmethods.execute_cmd: {e}")
            elif expected_args_len == 0 and given_args_len != 0:
                return func()
            else: # wrong number of arguments were given
                return f"Command {command} takes {expected_args_len} arguments, you gave {given_args_len}."
        else:  # no args where given:
            if expected_args_len == given_args_len:
                # run method:
                try:
                    return func()
                except Exception as e:
                    return f"ERROR in Clienmethods.excute_cmd: {e}"
            else: # wrong number of arguments were given
                return f"Command {command} takes {expected_args_len} arguments, you gave {given_args_len}."

    def user_input_get_command(self, prompt="input$>"):
        user_in = input(f"{prompt} ").split(" ")
        if len(user_in) > 1:
            return user_in[0], user_in[1:]
        # else:
        return user_in[0], []

    def func1(self):
        print("func!1")

    def new_print(self, data):
        system("clear")
        print(data)

    def clear(self):
        TerminalHandler.clear()